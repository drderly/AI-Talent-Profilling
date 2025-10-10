# Quick Reference - LLM API Backends

## 🎯 Which Backend Should I Use?

```
┌─────────────────────────────────────────────────────────────┐
│ Need the easiest setup?                                     │
│ → Use Ollama (app_ollama.py on port 8000)                  │
│   Just run: ollama pull phi && uvicorn app_ollama:app      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Need production-grade performance?                          │
│ → Use ONNX GenAI (app_onnx_genai.py on port 8002)         │
│   Best streaming, lowest latency, minimal deps             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Need HuggingFace model compatibility?                       │
│ → Use ONNX (app_onnx.py on port 8001)                     │
│   Full transformers support, any HF model                  │
└─────────────────────────────────────────────────────────────┘
```

## ⚡ Quick Start Commands

### Ollama Backend (Easiest)

```bash
# 1. Install Ollama (if not installed)
# Download from: https://ollama.ai/

# 2. Pull a model
ollama pull phi

# 3. Update .env
OLLAMA_URL=http://127.0.0.1:11434

# 4. Start API
uvicorn app_ollama:app --port 8000 --reload

# 5. Test
curl -X POST http://127.0.0.1:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hi!"}]}'
```

### ONNX GenAI Backend (Recommended for Production)

```bash
# 1. Install dependencies
pip install onnxruntime-genai

# 2. Download pre-exported model
huggingface-cli download microsoft/Phi-3-mini-4k-instruct-onnx --local-dir ./genai-model

# 3. Update .env
GENAI_MODEL_DIR=./genai-model
GENAI_DEVICE=cpu

# 4. Start API
uvicorn app_onnx_genai:app --port 8002 --reload

# 5. Test
curl -X POST http://127.0.0.1:8002/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hi!"}]}'
```

### ONNX Backend (HuggingFace Compatibility)

```bash
# 1. Install dependencies
pip install transformers optimum[onnxruntime] torch

# 2. Export a model
optimum-cli export onnx -m microsoft/phi-2 ./onnx-model

# 3. Update .env
ONNX_MODEL_DIR=./onnx-model
ONNX_PROVIDER=CPUExecutionProvider

# 4. Start API
uvicorn app_onnx:app --port 8001 --reload

# 5. Test
curl -X POST http://127.0.0.1:8001/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hi!"}]}'
```

## 📊 Performance Comparison

| Metric | Ollama | ONNX | ONNX GenAI |
|--------|--------|------|------------|
| **TTFT** (Phi-2, CPU) | 0.3-0.5s | 0.5-0.8s | 0.2-0.4s |
| **Tokens/sec** | 50-70 | 30-50 | 40-60 |
| **Memory** | Low | High | Low |
| **Streaming** | ✅ True | ⚠️ Simulated | ✅ True |
| **Setup Time** | 1 min | 5 min | 3 min |

## 🔌 API Endpoints (All Backends)

### Health Check
```bash
GET /healthz
```

### Non-Streaming Chat
```bash
POST /v1/chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "What is AI?"}
  ],
  "temperature": 0.7,
  "max_tokens": 100
}
```

### Streaming Chat
```bash
POST /v1/chat/stream
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "What is AI?"}
  ],
  "temperature": 0.7,
  "max_tokens": 100
}
```

## 🐍 Python Client Example

```python
import requests

# Choose your backend port
BASE_URL = "http://127.0.0.1:8002"  # ONNX GenAI
# BASE_URL = "http://127.0.0.1:8000"  # Ollama
# BASE_URL = "http://127.0.0.1:8001"  # ONNX

# Non-streaming
response = requests.post(
    f"{BASE_URL}/v1/chat",
    json={
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain quantum computing in simple terms"}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }
)

result = response.json()
print(result["content"])
print(f"Latency: {result['metrics']['total_latency']}s")
print(f"Tokens/sec: {result['metrics']['output_tokens_per_second']}")

# Streaming
response = requests.post(
    f"{BASE_URL}/v1/chat/stream",
    json={
        "messages": [
            {"role": "user", "content": "Write a haiku about programming"}
        ],
        "temperature": 0.9
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            import json
            data = json.loads(line_str[6:])
            if data.get('done'):
                print(f"\n\nMetrics: {data['metrics']}")
                break
            print(data.get('token', ''), end='', flush=True)
```

## 🎛️ Environment Variables Cheat Sheet

```env
# Server (all backends)
HOST=127.0.0.1
PORT=8000
RELOAD=true
WORKERS=2

# Ollama Backend
OLLAMA_URL=http://127.0.0.1:11434

# ONNX GenAI Backend (recommended)
GENAI_MODEL_DIR=./genai-model
GENAI_DEVICE=cpu              # cpu, cuda, directml
GENAI_MAX_LENGTH=2048

# ONNX Backend (legacy)
ONNX_MODEL_DIR=./onnx-model
ONNX_PROVIDER=CPUExecutionProvider  # or CUDAExecutionProvider
ONNX_MAX_NEW_TOKENS=512
```

## 🚀 GPU Acceleration

### CUDA (NVIDIA)

```bash
# Ollama: Automatically uses GPU if available

# ONNX GenAI: Install GPU version
pip install onnxruntime-genai-cuda
# Set in .env:
GENAI_DEVICE=cuda

# ONNX: Install GPU version
pip install onnxruntime-gpu
# Set in .env:
ONNX_PROVIDER=CUDAExecutionProvider
```

### DirectML (Windows AMD/Intel/NVIDIA)

```bash
# ONNX GenAI only
pip install onnxruntime-genai-directml
# Set in .env:
GENAI_DEVICE=directml
```

## 📁 Project Structure

```
llm-api/
├── app_ollama.py          # Ollama backend (port 8000)
├── app_onnx_genai.py      # ONNX GenAI backend (port 8002) ⭐
├── app_onnx.py            # ONNX backend (port 8001)
├── main.py                # Server launcher
├── .env                   # Configuration (copy from .env.example)
├── .env.example           # Example configuration
├── requirements.txt       # Python dependencies
├── README.md              # Full documentation
├── ONNX_GENAI_GUIDE.md    # ONNX GenAI setup guide
├── METRICS.md             # Performance metrics guide
└── QUICK_REFERENCE.md     # This file
```

## 🔧 Troubleshooting

### "Model directory not found"
```bash
# Make sure you've downloaded/exported the model
# For ONNX GenAI:
huggingface-cli download microsoft/Phi-3-mini-4k-instruct-onnx --local-dir ./genai-model

# For ONNX:
optimum-cli export onnx -m microsoft/phi-2 ./onnx-model
```

### "onnxruntime-genai not installed"
```bash
pip install onnxruntime-genai
```

### "Ollama connection refused"
```bash
# Start Ollama service
ollama serve
```

### Slow performance
1. Use quantized models (int4 for ONNX GenAI)
2. Enable GPU acceleration
3. Reduce max_tokens
4. Use streaming for better perceived performance

## 📚 Additional Resources

- **Full Setup**: See [README.md](README.md)
- **ONNX GenAI Guide**: See [ONNX_GENAI_GUIDE.md](ONNX_GENAI_GUIDE.md)
- **Metrics Explanation**: See [METRICS.md](METRICS.md)
- **Swagger UI**: http://localhost:{PORT}/docs

## 🆘 Support

- For ONNX GenAI issues: https://github.com/microsoft/onnxruntime-genai
- For Ollama issues: https://github.com/ollama/ollama
- For API issues: Open an issue in this repository
