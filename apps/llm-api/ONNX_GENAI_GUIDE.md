# ONNX Runtime GenAI Backend Guide

This guide explains how to set up and use the ONNX Runtime GenAI backend (`app_onnx_genai.py`) for high-performance local LLM inference.

## Overview

The ONNX GenAI backend provides:

- ✅ **True token-by-token streaming** (not simulated)
- ✅ **Native KV cache** for fast incremental decoding
- ✅ **Multiple hardware backends**: CPU, CUDA (NVIDIA), DirectML (Windows AMD/Intel)
- ✅ **Lower latency** than traditional transformers pipeline
- ✅ **Smaller dependencies** (no PyTorch required at runtime)
- ✅ **Production-ready** with battle-tested ONNX Runtime

## Installation

### 1. Install Dependencies

```bash
pip install onnxruntime-genai
```

For GPU support:
```bash
# CUDA (NVIDIA)
pip install onnxruntime-genai-cuda

# DirectML (Windows AMD/Intel/NVIDIA)
pip install onnxruntime-genai-directml
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update:

```env
GENAI_MODEL_DIR=./genai-model
GENAI_DEVICE=cpu          # or cuda, directml
GENAI_MAX_LENGTH=2048
```

## Exporting Models

ONNX GenAI requires models in a specific format. You have several options:

### Option 1: Use Pre-exported Models (Easiest)

Microsoft provides pre-exported models compatible with ONNX GenAI:

**Download from Hugging Face:**
```bash
# Example: Phi-3 Mini
huggingface-cli download microsoft/Phi-3-mini-4k-instruct-onnx --local-dir ./genai-model

# Example: Phi-2
huggingface-cli download microsoft/phi-2-onnx --local-dir ./genai-model
```

**Available pre-exported models:**
- `microsoft/Phi-3-mini-4k-instruct-onnx`
- `microsoft/Phi-3-mini-128k-instruct-onnx`
- `microsoft/Phi-2-onnx`
- Check [Microsoft's ONNX model collection](https://huggingface.co/models?other=onnx) for more

### Option 2: Export Using Model Builder (Python API)

```python
import onnxruntime_genai as og

# Export a model from Hugging Face
model_name = "microsoft/phi-2"
output_dir = "./genai-model"

# Create model builder
builder = og.ModelBuilder()

# Export (this downloads and converts the model)
builder.create_model(
    model_name,
    output_dir,
    precision="fp32",          # or "fp16", "int4"
    execution_provider="cpu"   # or "cuda", "directml"
)

print(f"Model exported to {output_dir}")
```

### Option 3: Export Using Command Line (Builder Tool)

Install the builder:
```bash
pip install onnxruntime-genai[builder]
```

Export a model:
```bash
# Basic export
python -m onnxruntime_genai.models.builder \
    -m microsoft/phi-2 \
    -o ./genai-model \
    -p fp32 \
    -e cpu

# With quantization (int4 for smaller size, faster inference)
python -m onnxruntime_genai.models.builder \
    -m microsoft/phi-2 \
    -o ./genai-model \
    -p int4 \
    -e cpu
```

**Parameters:**
- `-m`: Hugging Face model name or local path
- `-o`: Output directory
- `-p`: Precision (`fp32`, `fp16`, `int4`, `int8`)
- `-e`: Execution provider (`cpu`, `cuda`, `directml`)

### Option 4: Export Using Olive (Advanced)

For maximum control and optimization, use [Olive](https://github.com/microsoft/Olive):

```bash
pip install olive-ai[onnxruntime]
```

Create `olive_config.json`:
```json
{
    "input_model": {
        "type": "PyTorchModel",
        "config": {
            "hf_config": {
                "model_name": "microsoft/phi-2"
            }
        }
    },
    "systems": {
        "local_system": {
            "type": "LocalSystem",
            "config": {
                "accelerators": ["cpu"]
            }
        }
    },
    "evaluators": {
        "common_evaluator": {
            "metrics": [
                {
                    "name": "latency",
                    "type": "latency"
                }
            ]
        }
    },
    "passes": {
        "convert": {
            "type": "OnnxConversion"
        },
        "optimize": {
            "type": "OrtTransformersOptimization"
        }
    },
    "output_dir": "./genai-model"
}
```

Run Olive:
```bash
olive run --config olive_config.json
```

## Model Directory Structure

A valid GENAI model directory must contain:

```
genai-model/
├── genai_config.json       # Generation configuration
├── model.onnx              # Main model (or model.onnx.data + model.onnx)
├── model.onnx.data         # Model weights (for large models)
├── tokenizer.json          # Tokenizer
├── tokenizer_config.json   # Tokenizer config
└── special_tokens_map.json # Special tokens
```

## Running the API

### Development Mode (Hot Reload)

```bash
uvicorn app_onnx_genai:app --host 127.0.0.1 --port 8002 --reload
```

### Production Mode

```bash
uvicorn app_onnx_genai:app --host 127.0.0.1 --port 8002 --workers 2
```

Or use the main.py approach by modifying it:

```python
# main_genai.py
import uvicorn
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "8002"))
    RELOAD = os.getenv("RELOAD", "true").lower() == "true"
    WORKERS = int(os.getenv("WORKERS", "2"))
    
    workers = 1 if RELOAD else WORKERS
    
    uvicorn.run(
        "app_onnx_genai:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        workers=workers,
        log_level="info"
    )
