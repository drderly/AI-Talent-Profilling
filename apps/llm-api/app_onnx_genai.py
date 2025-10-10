from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Literal, AsyncGenerator, Optional
import os, time, json, asyncio
from dotenv import load_dotenv
import onnxruntime_genai as og

load_dotenv()

# Environment configuration
MODEL_DIR = os.getenv("GENAI_MODEL_DIR", r"C:\Users\user\Documents\GitHub\AI-Talent-Profilling\models\onnx\Phi-3-mini-4k-instruct-onnx\cpu-int4-rtn-block-32-acc-level-4")

# Load model at startup
print(f"Loading model from: {MODEL_DIR}")
model = og.Model(MODEL_DIR)
tokenizer = og.Tokenizer(model)
print("Model loaded successfully!")

app = FastAPI(title="ONNX GenAI API", version="1.0")

# Schemas
class Message(BaseModel):
    """Chat message with role and content"""
    role: Literal["system", "user", "assistant"] = Field(
        ..., 
        description="Role of the message sender",
        example="user"
    )
    content: str = Field(
        ..., 
        description="Content of the message",
        example="Hello, how are you?"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "What is the capital of France?"
            }
        }

class ChatRequest(BaseModel):
    """Request body for chat completion"""
    model: str = Field(
        default="onnx-genai",
        description="Model identifier for ONNX GenAI",
        example="onnx-genai"
    )
    messages: List[Message] = Field(
        ...,
        description="List of messages in the conversation",
        min_length=1
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0.0 to 2.0). Higher values make output more random.",
        example=0.7
    )
    max_tokens: int | None = Field(
        default=4096,
        ge=1,
        description="Maximum number of tokens to generate. None means no limit.",
        example=4096
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "onnx-genai",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "temperature": 0.7,
                "max_tokens": 256
            }
        }

class PerformanceMetrics(BaseModel):
    """Performance metrics for LLM inference"""
    ttft: Optional[float] = Field(
        None,
        description="Time to First Token in seconds - measures responsiveness",
        example=0.234
    )
    total_latency: float = Field(
        ...,
        description="End-to-end latency in seconds",
        example=2.456
    )
    tokens_per_second: Optional[float] = Field(
        None,
        description="Overall tokens generated per second (input + output / total time)",
        example=45.2
    )
    output_tokens_per_second: Optional[float] = Field(
        None,
        description="Output tokens generated per second (output / generation time)",
        example=52.8
    )
    input_tokens: Optional[int] = Field(
        None,
        description="Number of tokens in the input prompt",
        example=156
    )
    output_tokens: Optional[int] = Field(
        None,
        description="Number of tokens in the generated output",
        example=89
    )
    tpot: Optional[float] = Field(
        None,
        description="Time Per Output Token in seconds - average time between tokens",
        example=0.019
    )
    model: str = Field(
        ...,
        description="Model used for generation",
        example="onnx-genai"
    )

class ChatResponse(BaseModel):
    """Response from non-streaming chat endpoint"""
    content: str = Field(
        ...,
        description="Generated response content",
        example="The capital of France is Paris."
    )
    metrics: PerformanceMetrics = Field(
        ...,
        description="Performance metrics for this generation"
    )

# Helper function
def build_prompt(messages: List[Message]) -> str:
    sys_prompt = "\n".join([m.content for m in messages if m.role == "system"])
    conv = "\n".join([f"{m.role.upper()}: {m.content}" for m in messages if m.role != "system"])
    return (sys_prompt + "\n" + conv + "\nASSISTANT:").strip()

# Endpoints
@app.get("/healthz")
def healthz():
    return {"status": "ok", "model_dir": MODEL_DIR}

