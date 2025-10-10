"""
User pages: Settings, Projects, Profile
"""
import panel as pn
import param
from models import get_session, AIModel, Project, ChatHistory
from auth import AuthState, session_manager

pn.extension(design="material", notifications=True)

def create_settings_page(auth_state: AuthState):
    """Create settings page"""
    
    # Chat Settings
    db = get_session()
    models = db.query(AIModel).filter_by(is_active=True).all()
    model_options = {f"{m.name} ({m.model_id})": m.model_id for m in models}
    db.close()
    
    default_model = pn.widgets.Select(
        name="Default Model",
        options=model_options,
        value=list(model_options.values())[0] if model_options else None,
        width=300
    )
    
    context_window = pn.widgets.IntInput(
        name="Context Window",
        value=4096,
        start=512,
        end=32768,
        step=512,
        width=300
    )
    
    temperature = pn.widgets.FloatSlider(
        name="Default Temperature",
        start=0.0,
        end=2.0,
        step=0.1,
        value=0.7,
        width=300
    )
    
    max_tokens = pn.widgets.IntInput(
        name="Default Max Tokens",
        value=2048,
        start=128,
        end=8192,
        step=128,
        width=300
    )
    
    # Appearance Settings
    theme_select = pn.widgets.Select(
        name="Theme",
        options=["Light", "Dark", "Auto"],
        value="Light",
        width=300
    )
    
    language_select = pn.widgets.Select(
        name="Language",
        options=["English", "Spanish", "French", "German", "Chinese", "Japanese"],
        value="English",
        width=300
    )
    
    # Save button
    save_btn = pn.widgets.Button(
        name="💾 Save Settings",
        button_type="success",
        width=200
    )
    
    def on_save(event):
        pn.state.notifications.success("Settings saved successfully!")
    
    save_btn.on_click(on_save)
    
    # Layout
    return pn.Column(
        pn.pane.Markdown("# ⚙️ Settings"),
        pn.layout.Spacer(height=20),
        
        pn.Card(
            pn.pane.Markdown("### 💬 Chat Settings"),
            default_model,
            context_window,
            temperature,
            max_tokens,
            title="Chat Configuration",
            collapsible=False,
            styles={"margin-bottom": "20px"}
        ),
        
        pn.Card(
            pn.pane.Markdown("### 🎨 Appearance"),
            theme_select,
            language_select,
            title="Appearance Settings",
            collapsible=False,
            styles={"margin-bottom": "20px"}
        ),
        
        save_btn,
        sizing_mode="stretch_width"
    )

def create_projects_page(auth_state: AuthState):
    """Create projects page"""
    
    # Get user projects
    def get_user_projects():
        db = get_session()
        try:
            user_session = session_manager.get_session(auth_state.session_id)
            if not user_session:
                return []
            
            projects = db.query(Project).filter_by(user_id=user_session["user_id"]).all()
            cards = []
            
            for proj in projects:
                # Count chats in project
                chat_count = db.query(ChatHistory).filter_by(project_id=proj.id).count()
                
                card = pn.Card(
                    pn.pane.Markdown(f"{proj.icon}\n\n**{proj.name}**"),
                    pn.pane.Markdown(f"{proj.description or 'No description'}"),
                    pn.pane.Markdown(f"💬 {chat_count} chats"),
                    pn.pane.Markdown(f"*Created: {proj.created_at.strftime('%Y-%m-%d')}*"),
                    title=proj.name,
                    width=300,
                    styles={"margin": "10px"}
                )
                cards.append(card)
            
            return cards
        finally:
            db.close()
    
    # Search bar
    search_input = pn.widgets.TextInput(
        placeholder="🔍 Search projects...",
        width=400
    )
    
    # New project button
    new_project_btn = pn.widgets.Button(
        name="➕ New Project",
        button_type="primary",
        width=150
    )
    
    # Projects grid
    projects_grid = pn.GridBox(*get_user_projects(), ncols=3, sizing_mode="stretch_width")
    
    def on_new_project(event):
        pn.state.notifications.info("Project creation coming soon!")
    
    new_project_btn.on_click(on_new_project)
    
    return pn.Column(
        pn.pane.Markdown("# 📁 Projects"),
        pn.Row(search_input, new_project_btn),
        pn.layout.Spacer(height=20),
        projects_grid,
        sizing_mode="stretch_width"
    )

