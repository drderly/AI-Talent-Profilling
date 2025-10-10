from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Literal, AsyncGenerator, Optional
import os, time, json, asyncio
from dotenv import load_dotenv

# Optional heavy imports are loaded lazily to speed up app import time
_tokenizer = None
_model = None

load_dotenv()

# Environment configuration
ONNX_MODEL_DIR = os.getenv("ONNX_MODEL_DIR", "./onnx-model")  # Path to ONNX-exported model (Optimum format)
ONNX_PROVIDER = os.getenv("ONNX_PROVIDER", "CPUExecutionProvider")  # Or "CUDAExecutionProvider"
DEFAULT_MAX_NEW_TOKENS = int(os.getenv("ONNX_MAX_NEW_TOKENS", "512"))

app = FastAPI(
    title="LLM API (ONNX)",
    version="1.0.0",
    description="""
    ⚙️ ONNX Runtime backend for the LLM API.

    This service mirrors the Ollama endpoints but runs an ONNX-exported causal LM
    (Optimum ONNX format) via ONNX Runtime. Use this when you want a local, vendor-neutral backend.

    Notes:
    - Non-streaming returns full text plus metrics.
    - Streaming is simulated (chunked response) unless your model export supports efficient token-by-token decoding.
    - Provide a local path in `ONNX_MODEL_DIR` that contains the Optimum ONNX model and tokenizer files.
    """,
)

# ---------- Schemas (mirrors app_ollama.py) ----------
class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    model: str = Field(
        default="onnx-local",
        description="Identifier for selection; not used by ONNX runtime",
        example="onnx-local"
    )
    messages: List[Message]
    temperature: float = 0.2
    max_tokens: Optional[int] = None

class PerformanceMetrics(BaseModel):
    ttft: Optional[float] = None
    total_latency: float
    tokens_per_second: Optional[float] = None
    output_tokens_per_second: Optional[float] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    tpot: Optional[float] = None
    model: str

class ChatResponse(BaseModel):
    content: str
    metrics: PerformanceMetrics

# ---------- Lazy model loader ----------

def _load_model():
    global _tokenizer, _model
    if _tokenizer is not None and _model is not None:
        return _tokenizer, _model

    try:
        from transformers import AutoTokenizer
        from optimum.onnxruntime import ORTModelForCausalLM
    except Exception as e:
        raise RuntimeError(
            "Missing dependencies for ONNX backend. Install: transformers, optimum[onnxruntime], onnxruntime (or onnxruntime-gpu)"
        ) from e

    if not os.path.isdir(ONNX_MODEL_DIR):
        raise RuntimeError(
            f"ONNX model directory not found: {ONNX_MODEL_DIR}. Set ONNX_MODEL_DIR to a valid Optimum ONNX model path."
        )

    _tokenizer = AutoTokenizer.from_pretrained(ONNX_MODEL_DIR, use_fast=True)
    _model = ORTModelForCausalLM.from_pretrained(ONNX_MODEL_DIR, provider=ONNX_PROVIDER)
    return _tokenizer, _model

# ---------- Utilities ----------

def build_prompt(messages: List[Message]) -> str:
    sys = "\n".join([m.content for m in messages if m.role == "system"])
    history = "\n".join([f"{m.role.upper()}: {m.content}" for m in messages if m.role != "system"])
    return (sys + "\n" + history).strip()

# ---------- Endpoints ----------

@app.get("/healthz")
def healthz():
    return {"status": "ok", "backend": "onnx", "model_dir": ONNX_MODEL_DIR}

