"""
Authentication and session management
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
import param
import panel as pn
from models import User, UserRole, get_session

class SessionManager:
    """Manage user sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.session_timeout = timedelta(hours=24)
    
    def create_session(self, user: User) -> str:
        """Create a new session for user"""
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session expired
        if datetime.utcnow() - session["last_activity"] > self.session_timeout:
            del self.sessions[session_id]
            return None
        
        # Update last activity
        session["last_activity"] = datetime.utcnow()
        return session
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def is_admin(self, session_id: str) -> bool:
        """Check if user is admin"""
        session = self.get_session(session_id)
        return session and session["role"] == UserRole.ADMIN

# Global session manager
session_manager = SessionManager()

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == password_hash

class AuthState(param.Parameterized):
    """Authentication state management"""
    
    is_authenticated = param.Boolean(default=False)
    session_id = param.String(default="")
    username = param.String(default="")
    email = param.String(default="")
    role = param.Parameter(default=None)
    error_message = param.String(default="")
    success_message = param.String(default="")
    
    def login(self, email: str, password: str) -> bool:
        """Login user"""
        self.error_message = ""
        self.success_message = ""
        
        if not email or not password:
            self.error_message = "Email and password are required"
            return False
        
        db = get_session()
        try:
            user = db.query(User).filter_by(email=email).first()
            
            if not user:
                self.error_message = "Invalid email or password"
                return False
            
            if not user.is_active:
                self.error_message = "Account is inactive"
                return False
            
            if not verify_password(password, user.password_hash):
                self.error_message = "Invalid email or password"
                return False
            
            # Create session
            self.session_id = session_manager.create_session(user)
            self.is_authenticated = True
            self.username = user.username
            self.email = user.email
            self.role = user.role
            self.success_message = f"Welcome back, {user.username}!"
            
            return True
            
        except Exception as e:
            self.error_message = f"Login error: {str(e)}"
            return False
        finally:
            db.close()
    
    def register(self, username: str, email: str, password: str, confirm_password: str) -> bool:
        """Register new user"""
        self.error_message = ""
        self.success_message = ""
        
        # Validation
        if not username or not email or not password:
            self.error_message = "All fields are required"
            return False
        
        if len(username) < 3:
            self.error_message = "Username must be at least 3 characters"
            return False
        
        if len(password) < 6:
            self.error_message = "Password must be at least 6 characters"
            return False
        
        if password != confirm_password:
            self.error_message = "Passwords do not match"
            return False
        
        if "@" not in email:
            self.error_message = "Invalid email format"
            return False
        
        db = get_session()
        try:
            # Check if user exists
            existing_user = db.query(User).filter(
                (User.email == email) | (User.username == username)
            ).first()
            
            if existing_user:
                if existing_user.email == email:
                    self.error_message = "Email already registered"
                else:
                    self.error_message = "Username already taken"
                return False
            
            # Create new user
            new_user = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
                role=UserRole.USER,
                is_active=True
            )
            
            db.add(new_user)
            db.commit()
            
            self.success_message = "Registration successful! Please login."
            return True
            
        except Exception as e:
            db.rollback()
            self.error_message = f"Registration error: {str(e)}"
            return False
        finally:
            db.close()
    
    def logout(self):
        """Logout user"""
        if self.session_id:
            session_manager.delete_session(self.session_id)
        
        self.is_authenticated = False
        self.session_id = ""
        self.username = ""
        self.email = ""
        self.role = None
        self.error_message = ""
        self.success_message = "Logged out successfully"
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.role == UserRole.ADMIN
    
    def get_user_initials(self) -> str:
        """Get user initials for avatar"""
        if not self.username:
            return "?"
        parts = self.username.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return self.username[:2].upper()

