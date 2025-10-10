"""
Chat interface with streaming support
"""
import panel as pn
import param
import asyncio
import json
from datetime import datetime
from typing import List, Dict
from llm_client import LLMClient, format_messages, calculate_token_estimate
from models import get_session, ChatHistory, AIModel, Project
from auth import AuthState

pn.extension(design="material", notifications=True)

class ChatMessage(param.Parameterized):
    """Individual chat message"""
    role = param.String(default="user")
    content = param.String(default="")
    timestamp = param.Parameter(default=None)
    
    def __init__(self, role: str, content: str, **params):
        super().__init__(role=role, content=content, **params)
        if self.timestamp is None:
            self.timestamp = datetime.now()

class ChatState(param.Parameterized):
    """Chat application state"""
    
    messages = param.List(default=[])
    current_input = param.String(default="")
    is_streaming = param.Boolean(default=False)
    selected_model = param.String(default="smollm2:1.7b")
    temperature = param.Number(default=0.7, bounds=(0.0, 2.0))
    max_tokens = param.Integer(default=2048, bounds=(1, 8192))
    context_window = param.Integer(default=4096)
    thinking_mode = param.Boolean(default=False)
    browsing_mode = param.Boolean(default=False)
    attach_mode = param.Boolean(default=False)
    
    # Performance metrics
    last_ttft = param.Number(default=0.0)
    last_latency = param.Number(default=0.0)
    last_tokens_per_sec = param.Number(default=0.0)
    last_input_tokens = param.Integer(default=0)
    last_output_tokens = param.Integer(default=0)
    
    # Chat management
    current_chat_id = param.Integer(default=None)
    chat_title = param.String(default="New Chat")
    current_project_id = param.Integer(default=None)
    
    def __init__(self, auth_state: AuthState, **params):
        super().__init__(**params)
        self.auth_state = auth_state
        self.llm_client = LLMClient()
        self._streaming_task = None
    
    def add_message(self, role: str, content: str):
        """Add a message to chat"""
        msg = ChatMessage(role=role, content=content)
        self.messages = self.messages + [msg]
    
    def clear_chat(self):
        """Clear current chat"""
        self.messages = []
        self.current_chat_id = None
        self.chat_title = "New Chat"
        self.current_project_id = None
        pn.state.notifications.success("Chat cleared")
    
    def save_chat(self):
        """Save chat to database"""
        if not self.messages or not self.auth_state.is_authenticated:
            return
        
        db = get_session()
        try:
            # Get user session
            session = self.auth_state.session_id
            if not session:
                return
            
            # Get model
            model = db.query(AIModel).filter_by(model_id=self.selected_model).first()
            if not model:
                return
            
            # Prepare messages as JSON
            messages_json = json.dumps([
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in self.messages
            ])
            
            # Generate title from first user message
            title = self.chat_title
            if title == "New Chat" and len(self.messages) > 0:
                first_msg = next((m for m in self.messages if m.role == "user"), None)
                if first_msg:
                    title = first_msg.content[:50] + ("..." if len(first_msg.content) > 50 else "")
            
            if self.current_chat_id:
                # Update existing chat
                chat = db.query(ChatHistory).filter_by(id=self.current_chat_id).first()
                if chat:
                    chat.messages = messages_json
                    chat.title = title
                    chat.temperature = self.temperature
                    chat.max_tokens = self.max_tokens
                    chat.context_window = self.context_window
                    chat.updated_at = datetime.utcnow()
            else:
                # Create new chat
                from auth import session_manager
                user_session = session_manager.get_session(self.auth_state.session_id)
                if not user_session:
                    return
                
                chat = ChatHistory(
                    user_id=user_session["user_id"],
                    project_id=self.current_project_id,
                    model_id=model.id,
                    title=title,
                    messages=messages_json,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    context_window=self.context_window
                )
                db.add(chat)
                db.commit()
                self.current_chat_id = chat.id
                self.chat_title = title
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            pn.state.notifications.error(f"Error saving chat: {str(e)}")
        finally:
            db.close()
    
    async def send_message_async(self, message: str):
        """Send message and get streaming response"""
        if not message.strip() or self.is_streaming:
            return
        
        # Add user message
        self.add_message("user", message)
        self.current_input = ""
        self.is_streaming = True
        
        # Prepare messages for API
        api_messages = []
        if self.thinking_mode:
            api_messages.append({
                "role": "system",
                "content": "You are a helpful AI assistant. Think step-by-step and show your reasoning."
            })
        
        for msg in self.messages:
            api_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add placeholder for assistant response
        assistant_msg = ChatMessage(role="assistant", content="")
        self.messages = self.messages + [assistant_msg]
        
        try:
            # Stream response
            async for event in self.llm_client.chat_stream(
                messages=api_messages,
                model=self.selected_model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            ):
                if event["type"] == "token":
                    # Update assistant message content
                    assistant_msg.content = event["content"]
                    # Trigger update
                    self.messages = self.messages[:]
                
                elif event["type"] == "done":
                    # Update metrics
                    metrics = event.get("metrics", {})
                    self.last_ttft = metrics.get("ttft", 0.0) or 0.0
                    self.last_latency = metrics.get("total_latency", 0.0) or 0.0
                    self.last_tokens_per_sec = metrics.get("output_tokens_per_second", 0.0) or 0.0
                    self.last_input_tokens = metrics.get("input_tokens", 0) or 0
                    self.last_output_tokens = metrics.get("output_tokens", 0) or 0
                    
                    # Save chat
                    self.save_chat()
                
                elif event["type"] == "error":
                    pn.state.notifications.error(f"Error: {event['error']}")
                    # Remove incomplete assistant message
                    self.messages = self.messages[:-1]
        
        except Exception as e:
            pn.state.notifications.error(f"Error sending message: {str(e)}")
            # Remove incomplete assistant message
            self.messages = self.messages[:-1]
        
        finally:
            self.is_streaming = False

