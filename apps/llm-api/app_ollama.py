from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Literal, AsyncGenerator, Optional
import httpx, os, json, time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")

app = FastAPI(
    title="LLM API (Ollama)",
    version="1.1.0",
    description="""
    🤖 **LLM API Wrapper for Ollama**
    
    This API provides both streaming and non-streaming chat endpoints with Server-Sent Events (SSE) support.
    
    ## Features
    * 🚀 Non-streaming chat completions
    * ⚡ Real-time streaming with SSE
    * 🔧 Configurable temperature and max tokens
    * 💬 Support for system, user, and assistant messages
    
    ## Models
    Supports any Ollama model (e.g., mistral:7b-instruct, llama3:8b-instruct)
    """,
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
    # Disable built-in docs and redoc; we provide custom routes below
    docs_url=None,
    redoc_url=None,
    swagger_ui_parameters={"persistAuthorization": True},
)

# ---------- Static assets (local, no CDN) ----------
try:
    # Serve local static assets from apps/llm-api/static
    local_static_dir = os.path.join(os.path.dirname(__file__), "static")

    # Mount them under /static to match your example
    app.mount("/static", StaticFiles(directory=local_static_dir), name="static")

    # Paths
    _DOCS_PATH = "/docs"
    _OAUTH2_REDIRECT_PATH = app.swagger_ui_oauth2_redirect_url or f"{_DOCS_PATH}/oauth2-redirect"

    @app.get(_DOCS_PATH, include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - Swagger UI",
            oauth2_redirect_url=_OAUTH2_REDIRECT_PATH,
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
        )

    @app.get(_OAUTH2_REDIRECT_PATH, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    # Optional ReDoc route. Note: redoc.standalone.js is NOT provided by swagger_ui_bundle.
    # To use local ReDoc, place the file at your own static directory and update the path below.
    @app.get("/redoc", include_in_schema=False)
    async def redoc_html_local():
        # If you add a local redoc.standalone.js under your own static dir, update redoc_js_url accordingly.
        # Returning a minimal page that informs about missing local asset to avoid CDN fallback.
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - ReDoc",
            redoc_js_url="/static/redoc.standalone.js",  # Provide this file locally if you need ReDoc
        )
except Exception as e:
    print(f"[Docs Setup] Failed to mount local static assets: {e}")