def create_login_page(auth_state: AuthState):
    """Create login page"""
    
    # Input fields
    email_input = pn.widgets.TextInput(
        name="Email",
        placeholder="Enter your email",
        width=300
    )
    
    password_input = pn.widgets.PasswordInput(
        name="Password",
        placeholder="Enter your password",
        width=300
    )
    
    # Messages
    message_pane = pn.pane.Alert(
        "", 
        alert_type="danger", 
        visible=False,
        width=300
    )
    
    def update_message(event=None):
        if auth_state.error_message:
            message_pane.object = auth_state.error_message
            message_pane.alert_type = "danger"
            message_pane.visible = True
        elif auth_state.success_message:
            message_pane.object = auth_state.success_message
            message_pane.alert_type = "success"
            message_pane.visible = True
        else:
            message_pane.visible = False
    
    auth_state.param.watch(update_message, ["error_message", "success_message"])
    
    # Login button
    def on_login(event):
        message_pane.visible = False
        success = auth_state.login(email_input.value, password_input.value)
        if not success:
            update_message()
    
    login_btn = pn.widgets.Button(
        name="Login",
        button_type="primary",
        width=300
    )
    login_btn.on_click(on_login)
    
    # Register link
    register_link = pn.pane.Markdown(
        "Don't have an account? [Register here](#register)",
        width=300
    )
    
    # Layout
    login_form = pn.Column(
        pn.pane.Markdown("# 🤖 LLM UI Login", styles={"text-align": "center"}),
        pn.layout.Spacer(height=20),
        message_pane,
        email_input,
        password_input,
        login_btn,
        pn.layout.Spacer(height=10),
        register_link,
        styles={
            "background": "white",
            "border-radius": "10px",
            "padding": "40px",
            "box-shadow": "0 2px 10px rgba(0,0,0,0.1)"
        },
        width=400
    )
    
    return pn.Column(
        login_form,
        styles={
            "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "min-height": "100vh"
        },
        align="center",
        sizing_mode="stretch_both"
    )

def create_register_page(auth_state: AuthState):
    """Create registration page"""
    
    # Input fields
    username_input = pn.widgets.TextInput(
        name="Username",
        placeholder="Choose a username",
        width=300
    )
    
    email_input = pn.widgets.TextInput(
        name="Email",
        placeholder="Enter your email",
        width=300
    )
    
    password_input = pn.widgets.PasswordInput(
        name="Password",
        placeholder="Choose a password",
        width=300
    )
    
    confirm_password_input = pn.widgets.PasswordInput(
        name="Confirm Password",
        placeholder="Confirm your password",
        width=300
    )
    
    # Messages
    message_pane = pn.pane.Alert(
        "", 
        alert_type="danger", 
        visible=False,
        width=300
    )
    
    def update_message(event=None):
        if auth_state.error_message:
            message_pane.object = auth_state.error_message
            message_pane.alert_type = "danger"
            message_pane.visible = True
        elif auth_state.success_message:
            message_pane.object = auth_state.success_message
            message_pane.alert_type = "success"
            message_pane.visible = True
        else:
            message_pane.visible = False
    
    auth_state.param.watch(update_message, ["error_message", "success_message"])
    
    # Register button
    def on_register(event):
        message_pane.visible = False
        success = auth_state.register(
            username_input.value,
            email_input.value,
            password_input.value,
            confirm_password_input.value
        )
        update_message()
    
    register_btn = pn.widgets.Button(
        name="Register",
        button_type="primary",
        width=300
    )
    register_btn.on_click(on_register)
    
    # Login link
    login_link = pn.pane.Markdown(
        "Already have an account? [Login here](#login)",
        width=300
    )
    
    # Layout
    register_form = pn.Column(
        pn.pane.Markdown("# 🤖 Create Account", styles={"text-align": "center"}),
        pn.layout.Spacer(height=20),
        message_pane,
        username_input,
        email_input,
        password_input,
        confirm_password_input,
        register_btn,
        pn.layout.Spacer(height=10),
        login_link,
        styles={
            "background": "white",
            "border-radius": "10px",
            "padding": "40px",
            "box-shadow": "0 2px 10px rgba(0,0,0,0.1)"
        },
        width=400
    )
    
    return pn.Column(
        register_form,
        styles={
            "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "min-height": "100vh"
        },
        align="center",
        sizing_mode="stretch_both"
    )
