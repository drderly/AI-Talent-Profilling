"""Authentication utilities and state management."""
import reflex as rx
from typing import Optional
import hashlib
import secrets
from datetime import datetime
from .models import User


def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == password_hash


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


class AuthState(rx.State):
    """Authentication state management."""
    
    # Current user
    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    is_admin: bool = False
    is_authenticated: bool = False
    
    # Form states
    login_email: str = ""
    login_password: str = ""
    register_email: str = ""
    register_username: str = ""
    register_password: str = ""
    register_confirm_password: str = ""
    
    # Error and success messages
    error_message: str = ""
    success_message: str = ""
    
    def set_login_email(self, value: str):
        """Set login email."""
        self.login_email = value
    
    def set_login_password(self, value: str):
        """Set login password."""
        self.login_password = value
    
    def set_register_email(self, value: str):
        """Set register email."""
        self.register_email = value
    
    def set_register_username(self, value: str):
        """Set register username."""
        self.register_username = value
    
    def set_register_password(self, value: str):
        """Set register password."""
        self.register_password = value
    
    def set_register_confirm_password(self, value: str):
        """Set register confirm password."""
        self.register_confirm_password = value
    
    def login(self):
        """Handle user login."""
        self.error_message = ""
        self.success_message = ""
        
        if not self.login_email or not self.login_password:
            self.error_message = "Email and password are required"
            return
        
        with rx.session() as session:
            user = session.exec(
                User.select().where(User.email == self.login_email)
            ).first()
            
            if not user:
                self.error_message = "Invalid email or password"
                return
            
            if not verify_password(self.login_password, user.password_hash):
                self.error_message = "Invalid email or password"
                return
            
            # Update last login
            user.last_login = datetime.now()
            session.add(user)
            session.commit()
            
            # Set authenticated state
            self.user_id = user.id
            self.username = user.username
            self.email = user.email
            self.is_admin = user.is_admin
            self.is_authenticated = True
            
            # Clear form
            self.login_email = ""
            self.login_password = ""
            
            self.success_message = f"Welcome back, {user.username}!"
            
            # Redirect based on role
            if self.is_admin:
                return rx.redirect("/admin/dashboard")
            else:
                return rx.redirect("/chat")
    
    def register(self):
        """Handle user registration."""
        self.error_message = ""
        self.success_message = ""
        
        # Validation
        if not self.register_email or not self.register_username or not self.register_password:
            self.error_message = "All fields are required"
            return
        
        if self.register_password != self.register_confirm_password:
            self.error_message = "Passwords do not match"
            return
        
        if len(self.register_password) < 8:
            self.error_message = "Password must be at least 8 characters"
            return
        
        with rx.session() as session:
            # Check if user already exists
            existing_user = session.exec(
                User.select().where(User.email == self.register_email)
            ).first()
            
            if existing_user:
                self.error_message = "Email already registered"
                return
            
            # Create new user
            new_user = User(
                email=self.register_email,
                username=self.register_username,
                password_hash=hash_password(self.register_password),
                is_admin=False,  # Regular user by default
                created_at=datetime.now()
            )
            
            session.add(new_user)
            session.commit()
            
            # Clear form
            self.register_email = ""
            self.register_username = ""
            self.register_password = ""
            self.register_confirm_password = ""
            
            self.success_message = "Registration successful! Please login."
    
    def logout(self):
        """Handle user logout."""
        self.user_id = None
        self.username = None
        self.email = None
        self.is_admin = False
        self.is_authenticated = False
        self.error_message = ""
        self.success_message = ""
        return rx.redirect("/")
    
    def require_login(self):
        """Check if user is logged in, redirect to login if not."""
        if not self.is_authenticated:
            return rx.redirect("/login")
    
    def require_admin(self):
        """Check if user is admin, redirect to home if not."""
        if not self.is_authenticated:
            return rx.redirect("/login")
        if not self.is_admin:
            return rx.redirect("/chat")
