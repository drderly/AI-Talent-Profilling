"""
Main LLM UI Application
Pure Python UI using Panel (HoloViz)
"""
import panel as pn
import param
from auth import AuthState, create_login_page, create_register_page
from chat_interface import create_chat_interface
from admin_dashboard import create_admin_dashboard
from user_pages import (
    create_settings_page,
    create_projects_page,
    create_profile_page,
    create_chat_history_page
)
from models import init_db, get_session, seed_data

# Initialize Panel with Material Design
pn.extension(
    design="material",
    notifications=True,
    tabulator=True,
    loading_spinner="dots",
    template="material"
)

class AppState(param.Parameterized):
    """Application state management"""
    
    current_page = param.String(default="login")
    auth_state = param.Parameter(default=None)
    
    def __init__(self, **params):
        super().__init__(**params)
        self.auth_state = AuthState()

def create_sidebar(app_state: AppState):
    """Create navigation sidebar"""
    
    auth_state = app_state.auth_state
    
    # User info section
    user_avatar = pn.pane.HTML(
        f"""
        <div style="width: 60px; height: 60px; border-radius: 50%; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex; align-items: center; justify-content: center;
                    color: white; font-size: 24px; font-weight: bold;
                    margin: 0 auto 10px;">
            {auth_state.get_user_initials()}
        </div>
        """,
        width=80,
        height=80,
        align="center"
    )
    
    user_info = pn.Column(
        user_avatar,
        pn.pane.Markdown(
            f"**{auth_state.username}**",
            styles={"text-align": "center", "margin": "0"}
        ),
        pn.pane.Markdown(
            f"*{auth_state.role.value.title() if auth_state.role else 'User'}*",
            styles={"text-align": "center", "color": "#666", "margin": "0"}
        ),
        styles={
            "background": "#f8f9fa",
            "padding": "20px",
            "border-radius": "8px",
            "margin-bottom": "20px"
        }
    )
    
    # Navigation buttons
    nav_buttons = []
    
    # Common navigation
    common_nav = [
        ("💬 Chat", "chat"),
        ("📜 History", "history"),
        ("📁 Projects", "projects"),
        ("📝 Prompts", "prompts"),
        ("⚙️ Settings", "settings"),
        ("👤 Profile", "profile"),
    ]
    
    for label, page in common_nav:
        btn = pn.widgets.Button(
            name=label,
            button_type="light",
            width=200,
            styles={"text-align": "left", "margin-bottom": "8px"}
        )
        btn.param.watch(lambda event, p=page: setattr(app_state, "current_page", p), "clicks")
        nav_buttons.append(btn)
    
    # Admin navigation
    if auth_state.is_admin():
        admin_divider = pn.pane.Markdown("---\n**Admin**", styles={"margin": "20px 0"})
        nav_buttons.append(admin_divider)
        
        admin_btn = pn.widgets.Button(
            name="🎛️ Admin Dashboard",
            button_type="warning",
            width=200,
            styles={"margin-bottom": "8px"}
        )
        admin_btn.param.watch(lambda event: setattr(app_state, "current_page", "admin"), "clicks")
        nav_buttons.append(admin_btn)
    
    # Logout button
    logout_btn = pn.widgets.Button(
        name="🚪 Logout",
        button_type="danger",
        width=200,
        styles={"margin-top": "20px"}
    )
    
    def on_logout(event):
        auth_state.logout()
        app_state.current_page = "login"
    
    logout_btn.on_click(on_logout)
    
    # Sidebar layout
    sidebar = pn.Column(
        pn.pane.Markdown(
            "# 🤖 LLM UI",
            styles={"text-align": "center", "margin-bottom": "20px"}
        ),
        user_info,
        *nav_buttons,
        logout_btn,
        styles={
            "background": "white",
            "padding": "20px",
            "border-right": "1px solid #e0e0e0",
            "min-height": "100vh"
        },
        width=280,
        scroll=True
    )
    
    return sidebar

def create_main_content(app_state: AppState):
    """Create main content area"""
    
    auth_state = app_state.auth_state
    
    # Content container
    content = pn.Column(
        sizing_mode="stretch_both",
        styles={"padding": "20px", "background": "#f5f5f5"}
    )
    
    def update_content(event=None):
        content.clear()
        
        page = app_state.current_page
        
        if page == "chat":
            content.append(create_chat_interface(auth_state))
        elif page == "history":
            content.append(create_chat_history_page(auth_state))
        elif page == "projects":
            content.append(create_projects_page(auth_state))
        elif page == "prompts":
            from admin_dashboard import create_prompts_library
            content.append(create_prompts_library(auth_state))
        elif page == "settings":
            content.append(create_settings_page(auth_state))
        elif page == "profile":
            content.append(create_profile_page(auth_state))
        elif page == "admin" and auth_state.is_admin():
            content.append(create_admin_dashboard(auth_state))
        else:
            content.append(pn.pane.Markdown("# Welcome to LLM UI\n\nSelect a page from the sidebar."))
    
    # Watch for page changes
    app_state.param.watch(update_content, "current_page")
    
    # Initial content
    update_content()
    
    return content

def create_app_layout(app_state: AppState):
    """Create main application layout"""
    
    sidebar = create_sidebar(app_state)
    content = create_main_content(app_state)
    
    layout = pn.Row(
        sidebar,
        content,
        sizing_mode="stretch_both"
    )
    
    return layout

def create_auth_layout(app_state: AppState):
    """Create authentication layout"""
    
    auth_state = app_state.auth_state
    
    # Content container
    content = pn.Column(sizing_mode="stretch_both")
    
    def update_auth_page(event=None):
        content.clear()
        
        if app_state.current_page == "login":
            content.append(create_login_page(auth_state))
        elif app_state.current_page == "register":
            content.append(create_register_page(auth_state))
    
    # Watch for page changes
    app_state.param.watch(update_auth_page, "current_page")
    
    # Initial page
    update_auth_page()
    
    # Handle login/register links
    def handle_hash_change(event=None):
        if pn.state.location:
            hash_value = pn.state.location.hash
            if hash_value == "#register":
                app_state.current_page = "register"
            elif hash_value == "#login":
                app_state.current_page = "login"
    
    if pn.state.location:
        pn.state.location.param.watch(handle_hash_change, "hash")
    
    return content

def main():
    """Main application entry point"""
    
    # Initialize database
    init_db()
    db = get_session()
    seed_data(db)
    db.close()
    
    # Create app state
    app_state = AppState()
    
    # Main container
    main_container = pn.Column(sizing_mode="stretch_both")
    
    def update_main_view(event=None):
        main_container.clear()
        
        if app_state.auth_state.is_authenticated:
            # Show main app
            if app_state.current_page in ["login", "register"]:
                app_state.current_page = "chat"
            main_container.append(create_app_layout(app_state))
        else:
            # Show auth pages
            if app_state.current_page not in ["login", "register"]:
                app_state.current_page = "login"
            main_container.append(create_auth_layout(app_state))
    
    # Watch for authentication changes
    app_state.auth_state.param.watch(update_main_view, "is_authenticated")
    
    # Initial view
    update_main_view()
    
    return main_container

# Create the app
app = main()

# For Panel serve
if __name__ == "__main__":
    pn.serve(
        {"/": app},
        title="LLM UI",
        port=5006,
        show=True,
        autoreload=True,
        websocket_origin="*",
        static_dirs={},
        admin=True
    )
elif __name__.startswith("bokeh"):
    # For Panel/Bokeh server
    app.servable()
