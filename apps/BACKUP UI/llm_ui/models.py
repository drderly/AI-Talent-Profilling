"""Database models for LLM UI."""
import reflex as rx
from datetime import datetime
from typing import Optional


class User(rx.Model, table=True):
    """User model for authentication."""
    email: str
    username: str
    password_hash: str
    is_admin: bool = False
    created_at: datetime = datetime.now()
    last_login: Optional[datetime] = None


class AIProvider(rx.Model, table=True):
    """AI Provider model (e.g., Ollama, OpenAI, Anthropic)."""
    name: str
    api_url: str
    api_key: Optional[str] = None
    provider_type: str  # ollama, openai, anthropic, etc.
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class AIModel(rx.Model, table=True):
    """AI Model model."""
    name: str
    display_name: str
    provider_id: int
    model_type: str  # text, image, audio, etc.
    context_window: int = 4096
    max_tokens: int = 2048
    is_active: bool = True
    created_at: datetime = datetime.now()


class AIType(rx.Model, table=True):
    """AI Type/Category model."""
    name: str
    description: str
    icon: str = "🤖"
    created_at: datetime = datetime.now()


class MediaProvider(rx.Model, table=True):
    """Media Provider model (e.g., Stable Diffusion, DALL-E)."""
    name: str
    api_url: str
    api_key: Optional[str] = None
    provider_type: str
    is_active: bool = True
    created_at: datetime = datetime.now()


class MediaModel(rx.Model, table=True):
    """Media Model model."""
    name: str
    display_name: str
    provider_id: int
    media_type: str  # image, video, audio
    is_active: bool = True
    created_at: datetime = datetime.now()


class MediaType(rx.Model, table=True):
    """Media Type/Category model."""
    name: str
    description: str
    icon: str = "🎨"
    created_at: datetime = datetime.now()


class BackgroundJob(rx.Model, table=True):
    """Background Job model for tracking async tasks."""
    job_id: str
    job_type: str  # model_sync, data_export, etc.
    status: str  # pending, running, completed, failed
    progress: int = 0
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = datetime.now()
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class APIKey(rx.Model, table=True):
    """API Key model for managing access keys."""
    key_name: str
    api_key: str
    user_id: int
    is_active: bool = True
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    created_at: datetime = datetime.now()


class ChatHistory(rx.Model, table=True):
    """Chat History model."""
    user_id: int
    project_id: Optional[int] = None
    model_name: str
    messages: str  # JSON string of messages
    title: str = "New Chat"
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class Project(rx.Model, table=True):
    """Project model for organizing chats."""
    user_id: int
    name: str
    description: Optional[str] = None
    icon: str = "📁"
    created_at: datetime = datetime.now()


class SystemPrompt(rx.Model, table=True):
    """System Prompt model for saving custom prompts."""
    user_id: int
    name: str
    prompt: str
    is_public: bool = False
    tags: Optional[str] = None  # JSON array
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class UsageLog(rx.Model, table=True):
    """Usage Log model for tracking API usage."""
    user_id: int
    model_name: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float = 0.0
    duration: float  # in seconds
    created_at: datetime = datetime.now()


class MonitoringLog(rx.Model, table=True):
    """Monitoring Log model for system events."""
    log_level: str  # info, warning, error, critical
    log_type: str  # api_call, system, auth, etc.
    message: str
    user_id: Optional[int] = None
    extra_data: Optional[str] = None  # JSON string (renamed from metadata to avoid conflict)
    created_at: datetime = datetime.now()


class PerformanceMetric(rx.Model, table=True):
    """Performance Metric model for tracking system performance."""
    metric_name: str
    metric_value: float
    model_name: Optional[str] = None
    endpoint: Optional[str] = None
    created_at: datetime = datetime.now()