class Message(BaseModel):
    """Chat message with role and content"""
    role: Literal["system","user","assistant"] = Field(
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
        default="smollm2:1.7b",
        description="Ollama model to use for generation",
        example="smollm2:1.7b"
    )
    messages: List[Message] = Field(
        ...,
        description="List of messages in the conversation",
        min_length=1
    )
    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0.0 to 2.0). Higher values make output more random.",
        example=0.7
    )
    max_tokens: int | None = Field(
        default=None,
        ge=1,
        description="Maximum number of tokens to generate. None means no limit.",
        example=1000
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "smollm2:1.7b",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
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
        example="smollm2:1.7b"
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

@app.get(
    "/healthz",
    tags=["Health"],
    summary="Health check endpoint",
    description="Check if the API is running and healthy",
    response_description="Returns status OK if the service is healthy"
)
def healthz():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict: Status object with "ok" value
    """
    return {"status": "ok"}

# ---------- Non-streaming (kept for compatibility) ----------
@app.post(
    "/v1/chat",
    tags=["Chat"],
    summary="Non-streaming chat completion",
    description="Generate a complete response from the LLM without streaming",
    response_model=ChatResponse,
    response_description="Complete generated response"
)
async def chat(req: ChatRequest) -> ChatResponse:
    """
    Generate a chat completion without streaming.
    
    This endpoint waits for the complete response before returning.
    Use this for simpler integrations where streaming is not needed.
    
    Args:
        req: Chat request with model, messages, and parameters
        
    Returns:
        ChatResponse: Complete generated response with performance metrics
        
    Raises:
        HTTPException: If Ollama service is unavailable or returns an error
    """
    # Start timing
    start_time = time.time()
    
    # Join messages into a single prompt (simple chat pattern)
    sys = "\n".join([m.content for m in req.messages if m.role=="system"])
    history = "\n".join([f"{m.role.upper()}: {m.content}" for m in req.messages if m.role!="system"])
    prompt = (sys + "\n" + history).strip()

    payload = {
        "model": req.model,
        "prompt": prompt,
        "options": {"temperature": req.temperature},
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
        r.raise_for_status()
        data = r.json()
    
    # Calculate metrics
    end_time = time.time()
    total_latency = end_time - start_time
    
    # Extract token counts from Ollama response
    prompt_eval_count = data.get("prompt_eval_count", 0)
    eval_count = data.get("eval_count", 0)
    
    # Calculate tokens per second metrics
    tokens_per_second = None
    output_tokens_per_second = None
    tpot = None
    
    if total_latency > 0:
        total_tokens = prompt_eval_count + eval_count
        if total_tokens > 0:
            tokens_per_second = total_tokens / total_latency
        
        if eval_count > 0:
            # Estimate generation time (excluding prompt processing)
            total_duration_s = data.get("total_duration", 0) / 1_000_000_000  # nanoseconds to seconds
            prompt_duration_s = data.get("prompt_eval_duration", 0) / 1_000_000_000
            generation_time = total_duration_s - prompt_duration_s if total_duration_s > prompt_duration_s else total_latency
            
            if generation_time > 0:
                output_tokens_per_second = eval_count / generation_time
                tpot = generation_time / eval_count
    
    # Build response with metrics
    metrics = PerformanceMetrics(
        ttft=None,  # Not available in non-streaming mode
        total_latency=round(total_latency, 4),
        tokens_per_second=round(tokens_per_second, 2) if tokens_per_second else None,
        output_tokens_per_second=round(output_tokens_per_second, 2) if output_tokens_per_second else None,
        input_tokens=prompt_eval_count if prompt_eval_count > 0 else None,
        output_tokens=eval_count if eval_count > 0 else None,
        tpot=round(tpot, 4) if tpot else None,
        model=req.model
    )
    
    return ChatResponse(
        content=data.get("response", ""),
        metrics=metrics
    )

# ---------- Streaming like ChatGPT (SSE) ----------
@app.post(
    "/v1/chat/stream",
    tags=["Chat"],
    summary="Streaming chat completion",
    description="Generate a response with real-time token streaming using Server-Sent Events (SSE)",
    response_description="Server-Sent Events stream with tokens"
)
async def chat_stream(req: ChatRequest):
    """
    Generate a chat completion with real-time streaming.
    
    This endpoint streams tokens as they are generated using Server-Sent Events (SSE).
    Each event contains a single token, and a final event includes performance metrics.
    
    **SSE Event Format:**
    ```
    data: {"token": "Hello"}
    
    data: {"token": " world"}
    
    data: {"done": true, "token": "[DONE]", "metrics": {...}}
    ```
    
    Args:
        req: Chat request with model, messages, and parameters
        
    Returns:
        StreamingResponse: SSE stream of tokens with metrics
        
    Raises:
        HTTPException: If Ollama service is unavailable or returns an error
    """

    sys = "\n".join([m.content for m in req.messages if m.role=="system"])
    history = "\n".join([f"{m.role.upper()}: {m.content}" for m in req.messages if m.role!="system"])
    prompt = (sys + "\n" + history).strip()

    payload = {
        "model": req.model,
        "prompt": prompt,
        "options": {
            "temperature": req.temperature,
            **({"num_predict": req.max_tokens} if req.max_tokens else {})
        },
        "stream": True
    }

    async def event_gen() -> AsyncGenerator[bytes, None]:
        # Track metrics
        start_time = time.time()
        ttft = None
        first_token_received = False
        token_count = 0
        prompt_eval_count = 0
        
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", f"{OLLAMA_URL}/api/generate", json=payload) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if not line:
                        continue
                    # Ollama streams JSON per line; parse and forward token
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if obj.get("done"):
                        # Calculate final metrics
                        end_time = time.time()
                        total_latency = end_time - start_time
                        
                        # Get token counts from final response
                        prompt_eval_count = obj.get("prompt_eval_count", prompt_eval_count)
                        eval_count = obj.get("eval_count", token_count)
                        
                        # Calculate performance metrics
                        tokens_per_second = None
                        output_tokens_per_second = None
                        tpot = None
                        
                        if total_latency > 0:
                            total_tokens = prompt_eval_count + eval_count
                            if total_tokens > 0:
                                tokens_per_second = total_tokens / total_latency
                            
                            if eval_count > 0:
                                generation_time = total_latency - (ttft if ttft else 0)
                                if generation_time > 0:
                                    output_tokens_per_second = eval_count / generation_time
                                    tpot = generation_time / eval_count
                        
                        # Build metrics object
                        metrics = {
                            "ttft": round(ttft, 4) if ttft else None,
                            "total_latency": round(total_latency, 4),
                            "tokens_per_second": round(tokens_per_second, 2) if tokens_per_second else None,
                            "output_tokens_per_second": round(output_tokens_per_second, 2) if output_tokens_per_second else None,
                            "input_tokens": prompt_eval_count if prompt_eval_count > 0 else None,
                            "output_tokens": eval_count if eval_count > 0 else None,
                            "tpot": round(tpot, 4) if tpot else None,
                            "model": req.model
                        }
                        
                        # Send final SSE event with metrics
                        final_event = {
                            "done": True,
                            "token": "[DONE]",
                            "metrics": metrics
                        }
                        yield f"data: {json.dumps(final_event, ensure_ascii=False)}\n\n".encode("utf-8")
                        break

                    token = obj.get("response", "")
                    if token:
                        # Record TTFT on first token
                        if not first_token_received:
                            ttft = time.time() - start_time
                            first_token_received = True
                        
                        token_count += 1
                        
                        # SSE frame; keep it tiny to flush quickly
                        chunk = json.dumps({"token": token}, ensure_ascii=False)
                        yield f"data: {chunk}\n\n".encode("utf-8")

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no"  # for some proxies; disables buffering
    }
    return StreamingResponse(event_gen(), media_type="text/event-stream", headers=headers)