@app.post("/v1/chat")
async def chat(req: ChatRequest) -> ChatResponse:
    tokenizer, model = _load_model()

    start_time = time.time()
    prompt = build_prompt(req.messages)

    # Tokenize
    inputs = tokenizer(prompt, return_tensors="pt")

    # Determine max_new_tokens
    max_new = req.max_tokens or DEFAULT_MAX_NEW_TOKENS

    # Generate (non-streaming)
    outputs = model.generate(
        **inputs,
        do_sample=True if req.temperature and req.temperature > 0 else False,
        temperature=max(req.temperature, 1e-6),
        max_new_tokens=max_new,
        use_cache=True,
        pad_token_id=tokenizer.eos_token_id,
    )

    end_time = time.time()
    total_latency = end_time - start_time

    # Decode
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only the generated completion by removing the prompt prefix
    if decoded.startswith(prompt):
        content = decoded[len(prompt):].lstrip()
    else:
        content = decoded

    # Token counts
    input_ids = inputs["input_ids"][0]
    output_len = max(int(outputs.shape[1] - input_ids.shape[0]), 0)
    input_tokens = int(input_ids.shape[0])
    output_tokens = output_len

    # Throughput metrics
    tokens_per_second = None
    output_tokens_per_second = None
    tpot = None
    if total_latency > 0:
        total_tokens = input_tokens + output_tokens
        if total_tokens > 0:
            tokens_per_second = total_tokens / total_latency
        if output_tokens > 0:
            # We don't have precise TTFT; treat generation time as total latency
            output_tokens_per_second = output_tokens / total_latency
            tpot = total_latency / output_tokens

    metrics = PerformanceMetrics(
        ttft=None,
        total_latency=round(total_latency, 4),
        tokens_per_second=round(tokens_per_second, 2) if tokens_per_second else None,
        output_tokens_per_second=round(output_tokens_per_second, 2) if output_tokens_per_second else None,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        tpot=round(tpot, 4) if tpot else None,
        model=req.model or "onnx-local",
    )

    return ChatResponse(content=content, metrics=metrics)

@app.post("/v1/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    Simulated SSE streaming: generates the full text, then streams it in small chunks.
    This approximates streaming when true token-by-token ONNX decoding isn't available.
    """
    tokenizer, model = _load_model()

    prompt = build_prompt(req.messages)

    start_time = time.time()
    inputs = tokenizer(prompt, return_tensors="pt")
    max_new = req.max_tokens or DEFAULT_MAX_NEW_TOKENS

    outputs = model.generate(
        **inputs,
        do_sample=True if req.temperature and req.temperature > 0 else False,
        temperature=max(req.temperature, 1e-6),
        max_new_tokens=max_new,
        use_cache=True,
        pad_token_id=tokenizer.eos_token_id,
    )

    # Decode full result and split for simulated streaming
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if decoded.startswith(prompt):
        content = decoded[len(prompt):].lstrip()
    else:
        content = decoded

    # Prepare metrics (approximate TTFT as time to first chunk)
    first_chunk_time = None

    async def event_gen() -> AsyncGenerator[bytes, None]:
        nonlocal first_chunk_time
        # Split by words to keep it light
        words = content.split()
        emitted = 0

        for w in words:
            if emitted == 0:
                first_chunk_time = time.time()
            chunk = json.dumps({"token": (w + " ")}, ensure_ascii=False)
            yield f"data: {chunk}\n\n".encode("utf-8")
            emitted += 1
            await asyncio.sleep(0.0)  # yield control to flush

        # Finalize metrics
        end_time = time.time()
        total_latency = end_time - start_time
        ttft = (first_chunk_time - start_time) if first_chunk_time else None

        input_tokens = int(inputs["input_ids"].shape[-1])
        output_tokens = max(int(outputs.shape[1] - input_tokens), 0)

        tokens_per_second = None
        output_tokens_per_second = None
        tpot = None
        if total_latency > 0:
            total_tokens = input_tokens + output_tokens
            if total_tokens > 0:
                tokens_per_second = total_tokens / total_latency
            if output_tokens > 0:
                gen_time = total_latency - (ttft or 0)
                if gen_time > 0:
                    output_tokens_per_second = output_tokens / gen_time
                    tpot = gen_time / output_tokens

        final_event = {
            "done": True,
            "token": "[DONE]",
            "metrics": {
                "ttft": round(ttft, 4) if ttft else None,
                "total_latency": round(total_latency, 4),
                "tokens_per_second": round(tokens_per_second, 2) if tokens_per_second else None,
                "output_tokens_per_second": round(output_tokens_per_second, 2) if output_tokens_per_second else None,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "tpot": round(tpot, 4) if tpot else None,
                "model": req.model or "onnx-local",
            },
        }
        yield f"data: {json.dumps(final_event, ensure_ascii=False)}\n\n".encode("utf-8")

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(event_gen(), media_type="text/event-stream", headers=headers)