def create_message_bubble(msg: ChatMessage, is_user: bool):
    """Create a styled message bubble"""
    
    timestamp_str = msg.timestamp.strftime("%H:%M") if msg.timestamp else ""
    
    if is_user:
        bubble_style = {
            "background": "#007bff",
            "color": "white",
            "padding": "12px 16px",
            "border-radius": "18px 18px 4px 18px",
            "max-width": "70%",
            "margin": "8px 0 8px auto",
            "word-wrap": "break-word"
        }
        container_style = {"display": "flex", "justify-content": "flex-end"}
    else:
        bubble_style = {
            "background": "#f1f3f4",
            "color": "#202124",
            "padding": "12px 16px",
            "border-radius": "18px 18px 18px 4px",
            "max-width": "70%",
            "margin": "8px 0",
            "word-wrap": "break-word"
        }
        container_style = {"display": "flex", "justify-content": "flex-start"}
    
    bubble = pn.Column(
        pn.pane.Markdown(
            msg.content,
            styles={"margin": "0", "color": "inherit"}
        ),
        pn.pane.HTML(
            f"<small style='opacity: 0.7;'>{timestamp_str}</small>",
            styles={"margin-top": "4px"}
        ),
        styles=bubble_style
    )
    
    return pn.pane.HTML(
        bubble,
        styles=container_style
    )

