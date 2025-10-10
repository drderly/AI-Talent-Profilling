"""
Main entry point for running the LLM API server with hot reload.
Usage: python main.py

Loads configuration from .env file (like in JavaScript)
"""
import uvicorn
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    
    # Configuration from .env file (all values must be set in .env)
    HOST = os.getenv("HOST")
    PORT = int(os.getenv("PORT"))
    RELOAD = os.getenv("RELOAD").lower() == "true"
    WORKERS = int(os.getenv("WORKERS"))
    # HOST = os.getenv("HOST", "127.0.0.1")
    # PORT = int(os.getenv("PORT", "8000"))
    # RELOAD = os.getenv("RELOAD", "true").lower() == "true"
    # WORKERS = int(os.getenv("WORKERS", "2"))
    
    # Dynamic workers: use 1 worker if reload is enabled, otherwise use configured workers
    workers = 1 if RELOAD else WORKERS
    
    uvicorn.run(
        "app_ollama:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        workers=workers,
        log_level="info"
    )