```

## API Endpoints

### Health Check

```bash
GET http://127.0.0.1:8002/healthz
```

Response:
```json
{
  "status": "ok",
  "backend": "onnx-genai",
  "device": "cpu",
  "model_dir": "./genai-model"
}
```

### Non-Streaming Chat

```bash
POST http://127.0.0.1:8002/v1/chat
```

Request:
```json
{
  "model": "onnx-genai",
  "messages": [
    {"role": "user", "content": "What is the capital of France?"}
  ],
  "temperature": 0.7,
  "max_tokens": 100,
  "top_p": 0.9,
  "top_k": 50
}
```

Response:
```json
{
  "content": "The capital of France is Paris.",
  "metrics": {
    "ttft": null,
    "total_latency": 0.8234,
    "tokens_per_second": 48.5,
    "output_tokens_per_second": 55.2,
    "input_tokens": 12,
    "output_tokens": 8,
    "tpot": 0.0181,
    "model": "onnx-genai"
  }
}
```

### Streaming Chat

```bash
POST http://127.0.0.1:8002/v1/chat/stream
```

Response (SSE):
```
data: {"token":"The"}

data: {"token":" capital"}

data: {"token":" of"}

data: {"token":" France"}

data: {"token":" is"}

data: {"token":" Paris"}

data: {"token":"."}

data: {"done": true, "token": "[DONE]", "metrics": {...}}
```

## Performance Comparison

| Backend | TTFT | Streaming | Memory | GPU Support |
|---------|------|-----------|--------|-------------|
| **Ollama** | Good | ✅ Native | High | CUDA |
| **ONNX (transformers)** | Fair | ⚠️ Simulated | High | CPU/CUDA |
| **ONNX GenAI** | Excellent | ✅ Native | Low | CPU/CUDA/DirectML |

### Typical Performance (Phi-2, CPU)

- **TTFT**: 0.2-0.4s
- **Tokens/sec**: 40-60
- **TPOT**: 0.015-0.025s
- **Memory**: ~2-3GB

## Hardware Acceleration

### CPU (Default)

```env
GENAI_DEVICE=cpu
```

Works on any system, good for development and light workloads.

### CUDA (NVIDIA GPU)

```env
GENAI_DEVICE=cuda
```

Requirements:
- NVIDIA GPU (Compute Capability 7.0+)
- CUDA 11.8+ or 12.x
- Install: `pip install onnxruntime-genai-cuda`

**5-10x faster than CPU** for most models.

### DirectML (Windows GPU)

```env
GENAI_DEVICE=directml
```

Requirements:
- Windows 10/11
- Any DirectX 12 compatible GPU (AMD, Intel, NVIDIA)
- Install: `pip install onnxruntime-genai-directml`

**2-4x faster than CPU**, works with non-NVIDIA GPUs.

## Quantization for Better Performance

Quantization reduces model size and increases speed:

| Precision | Size | Speed | Quality |
|-----------|------|-------|---------|
| **fp32** | 100% | 1x | Best |
| **fp16** | 50% | 1.5-2x | Excellent |
| **int8** | 25% | 2-3x | Very Good |
| **int4** | 12.5% | 3-5x | Good |

Export with quantization:
```bash
python -m onnxruntime_genai.models.builder \
    -m microsoft/phi-2 \
    -o ./genai-model-int4 \
    -p int4 \
    -e cpu
```

## Troubleshooting

### "Model directory not found"

Ensure `GENAI_MODEL_DIR` points to a valid directory with:
- `genai_config.json`
- `model.onnx` (or `model.onnx` + `model.onnx.data`)
- Tokenizer files

### "onnxruntime-genai not installed"

Install the package:
```bash
pip install onnxruntime-genai
```

For GPU:
```bash
pip install onnxruntime-genai-cuda  # NVIDIA
# or
pip install onnxruntime-genai-directml  # Windows AMD/Intel
```

### Low performance on CPU

1. Use quantized models (int4 or int8)
2. Reduce `max_tokens`
3. Use smaller models (Phi-2 instead of Llama-7B)
4. Enable hardware acceleration if available

### Out of memory

1. Use quantized models
2. Reduce `GENAI_MAX_LENGTH`
3. Use a smaller model
4. Close other applications

## Supported Models

ONNX GenAI works best with:

- **Phi series**: Phi-2, Phi-3
- **Llama series**: Llama-2, Llama-3, CodeLlama
- **Mistral**: Mistral-7B, Mixtral
- **Gemma**: Gemma-2B, Gemma-7B
- Any causal LM with compatible architecture

## Best Practices

1. **Development**: Use CPU with fp32 for fastest iteration
2. **Production CPU**: Use int4 quantization for best speed/quality tradeoff
3. **Production GPU**: Use fp16 for best quality, int4 for maximum throughput
4. **Streaming**: Always use streaming for better UX (enables TTFT measurement)
5. **Metrics**: Monitor TTFT and TPOT to ensure smooth user experience

## Integration Example

```python
import requests

# Non-streaming
response = requests.post(
    "http://127.0.0.1:8002/v1/chat",
    json={
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain ONNX in simple terms"}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }
)

result = response.json()
print(result["content"])
print(f"Latency: {result['metrics']['total_latency']}s")
print(f"Tokens/sec: {result['metrics']['output_tokens_per_second']}")
```

## References

- [ONNX Runtime GenAI Documentation](https://onnxruntime.ai/docs/genai/)
- [ONNX Runtime GenAI GitHub](https://github.com/microsoft/onnxruntime-genai)
- [Pre-exported Models](https://huggingface.co/models?other=onnx)
- [Olive Optimization Tool](https://github.com/microsoft/Olive)

## Contributing

Found a way to improve ONNX GenAI performance? Contributions welcome!
