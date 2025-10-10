"""
LLM API Client for chat communication
"""
import httpx
import json
from typing import List, Dict, AsyncGenerator, Optional
import asyncio
import os
from dotenv import load_dotenv

class LLMClient:
    """Client for LLM API communication"""
    
    def __init__(self, base_url: str = None):
        # Load .env if present and pick up LLM_API_URL
        try:
            load_dotenv()
        except Exception:
            pass
        env_url = os.getenv("LLM_API_URL")
        resolved = base_url or env_url or "http://127.0.0.1:8000"
        self.base_url = resolved.rstrip("/")
        self.timeout = httpx.Timeout(120.0, connect=10.0)
    
    async def health_check(self) -> bool:
        """Check if API is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/healthz")
                return response.status_code == 200
        except Exception:
            return False
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "smollm2:1.7b",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict:
        """Non-streaming chat completion"""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v1/chat",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise RuntimeError(f"Chat request failed: {e}")
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "smollm2:1.7b",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        callback=None
    ) -> AsyncGenerator[Dict, None]:
        """Streaming chat completion with SSE"""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        full_content = ""
        metrics = None
        
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(None)) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/v1/chat/stream",
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        
                        # Parse SSE data
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        try:
                            data = json.loads(data_str)
                            
                            if data.get("done"):
                                # Final event with metrics
                                metrics = data.get("metrics")
                                yield {
                                    "type": "done",
                                    "content": full_content,
                                    "metrics": metrics
                                }
                                break
                            
                            # Token event
                            token = data.get("token", "")
                            if token:
                                full_content += token
                                
                                # Call callback if provided
                                if callback:
                                    try:
                                        callback(token)
                                    except Exception:
                                        pass
                                
                                yield {
                                    "type": "token",
                                    "token": token,
                                    "content": full_content
                                }
                        
                        except json.JSONDecodeError:
                            continue
        
        except httpx.ConnectError as e:
            yield {
                "type": "error",
                "error": f"Cannot connect to LLM API at {self.base_url}. {e}"
            }
        except httpx.HTTPError as e:
            yield {
                "type": "error",
                "error": f"HTTP error from LLM API: {e}"
            }
        except Exception as e:
            yield {
                "type": "error",
                "error": str(e)
            }

def format_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Format messages for API"""
    return [
        {
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        }
        for msg in messages
    ]

def calculate_token_estimate(text: str) -> int:
    """Rough token count estimation (1 token ≈ 4 characters)"""
    return len(text) // 4
