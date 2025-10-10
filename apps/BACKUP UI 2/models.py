"""
Database models for LLM UI application
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    """User roles"""
    USER = "user"
    ADMIN = "admin"

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")

class AIType(Base):
    """AI model types"""
    __tablename__ = "ai_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    providers = relationship("AIProvider", back_populates="ai_type")

class AIProvider(Base):
    """AI service providers"""
    __tablename__ = "ai_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    ai_type_id = Column(Integer, ForeignKey("ai_types.id"), nullable=False)
    api_url = Column(String(255), nullable=False)
    api_key = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ai_type = relationship("AIType", back_populates="providers")
    models = relationship("AIModel", back_populates="provider", cascade="all, delete-orphan")

class AIModel(Base):
    """AI models configuration"""
    __tablename__ = "ai_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=False)
    model_id = Column(String(100), nullable=False)  # e.g., "gpt-4", "mistral:7b"
    context_window = Column(Integer, default=4096)
    max_tokens = Column(Integer, default=2048)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    provider = relationship("AIProvider", back_populates="models")
    chat_histories = relationship("ChatHistory", back_populates="model")

class Project(Base):
    """Projects for organizing chats"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(50), default="💼")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    chat_histories = relationship("ChatHistory", back_populates="project")

class SystemPrompt(Base):
    """Reusable system prompts"""
    __tablename__ = "system_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)
    tags = Column(String(255))  # Comma-separated tags
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatHistory(Base):
    """Chat conversation history"""
    __tablename__ = "chat_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=False)
    title = Column(String(255), default="New Chat")
    messages = Column(Text)  # JSON string of messages array
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer)
    context_window = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chat_histories")
    project = relationship("Project", back_populates="chat_histories")
    model = relationship("AIModel", back_populates="chat_histories")

class UsageLog(Base):
    """Track API usage and costs"""
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_id = Column(Integer, ForeignKey("chat_histories.id"))
    model_name = Column(String(100), nullable=False)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    latency = Column(Float)  # in seconds
    ttft = Column(Float)  # Time to first token
    tokens_per_second = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="usage_logs")

class MonitoringLog(Base):
    """System monitoring and activity logs"""
    __tablename__ = "monitoring_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    details = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

class PerformanceMetric(Base):
    """Performance metrics tracking"""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    unit = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class BackgroundJob(Base):
    """Background job tracking"""
    __tablename__ = "background_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)  # PENDING, RUNNING, COMPLETED, FAILED
    progress = Column(Float, default=0.0)
    result = Column(Text)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class APIKey(Base):
    """API keys for external access"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup functions
def init_db(database_url="sqlite:///./llm_ui.db"):
    """Initialize database with tables"""
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(bind=engine)
    return engine

def get_session(database_url="sqlite:///./llm_ui.db"):
    """Get database session"""
    engine = create_engine(database_url, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def seed_data(session):
    """Seed initial data"""
    # Create default AI types
    ai_types = [
        AIType(name="LLM", description="Large Language Models"),
        AIType(name="Vision", description="Vision Models"),
        AIType(name="Audio", description="Audio Models"),
    ]
    
    for ai_type in ai_types:
        existing = session.query(AIType).filter_by(name=ai_type.name).first()
        if not existing:
            session.add(ai_type)
    
    session.commit()
    
    # Create default Ollama provider
    llm_type = session.query(AIType).filter_by(name="LLM").first()
    if llm_type:
        existing_provider = session.query(AIProvider).filter_by(name="Ollama").first()
        if not existing_provider:
            ollama_provider = AIProvider(
                name="Ollama",
                ai_type_id=llm_type.id,
                api_url="http://127.0.0.1:8000",
                is_active=True
            )
            session.add(ollama_provider)
            session.commit()
            
            # Create default models
            default_models = [
                AIModel(
                    name="SmolLM2 1.7B",
                    provider_id=ollama_provider.id,
                    model_id="smollm2:1.7b",
                    context_window=4096,
                    max_tokens=2048,
                    is_active=True
                ),
                AIModel(
                    name="Mistral 7B Instruct",
                    provider_id=ollama_provider.id,
                    model_id="mistral:7b-instruct",
                    context_window=8192,
                    max_tokens=4096,
                    is_active=True
                ),
            ]
            
            for model in default_models:
                session.add(model)
            session.commit()
    
    # Create default system prompts
    default_prompts = [
        SystemPrompt(
            name="General Assistant",
            description="A helpful and friendly AI assistant",
            content="You are a helpful, friendly, and knowledgeable AI assistant. Provide clear, accurate, and concise responses.",
            tags="general,assistant",
            is_public=True
        ),
        SystemPrompt(
            name="Code Assistant",
            description="Expert programmer and code reviewer",
            content="You are an expert programmer proficient in multiple languages. Help with coding, debugging, and best practices. Provide clear explanations and well-commented code.",
            tags="coding,programming,development",
            is_public=True
        ),
        SystemPrompt(
            name="Writing Assistant",
            description="Professional writing and editing help",
            content="You are a professional writer and editor. Help with writing, editing, proofreading, and improving text clarity and style.",
            tags="writing,editing,content",
            is_public=True
        ),
    ]
    
    for prompt in default_prompts:
        existing = session.query(SystemPrompt).filter_by(name=prompt.name).first()
        if not existing:
            session.add(prompt)
    
    session.commit()