@app.post("/v1/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Start timing
    start_time = time.time()
    
    # Build prompt
    prompt = build_prompt(req.messages)
    
    # Tokenize
    input_tokens = tokenizer.encode(prompt)
    input_token_count = len(input_tokens)
    
    # Set search options
    params = og.GeneratorParams(model)
    max_length = req.max_tokens if req.max_tokens else 4096
    params.set_search_options(max_length=max_length, temperature=req.temperature)
    
    # Create generator and add input tokens
    generator = og.Generator(model, params)
    generator.append_tokens(input_tokens)
    
    # Generate
    while not generator.is_done():
        generator.generate_next_token()
    
    # Get output sequence
    output_seq = generator.get_sequence(0)
    
    # Decode full sequence
    output_text = tokenizer.decode(output_seq)
    
    # Remove prompt from output
    if output_text.startswith(prompt):
        content = output_text[len(prompt):].strip()
    else:
        content = output_text.strip()
    
    # Calculate metrics
    end_time = time.time()
    total_latency = end_time - start_time
    output_token_count = len(output_seq) - input_token_count
    
    # Calculate performance metrics
    tokens_per_second = None
    output_tokens_per_second = None
    tpot = None
    
    if total_latency > 0:
        total_tokens = input_token_count + output_token_count
        if total_tokens > 0:
            tokens_per_second = total_tokens / total_latency
        
        if output_token_count > 0:
            output_tokens_per_second = output_token_count / total_latency
            tpot = total_latency / output_token_count
    
    metrics = PerformanceMetrics(
        ttft=None,
        total_latency=round(total_latency, 4),
        tokens_per_second=round(tokens_per_second, 2) if tokens_per_second else None,
        output_tokens_per_second=round(output_tokens_per_second, 2) if output_tokens_per_second else None,
        input_tokens=input_token_count,
        output_tokens=output_token_count,
        tpot=round(tpot, 4) if tpot else None,
        model=req.model
    )
    
    return ChatResponse(content=content, metrics=metrics)

@app.post("/v1/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    Generate a chat completion with real-time token-by-token streaming.
    Uses Server-Sent Events (SSE) format.
    """
    prompt = build_prompt(req.messages)
    
    async def event_gen() -> AsyncGenerator[bytes, None]:
        # Track metrics
        start_time = time.time()
        ttft = None
        first_token = True
        token_count = 0
        
        # Tokenize input
        input_tokens = tokenizer.encode(prompt)
        input_token_count = len(input_tokens)
        
        # Set search options
        params = og.GeneratorParams(model)
        max_length = req.max_tokens if req.max_tokens else 4096
        params.set_search_options(max_length=max_length, temperature=req.temperature)
        
        # Create generator
        generator = og.Generator(model, params)
        generator.append_tokens(input_tokens)
        
        # Stream tokens
        while not generator.is_done():
            generator.generate_next_token()
            
            # Get the new token
            new_token_id = generator.get_next_tokens()[0]
            token_text = tokenizer.decode([new_token_id])
            
            # Record TTFT on first token
            if first_token:
                ttft = time.time() - start_time
                first_token = False
            
            token_count += 1
            
            # Send token via SSE
            chunk = json.dumps({"token": token_text}, ensure_ascii=False)
            yield f"data: {chunk}\n\n".encode("utf-8")
            
            # Small async sleep to allow event loop processing
            await asyncio.sleep(0)
        
        # Calculate final metrics
        end_time = time.time()
        total_latency = end_time - start_time
        output_token_count = token_count
        
        # Performance metrics
        tokens_per_second = None
        output_tokens_per_second = None
        tpot = None
        
        if total_latency > 0:
            total_tokens = input_token_count + output_token_count
            if total_tokens > 0:
                tokens_per_second = total_tokens / total_latency
            
            if output_token_count > 0:
                generation_time = total_latency - (ttft if ttft else 0)
                if generation_time > 0:
                    output_tokens_per_second = output_token_count / generation_time
                    tpot = generation_time / output_token_count
        
        # Send final event with metrics
        final_event = {
            "done": True,
            "token": "[DONE]",
            "metrics": {
                "ttft": round(ttft, 4) if ttft else None,
                "total_latency": round(total_latency, 4),
                "tokens_per_second": round(tokens_per_second, 2) if tokens_per_second else None,
                "output_tokens_per_second": round(output_tokens_per_second, 2) if output_tokens_per_second else None,
                "input_tokens": input_token_count,
                "output_tokens": output_token_count,
                "tpot": round(tpot, 4) if tpot else None,
                "model": req.model
            }
        }
        yield f"data: {json.dumps(final_event, ensure_ascii=False)}\n\n".encode("utf-8")
    
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no"
    }
    return StreamingResponse(event_gen(), media_type="text/event-stream", headers=headers)