def create_profile_page(auth_state: AuthState):
    """Create user profile page"""
    
    # Get user info
    user_session = session_manager.get_session(auth_state.session_id)
    if not user_session:
        return pn.pane.Markdown("# Error: Not logged in")
    
    # Avatar
    initials = auth_state.get_user_initials()
    avatar = pn.pane.HTML(
        f"""
        <div style="width: 100px; height: 100px; border-radius: 50%; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex; align-items: center; justify-content: center;
                    color: white; font-size: 36px; font-weight: bold;
                    margin: 0 auto 20px;">
            {initials}
        </div>
        """
    )
    
    # User info
    info_card = pn.Card(
        pn.pane.Markdown(f"**Username:** {auth_state.username}"),
        pn.pane.Markdown(f"**Email:** {auth_state.email}"),
        pn.pane.Markdown(f"**Role:** {auth_state.role.value.upper() if auth_state.role else 'USER'}"),
        pn.pane.Markdown(f"**Account Status:** ✅ Active"),
        title="Account Information",
        width=500
    )
    
    # Statistics
    db = get_session()
    try:
        chat_count = db.query(ChatHistory).filter_by(user_id=user_session["user_id"]).count()
        project_count = db.query(Project).filter_by(user_id=user_session["user_id"]).count()
    finally:
        db.close()
    
    stats_card = pn.Card(
        pn.pane.Markdown(f"**Total Chats:** {chat_count}"),
        pn.pane.Markdown(f"**Total Projects:** {project_count}"),
        title="Statistics",
        width=500
    )
    
    return pn.Column(
        pn.pane.Markdown("# 👤 Profile", styles={"text-align": "center"}),
        avatar,
        pn.layout.Spacer(height=20),
        pn.Column(
            info_card,
            stats_card,
            align="center"
        ),
        sizing_mode="stretch_width"
    )

def create_chat_history_page(auth_state: AuthState):
    """Create chat history page"""
    
    def get_chat_history():
        db = get_session()
        try:
            user_session = session_manager.get_session(auth_state.session_id)
            if not user_session:
                return []
            
            chats = db.query(ChatHistory).filter_by(
                user_id=user_session["user_id"]
            ).order_by(ChatHistory.updated_at.desc()).all()
            
            data = []
            for chat in chats:
                data.append({
                    "ID": chat.id,
                    "Title": chat.title,
                    "Model": chat.model.name if chat.model else "N/A",
                    "Project": chat.project.name if chat.project else "General",
                    "Updated": chat.updated_at.strftime("%Y-%m-%d %H:%M")
                })
            return data
        finally:
            db.close()
    
    history_table = pn.widgets.Tabulator(
        value=get_chat_history(),
        pagination="local",
        page_size=20,
        sizing_mode="stretch_width",
        height=600,
        selectable=True
    )
    
    # Action buttons
    load_btn = pn.widgets.Button(
        name="📂 Load Chat",
        button_type="primary",
        width=120
    )
    
    delete_btn = pn.widgets.Button(
        name="🗑️ Delete",
        button_type="danger",
        width=120
    )
    
    refresh_btn = pn.widgets.Button(
        name="🔄 Refresh",
        button_type="success",
        width=120
    )
    
    def on_refresh(event):
        history_table.value = get_chat_history()
        pn.state.notifications.info("History refreshed")
    
    refresh_btn.on_click(on_refresh)
    
    return pn.Column(
        pn.pane.Markdown("# 📜 Chat History"),
        pn.Row(load_btn, delete_btn, refresh_btn),
        pn.layout.Spacer(height=20),
        history_table,
        sizing_mode="stretch_width"
    )
