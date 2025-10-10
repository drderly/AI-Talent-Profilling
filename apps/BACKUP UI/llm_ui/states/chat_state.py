"""Chat state management with SSE streaming support."""
import reflex as rx
from typing import List, Dict, Any
import asyncio
import json
from datetime import datetime
from ..api_client import llm_client
from ..models import ChatHistory, UsageLog


class Message(rx.Base):
    """Message model for chat."""
    role: str
    content: str
    timestamp: str = ""


class ChatState(rx.State):
    """Chat state with streaming support."""
    
    # Chat messages
    messages: List[Message] = []
    current_input: str = ""
    is_streaming: bool = False
    current_response: str = ""
    
    # Chat settings
    selected_model: str = "smollm2:1.7b"
    temperature: float = 0.2
    max_tokens: int = 2048
    context_window: int = 4096
    
    # Advanced modes
    thinking_mode: bool = False
    browsing_mode: bool = False
    attach_mode: bool = False
    
    # Chat history
    current_chat_id: int | None = None
    chat_title: str = "New Chat"
    
    # Performance metrics
    last_metrics: Dict[str, Any] = {}
    
    # Error handling
    error_message: str = ""
    
    def set_current_input(self, value: str):
        """Set current input."""
        self.current_input = value
    
    def set_selected_model(self, value: str):
        """Set selected model."""
        self.selected_model = value
    
    def set_temperature(self, value: float):
        """Set temperature."""
        self.temperature = value
    
    def set_max_tokens(self, value: int):
        """Set max tokens."""
        self.max_tokens = value
    
    def toggle_thinking_mode(self):
        """Toggle thinking mode."""
        self.thinking_mode = not self.thinking_mode
    
    def toggle_browsing_mode(self):
        """Toggle browsing mode."""
        self.browsing_mode = not self.browsing_mode
    
    def toggle_attach_mode(self):
        """Toggle attach mode."""
        self.attach_mode = not self.attach_mode
    
    async def send_message(self):
        """Send message with streaming."""
        if not self.current_input.strip():
            return
        
        # Add user message
        user_message = Message(
            role="user",
            content=self.current_input,
            timestamp=datetime.now().strftime("%H:%M")
        )
        self.messages.append(user_message)
        
        # Clear input
        user_input = self.current_input
        self.current_input = ""
        self.is_streaming = True
        self.current_response = ""
        self.error_message = ""
        
        # Add thinking mode system message if enabled
        system_messages = []
        if self.thinking_mode:
            system_messages.append({
                "role": "system",
                "content": "Think step by step and show your reasoning process."
            })
        
        # Prepare messages for API
        api_messages = system_messages + [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages[-10:]  # Keep last 10 messages for context
        ]
        
        try:
            # Stream response
            async for chunk in llm_client.chat_stream(
                model=self.selected_model,
                messages=api_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            ):
                if chunk.get("done"):
                    # Final chunk with metrics
                    self.last_metrics = chunk.get("metrics", {})
                    
                    # Add assistant message
                    assistant_message = Message(
                        role="assistant",
                        content=self.current_response,
                        timestamp=datetime.now().strftime("%H:%M")
                    )
                    self.messages.append(assistant_message)
                    
                    # Log usage (if user is authenticated)
                    await self._log_usage(user_input, self.current_response)
                    
                    # Save chat history
                    await self._save_chat_history()
                    
                    self.is_streaming = False
                    self.current_response = ""
                    break
                
                # Append token to current response
                token = chunk.get("token", "")
                self.current_response += token
                yield
                
        except Exception as e:
            self.error_message = f"Error: {str(e)}"
            self.is_streaming = False
            self.current_response = ""
    
    async def _log_usage(self, input_text: str, output_text: str):
        """Log usage to database."""
        try:
            # Get user_id from auth state (you'll need to access this)
            user_id = self.router.session.client_token  # Placeholder
            
            metrics = self.last_metrics
            input_tokens = metrics.get("input_tokens", 0)
            output_tokens = metrics.get("output_tokens", 0)
            total_tokens = input_tokens + output_tokens
            duration = metrics.get("total_latency", 0)
            
            with rx.session() as session:
                usage_log = UsageLog(
                    user_id=1,  # TODO: Get from auth state
                    model_name=self.selected_model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    cost=0.0,  # TODO: Calculate based on model pricing
                    duration=duration,
                    created_at=datetime.now()
                )
                session.add(usage_log)
                session.commit()
        except Exception as e:
            print(f"Error logging usage: {e}")
    
    async def _save_chat_history(self):
        """Save chat history to database."""
        try:
            with rx.session() as session:
                messages_json = json.dumps([
                    {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp}
                    for msg in self.messages
                ])
                
                if self.current_chat_id:
                    # Update existing chat
                    chat = session.get(ChatHistory, self.current_chat_id)
                    if chat:
                        chat.messages = messages_json
                        chat.updated_at = datetime.now()
                        session.add(chat)
                else:
                    # Create new chat
                    chat = ChatHistory(
                        user_id=1,  # TODO: Get from auth state
                        model_name=self.selected_model,
                        messages=messages_json,
                        title=self.chat_title,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    session.add(chat)
                
                session.commit()
                
                if not self.current_chat_id and chat.id:
                    self.current_chat_id = chat.id
        except Exception as e:
            print(f"Error saving chat history: {e}")
    
    def new_chat(self):
        """Start a new chat."""
        self.messages = []
        self.current_input = ""
        self.current_response = ""
        self.is_streaming = False
        self.current_chat_id = None
        self.chat_title = "New Chat"
        self.error_message = ""
        self.last_metrics = {}
    
    def clear_chat(self):
        """Clear current chat."""
        self.new_chat()
