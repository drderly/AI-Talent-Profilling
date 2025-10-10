# LLM API - Multi-Backend Inference Server

A production-ready FastAPI-based LLM inference server with **multiple backend options**: Ollama, ONNX Runtime, and ONNX Runtime GenAI. Choose the backend that best fits your deployment needs.

## Features

- ✨ **Multiple Backends**: Ollama, ONNX Runtime, ONNX GenAI
- 🚀 **True Streaming**: Real-time token-by-token streaming using Server-Sent Events (SSE)
- 📊 **Performance Metrics**: TTFT, TPS, TPOT, and comprehensive benchmarking
- 🔄 **Hot Reload**: Development mode with automatic code reloading
- ⚙️ **Environment Configuration**: Easy configuration using `.env` file
- 🔧 **Production Ready**: Multi-worker support for production deployment
- 💻 **Hardware Acceleration**: CPU, CUDA (NVIDIA), DirectML (Windows)

## Backend Comparison

| Backend | File | Streaming | Performance | Dependencies | GPU Support | Best For |
|---------|------|-----------|-------------|--------------|-------------|----------|
| **Ollama** | `app_ollama.py` | ✅ Native | Excellent | Lightweight | CUDA | Easy setup, quick start |
| **ONNX** | `app_onnx.py` | ⚠️ Simulated | Good | Heavy (PyTorch) | CPU/CUDA | HuggingFace compatibility |
| **ONNX GenAI** | `app_onnx_genai.py` | ✅ Native | Excellent | Minimal | CPU/CUDA/DirectML | **Production (recommended)** |

**Recommendation**: Use **ONNX GenAI** (`app_onnx_genai.py`) for production deployments. It offers the best combination of performance, true streaming, and minimal dependencies.

## Prerequisites