def create_chat_interface(auth_state: AuthState):
    """Create main chat interface"""
    
    chat_state = ChatState(auth_state=auth_state)
    
    # Model selector
    db = get_session()
    models = db.query(AIModel).filter_by(is_active=True).all()
    model_options = {f"{m.name} ({m.model_id})": m.model_id for m in models}
    db.close()
    
    if not model_options:
        model_options = {"SmolLM2 1.7B (smollm2:1.7b)": "smollm2:1.7b"}
    
    model_selector = pn.widgets.Select(
        name="Model",
        options=model_options,
        value=chat_state.selected_model,
        width=250
    )
    model_selector.link(chat_state, value="selected_model")
    
    # Temperature slider
    temperature_slider = pn.widgets.FloatSlider(
        name="Temperature",
        start=0.0,
        end=2.0,
        step=0.1,
        value=chat_state.temperature,
        width=200
    )
    temperature_slider.link(chat_state, value="temperature")
    
    # Max tokens input
    max_tokens_input = pn.widgets.IntInput(
        name="Max Tokens",
        value=chat_state.max_tokens,
        start=1,
        end=8192,
        step=128,
        width=150
    )
    max_tokens_input.link(chat_state, value="max_tokens")
    
    # Mode toggles
    thinking_toggle = pn.widgets.Toggle(
        name="🧠 Thinking",
        value=chat_state.thinking_mode,
        button_type="success",
        width=120
    )
    thinking_toggle.link(chat_state, value="thinking_mode")
    
    browsing_toggle = pn.widgets.Toggle(
        name="🌐 Browse",
        value=chat_state.browsing_mode,
        disabled=True,
        width=120
    )
    
    attach_toggle = pn.widgets.Toggle(
        name="📎 Attach",
        value=chat_state.attach_mode,
        disabled=True,
        width=120
    )
    
    # Chat controls
    new_chat_btn = pn.widgets.Button(
        name="New Chat",
        button_type="primary",
        icon="plus",
        width=120
    )
    
    clear_chat_btn = pn.widgets.Button(
        name="Clear",
        button_type="warning",
        icon="trash",
        width=100
    )
    
    def on_new_chat(event):
        chat_state.clear_chat()
    
    def on_clear_chat(event):
        chat_state.clear_chat()
    
    new_chat_btn.on_click(on_new_chat)
    clear_chat_btn.on_click(on_clear_chat)
    
    # Performance metrics display
    metrics_display = pn.pane.Markdown(
        "",
        styles={
            "background": "#f8f9fa",
            "padding": "8px 12px",
            "border-radius": "6px",
            "font-size": "0.85em"
        }
    )
    
    def update_metrics(event=None):
        if chat_state.last_latency > 0:
            metrics_text = f"""
**⚡ Performance:** TTFT: {chat_state.last_ttft:.2f}s | 
Latency: {chat_state.last_latency:.2f}s | 
Speed: {chat_state.last_tokens_per_sec:.1f} tok/s | 
Tokens: {chat_state.last_input_tokens}↑ {chat_state.last_output_tokens}↓
            """.strip()
            metrics_display.object = metrics_text
        else:
            metrics_display.object = ""
    
    chat_state.param.watch(update_metrics, [
        "last_ttft", "last_latency", "last_tokens_per_sec",
        "last_input_tokens", "last_output_tokens"
    ])
    
    # Messages container
    messages_column = pn.Column(
        sizing_mode="stretch_width",
        scroll=True,
        height=500,
        styles={
            "background": "white",
            "padding": "16px",
            "border-radius": "8px"
        }
    )
    
    def update_messages(event=None):
        messages_column.clear()
        for msg in chat_state.messages:
            is_user = msg.role == "user"
            bubble = create_message_bubble(msg, is_user)
            messages_column.append(bubble)
        
        # Auto-scroll to bottom
        if len(messages_column) > 0:
            messages_column.scroll_to_bottom()
    
    chat_state.param.watch(update_messages, "messages")
    
    # Input area
    message_input = pn.widgets.TextAreaInput(
        placeholder="Type your message here...",
        auto_grow=True,
        max_rows=5,
        height=80,
        styles={"width": "100%"}
    )
    
    send_btn = pn.widgets.Button(
        name="Send",
        button_type="primary",
        icon="send",
        width=100,
        height=40
    )
    
    streaming_indicator = pn.indicators.LoadingSpinner(
        value=False,
        size=30,
        visible=False
    )
    
    def update_streaming_indicator(event=None):
        streaming_indicator.visible = chat_state.is_streaming
        send_btn.disabled = chat_state.is_streaming
    
    chat_state.param.watch(update_streaming_indicator, "is_streaming")
    
    def on_send(event):
        message = message_input.value
        if message.strip():
            message_input.value = ""
            asyncio.create_task(chat_state.send_message_async(message))
    
    send_btn.on_click(on_send)
    
    # Layout
    controls_row = pn.Row(
        model_selector,
        temperature_slider,
        max_tokens_input,
        thinking_toggle,
        browsing_toggle,
        attach_toggle,
        new_chat_btn,
        clear_chat_btn,
        styles={
            "background": "#f8f9fa",
            "padding": "12px",
            "border-radius": "8px",
            "margin-bottom": "16px"
        },
        scroll=True
    )
    
    input_row = pn.Row(
        message_input,
        pn.Column(send_btn, streaming_indicator),
        styles={"margin-top": "16px"}
    )
    
    chat_layout = pn.Column(
        pn.pane.Markdown(
            f"# 💬 Chat - {chat_state.chat_title}",
            styles={"margin-bottom": "16px"}
        ),
        controls_row,
        metrics_display,
        messages_column,
        input_row,
        sizing_mode="stretch_width"
    )
    
    # Update title when it changes
    def update_title(event=None):
        chat_layout[0].object = f"# 💬 Chat - {chat_state.chat_title}"
    
    chat_state.param.watch(update_title, "chat_title")
    
    return chat_layout
