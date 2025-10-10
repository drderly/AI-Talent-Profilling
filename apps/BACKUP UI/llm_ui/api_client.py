"""API client for communicating with LLM API backend."""
import httpx
import os
from typing import List, Dict, Any, AsyncGenerator
import json
from dotenv import load_dotenv

load_dotenv()

LLM_API_URL = os.getenv("LLM_API_URL", "http://127.0.0.1:8000")


class LLMAPIClient:
    """Client for LLM API."""
    
    def __init__(self, base_url: str = LLM_API_URL):
        self.base_url = base_url
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/healthz")
            response.raise_for_status()
            return response.json()
    
    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int | None = None
    ) -> Dict[str, Any]:
        """Non-streaming chat completion."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def chat_stream(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int | None = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Streaming chat completion with SSE."""
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/chat/stream",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        try:
                            yield json.loads(data)
                        except json.JSONDecodeError:
                            continue


# Create a global instance
llm_client = LLMAPIClient()