### For Ollama Backend
- Python 3.10 or higher
- [Ollama](https://ollama.ai/) installed and running locally
- A model pulled in Ollama (e.g., `ollama pull mistral:7b-instruct`)

### For ONNX GenAI Backend (Recommended)
- Python 3.10 or higher
- An ONNX-exported model (see [ONNX_GENAI_GUIDE.md](ONNX_GENAI_GUIDE.md))
- Optional: GPU with CUDA or DirectML support

## Installation

### Quick Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd apps/llm-api
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   # or
   source .venv/bin/activate    # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or use setup.py:
   ```bash
   python setup.py install
   ```

   For development mode:
   ```bash
   pip install -e .
   ```

## Configuration

All configuration is managed through the `.env` file. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

### Configuration Options

**Server Configuration** (all backends):
| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host address | `127.0.0.1` |
| `PORT` | Server port | `8000` |
| `RELOAD` | Enable hot reload (dev mode) | `true` |
| `WORKERS` | Number of worker processes | `2` |

**Ollama Backend** (`app_ollama.py`):
| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_URL` | Ollama API endpoint | `http://127.0.0.1:11434` |

**ONNX GenAI Backend** (`app_onnx_genai.py`):
| Variable | Description | Default |
|----------|-------------|---------|
| `GENAI_MODEL_DIR` | Path to ONNX GenAI model | `C:\ai\models\phi3-mini-4k-instruct` |
| `GENAI_DEVICE` | Device preference (cpu/cuda/directml) | `cpu` |
| `GENAI_MAX_LENGTH` | Max sequence length | `2048` |

**Note**: Actual device used depends on which `onnxruntime-genai` package is installed (cpu/cuda/directml version).

**Note**: Hot reload (`RELOAD=true`) automatically uses 1 worker. Multiple workers are only used when `RELOAD=false`.

## Usage

### Start the Server

#### Option 1: Ollama Backend (Port 8000)

```bash
# Development
uvicorn app_ollama:app --host 127.0.0.1 --port 8000 --reload

# Production
uvicorn app_ollama:app --host 127.0.0.1 --port 8000 --workers 2
```

#### Option 2: ONNX GenAI Backend (Port 8002) - **Recommended**

```bash
# Development
uvicorn app_onnx_genai:app --host 127.0.0.1 --port 8002 --reload

# Production
uvicorn app_onnx_genai:app --host 127.0.0.1 --port 8002 --workers 2
```

**For detailed ONNX GenAI setup**: See [ONNX_GENAI_GUIDE.md](ONNX_GENAI_GUIDE.md)

#### Option 3: ONNX Backend (Port 8001)

```bash
# Development
uvicorn app_onnx:app --host 127.0.0.1 --port 8001 --reload

# Production
uvicorn app_onnx:app --host 127.0.0.1 --port 8001 --workers 2
```

### Interactive API Documentation

Each backend has its own Swagger UI on its respective port:

- **Ollama** (8000): http://127.0.0.1:8000/docs
- **ONNX GenAI** (8002): http://127.0.0.1:8002/docs
- **ONNX** (8001): http://127.0.0.1:8001/docs

The Swagger UI provides:
- 🎯 Interactive endpoint testing
- 📝 Detailed request/response schemas
- 🔍 Example requests and responses
- 📚 Complete API documentation

### Quick Start (ONNX GenAI)

1. **Download a pre-exported model**:
   ```bash
   huggingface-cli download microsoft/Phi-3-mini-4k-instruct-onnx --local-dir ./genai-model
   ```

2. **Update `.env`**:
   ```env
   GENAI_MODEL_DIR=C:\ai\models\phi3-mini-4k-instruct
   GENAI_DEVICE=cpu
   GENAI_MAX_LENGTH=2048
   ```

3. **Start the server**:
   ```bash
   uvicorn app_onnx_genai:app --host 127.0.0.1 --port 8002 --reload
   ```

4. **Test it**:
   ```bash
   curl -X POST http://127.0.0.1:8002/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"messages":[{"role":"user","content":"Hello!"}]}'
   ```

## Performance Metrics

All API responses include comprehensive performance metrics following industry best practices for LLM inference benchmarking.

### Available Metrics

| Metric | Description | Available In |
|--------|-------------|--------------|
| **TTFT** | Time to First Token (seconds) - Measures responsiveness | Streaming only |
| **Total Latency** | End-to-end latency from request to completion (seconds) | Both |
| **Tokens/Second** | Overall tokens processed per second (input + output / total time) | Both |
| **Output Tokens/Second** | Output tokens generated per second (output / generation time) | Both |
| **Input Tokens** | Number of tokens in the input prompt | Both |
| **Output Tokens** | Number of tokens in the generated output | Both |
| **TPOT** | Time Per Output Token (seconds) - Average time between tokens | Both |
| **Model** | Model used for generation | Both |

### Metrics Interpretation

- **TTFT < 0.5s**: Excellent responsiveness for real-time applications
- **Output Tokens/Second > 50**: Good generation speed for most use cases
- **TPOT < 0.02s**: Smooth streaming experience (faster than human reading)

### Example Response with Metrics

**Non-streaming:**
```json
{
  "content": "The capital of France is Paris.",
  "metrics": {
    "ttft": null,
    "total_latency": 1.2456,
    "tokens_per_second": 45.2,
    "output_tokens_per_second": 52.8,
    "input_tokens": 23,
    "output_tokens": 12,
    "tpot": 0.0189,
    "model": "smollm2:1.7b"
  }
}
```

**Streaming (final event):**
```
data: {"done": true, "token": "[DONE]", "metrics": {"ttft": 0.234, "total_latency": 2.456, ...}}
```

### API Endpoints

#### Health Check
```bash
GET /healthz
```

**Response:**
```json
{
  "status": "ok"
}
```

#### Non-Streaming Chat
```bash
POST /v1/chat
```

**Request Body:**
```json
{
  "model": "mistral:7b-instruct",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ],
  "temperature": 0.2,
  "max_tokens": null
}
```

**Response:**
```json
{
  "content": "I'm doing well, thank you for asking! How can I help you today?",
  "metrics": {
    "ttft": null,
    "total_latency": 1.2456,
    "tokens_per_second": 45.2,
    "output_tokens_per_second": 52.8,
    "input_tokens": 23,
    "output_tokens": 12,
    "tpot": 0.0189,
    "model": "smollm2:1.7b"
  }
}
```

#### Streaming Chat (SSE)
```bash
POST /v1/chat/stream
```

**Request Body:** Same as non-streaming endpoint

**Response:** Server-Sent Events stream
```
data: {"token":"I"}

data: {"token":"'m"}

data: {"token":" doing"}

data: {"token":" well"}

data: {"done": true, "token": "[DONE]", "metrics": {"ttft": 0.234, "total_latency": 2.456, "tokens_per_second": 45.2, "output_tokens_per_second": 52.8, "input_tokens": 23, "output_tokens": 12, "tpot": 0.0189, "model": "smollm2:1.7b"}}
```

### Example Usage

**Python:**
```python
import requests

# Non-streaming
response = requests.post(
    "http://127.0.0.1:8000/v1/chat",
    json={
        "model": "mistral:7b-instruct",
        "messages": [
            {"role": "user", "content": "Hello!"}
        ]
    }
)
print(response.json()["content"])

# Streaming
response = requests.post(
    "http://127.0.0.1:8000/v1/chat/stream",
    json={
        "model": "mistral:7b-instruct",
        "messages": [
            {"role": "user", "content": "Hello!"}
        ]
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

**cURL:**
```bash
# Non-streaming
curl -X POST http://127.0.0.1:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral:7b-instruct",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'

# Streaming
curl -X POST http://127.0.0.1:8000/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral:7b-instruct",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

## Project Structure

```
llm-api/
├── app_ollama.py       # Main FastAPI application
├── main.py             # Server entry point with hot reload
├── .env                # Environment configuration
├── requirements.txt    # Python dependencies
├── setup.py            # Package installation script
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Development

### Hot Reload

Set `RELOAD=true` in `.env` and run:
```bash
python main.py
```

The server will automatically restart when you modify the code.

### Adding Dependencies

1. Add the package to `requirements.txt`
2. Install it:
   ```bash
   pip install -r requirements.txt
   ```

## Production Deployment

1. Set `RELOAD=false` in `.env`
2. Adjust `WORKERS` based on your CPU cores
3. Consider using a process manager like `systemd` or `supervisor`
4. Use a reverse proxy like Nginx for SSL and load balancing

## Troubleshooting

### Ollama Connection Issues

**Error:** `httpx.ConnectError` or `Connection refused`

**Solution:** Ensure Ollama is running:
```bash
ollama serve
```

### Model Not Found

**Error:** Model not available

**Solution:** Pull the model first:
```bash
ollama pull mistral:7b-instruct
```

### Port Already in Use

**Error:** `Address already in use`

**Solution:** Change the `PORT` in `.env` or stop the process using the port.

## License

[Your License Here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.
