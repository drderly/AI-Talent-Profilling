"""Admin state management."""
import reflex as rx
from typing import List
from datetime import datetime
from ..models import (
    AIProvider, AIModel, AIType,
    MediaProvider, MediaModel, MediaType,
    BackgroundJob, APIKey, MonitoringLog, 
    PerformanceMetric, UsageLog
)


class AdminDashboardState(rx.State):
    """Admin dashboard state."""
    
    # Statistics
    total_users: int = 0
    total_chats: int = 0
    total_api_calls: int = 0
    total_tokens: int = 0
    
    # Recent logs
    recent_logs: List[MonitoringLog] = []
    
    def load_dashboard_data(self):
        """Load dashboard statistics."""
        with rx.session() as session:
            # Get statistics (simplified for now)
            self.total_users = 10  # TODO: Count from User table
            self.total_chats = 25
            self.total_api_calls = 150
            self.total_tokens = 50000
            
            # Get recent logs
            self.recent_logs = session.exec(
                MonitoringLog.select().order_by(MonitoringLog.created_at.desc()).limit(10)
            ).all()


class AIProviderState(rx.State):
    """AI Provider management state."""
    
    providers: List[AIProvider] = []
    
    # Form fields
    form_name: str = ""
    form_api_url: str = ""
    form_api_key: str = ""
    form_provider_type: str = "ollama"
    form_is_active: bool = True
    editing_id: int | None = None
    
    error_message: str = ""
    success_message: str = ""
    
    def load_providers(self):
        """Load all AI providers."""
        with rx.session() as session:
            self.providers = session.exec(AIProvider.select()).all()
    
    def set_form_name(self, value: str):
        self.form_name = value
    
    def set_form_api_url(self, value: str):
        self.form_api_url = value
    
    def set_form_api_key(self, value: str):
        self.form_api_key = value
    
    def set_form_provider_type(self, value: str):
        self.form_provider_type = value
    
    def toggle_form_is_active(self):
        self.form_is_active = not self.form_is_active
    
    def save_provider(self):
        """Save or update provider."""
        self.error_message = ""
        self.success_message = ""
        
        if not self.form_name or not self.form_api_url:
            self.error_message = "Name and API URL are required"
            return
        
        with rx.session() as session:
            if self.editing_id:
                # Update existing
                provider = session.get(AIProvider, self.editing_id)
                if provider:
                    provider.name = self.form_name
                    provider.api_url = self.form_api_url
                    provider.api_key = self.form_api_key
                    provider.provider_type = self.form_provider_type
                    provider.is_active = self.form_is_active
                    provider.updated_at = datetime.now()
                    session.add(provider)
                    self.success_message = "Provider updated successfully"
            else:
                # Create new
                provider = AIProvider(
                    name=self.form_name,
                    api_url=self.form_api_url,
                    api_key=self.form_api_key,
                    provider_type=self.form_provider_type,
                    is_active=self.form_is_active,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                session.add(provider)
                self.success_message = "Provider created successfully"
            
            session.commit()
            self.load_providers()
            self.clear_form()
    
    def edit_provider(self, provider_id: int):
        """Load provider for editing."""
        with rx.session() as session:
            provider = session.get(AIProvider, provider_id)
            if provider:
                self.editing_id = provider_id
                self.form_name = provider.name
                self.form_api_url = provider.api_url
                self.form_api_key = provider.api_key or ""
                self.form_provider_type = provider.provider_type
                self.form_is_active = provider.is_active
    
    def delete_provider(self, provider_id: int):
        """Delete provider."""
        with rx.session() as session:
            provider = session.get(AIProvider, provider_id)
            if provider:
                session.delete(provider)
                session.commit()
                self.load_providers()
                self.success_message = "Provider deleted successfully"
    
    def clear_form(self):
        """Clear form fields."""
        self.form_name = ""
        self.form_api_url = ""
        self.form_api_key = ""
        self.form_provider_type = "ollama"
        self.form_is_active = True
        self.editing_id = None


class AIModelState(rx.State):
    """AI Model management state."""
    
    models: List[AIModel] = []
    providers: List[AIProvider] = []
    
    # Form fields
    form_name: str = ""
    form_display_name: str = ""
    form_provider_id: int = 0
    form_model_type: str = "text"
    form_context_window: int = 4096
    form_max_tokens: int = 2048
    form_is_active: bool = True
    editing_id: int | None = None
    
    error_message: str = ""
    success_message: str = ""
    
    def load_models(self):
        """Load all AI models."""
        with rx.session() as session:
            self.models = session.exec(AIModel.select()).all()
            self.providers = session.exec(AIProvider.select()).all()
    
    def save_model(self):
        """Save or update model."""
        self.error_message = ""
        self.success_message = ""
        
        if not self.form_name or not self.form_display_name or self.form_provider_id == 0:
            self.error_message = "All fields are required"
            return
        
        with rx.session() as session:
            if self.editing_id:
                # Update existing
                model = session.get(AIModel, self.editing_id)
                if model:
                    model.name = self.form_name
                    model.display_name = self.form_display_name
                    model.provider_id = self.form_provider_id
                    model.model_type = self.form_model_type
                    model.context_window = self.form_context_window
                    model.max_tokens = self.form_max_tokens
                    model.is_active = self.form_is_active
                    session.add(model)
                    self.success_message = "Model updated successfully"
            else:
                # Create new
                model = AIModel(
                    name=self.form_name,
                    display_name=self.form_display_name,
                    provider_id=self.form_provider_id,
                    model_type=self.form_model_type,
                    context_window=self.form_context_window,
                    max_tokens=self.form_max_tokens,
                    is_active=self.form_is_active,
                    created_at=datetime.now()
                )
                session.add(model)
                self.success_message = "Model created successfully"
            
            session.commit()
            self.load_models()
            self.clear_form()
    
    def delete_model(self, model_id: int):
        """Delete model."""
        with rx.session() as session:
            model = session.get(AIModel, model_id)
            if model:
                session.delete(model)
                session.commit()
                self.load_models()
                self.success_message = "Model deleted successfully"
    
    def clear_form(self):
        """Clear form fields."""
        self.form_name = ""
        self.form_display_name = ""
        self.form_provider_id = 0
        self.form_model_type = "text"
        self.form_context_window = 4096
        self.form_max_tokens = 2048
        self.form_is_active = True
        self.editing_id = None
