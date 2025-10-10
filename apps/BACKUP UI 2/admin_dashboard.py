"""
Admin dashboard and management pages
"""
import panel as pn
import param
from datetime import datetime
from models import (
    get_session, User, AIProvider, AIModel, AIType, 
    ChatHistory, UsageLog, SystemPrompt, Project
)
from auth import AuthState

pn.extension(design="material", notifications=True)

def create_stat_card(title: str, value: str, icon: str, color: str = "primary"):
    """Create a statistics card"""
    return pn.Card(
        pn.Column(
            pn.pane.Markdown(f"## {icon} {value}", styles={"text-align": "center", "margin": "0"}),
            pn.pane.Markdown(f"**{title}**", styles={"text-align": "center", "color": "#666"}),
        ),
        styles={
            "background": f"linear-gradient(135deg, {'#667eea' if color == 'primary' else '#f093fb'} 0%, {'#764ba2' if color == 'primary' else '#f5576c'} 100%)",
            "color": "white",
            "border": "none"
        },
        height=150,
        width=250
    )

def create_admin_overview(auth_state: AuthState):
    """Create admin dashboard overview"""
    
    # Get statistics
    db = get_session()
    try:
        total_users = db.query(User).count()
        total_chats = db.query(ChatHistory).count()
        total_providers = db.query(AIProvider).count()
        total_models = db.query(AIModel).count()
        
        # Token usage
        usage_logs = db.query(UsageLog).all()
        total_tokens = sum(log.total_tokens for log in usage_logs)
        
    finally:
        db.close()
    
    # Statistics cards
    stats_row = pn.Row(
        create_stat_card("Total Users", str(total_users), "👥", "primary"),
        create_stat_card("Total Chats", str(total_chats), "💬", "primary"),
        create_stat_card("AI Providers", str(total_providers), "🤖", "secondary"),
        create_stat_card("AI Models", str(total_models), "🧠", "secondary"),
        create_stat_card("Total Tokens", f"{total_tokens:,}", "🎯", "primary"),
        scroll=True
    )
    
    # Recent activity
    recent_activity = pn.pane.Markdown("""
### 📊 Recent Activity
- System is running smoothly
- All services operational
- Database connected
    """)
    
    return pn.Column(
        pn.pane.Markdown("# 🎛️ Admin Dashboard", styles={"margin-bottom": "20px"}),
        stats_row,
        pn.layout.Spacer(height=30),
        recent_activity,
        sizing_mode="stretch_width"
    )

def create_provider_management(auth_state: AuthState):
    """Create AI provider management page"""
    
    # State for form
    class ProviderFormState(param.Parameterized):
        provider_id = param.Integer(default=None)
        name = param.String(default="")
        ai_type_id = param.Integer(default=1)
        api_url = param.String(default="")
        api_key = param.String(default="")
        is_active = param.Boolean(default=True)
        mode = param.String(default="list")  # list, create, edit
    
    form_state = ProviderFormState()
    
    # Get AI types for dropdown
    db = get_session()
    ai_types = db.query(AIType).all()
    ai_type_options = {at.name: at.id for at in ai_types}
    db.close()
    
    # Form inputs
    name_input = pn.widgets.TextInput(name="Provider Name", width=300)
    ai_type_select = pn.widgets.Select(
        name="AI Type",
        options=ai_type_options,
        width=300
    )
    api_url_input = pn.widgets.TextInput(name="API URL", width=300)
    api_key_input = pn.widgets.PasswordInput(name="API Key (optional)", width=300)
    is_active_toggle = pn.widgets.Checkbox(name="Active", value=True)
    
    # Providers table
    def get_providers_data():
        db = get_session()
        try:
            providers = db.query(AIProvider).all()
            data = []
            for p in providers:
                data.append({
                    "ID": p.id,
                    "Name": p.name,
                    "Type": p.ai_type.name if p.ai_type else "N/A",
                    "API URL": p.api_url,
                    "Active": "✅" if p.is_active else "❌",
                    "Created": p.created_at.strftime("%Y-%m-%d %H:%M")
                })
            return data
        finally:
            db.close()
    
    providers_table = pn.widgets.Tabulator(
        value=get_providers_data(),
        pagination="local",
        page_size=10,
        sizing_mode="stretch_width",
        height=400
    )
    
    # Form container
    form_container = pn.Column(visible=False)
    
    def show_create_form(event=None):
        form_state.mode = "create"
        form_state.provider_id = None
        name_input.value = ""
        api_url_input.value = ""
        api_key_input.value = ""
        is_active_toggle.value = True
        form_container.visible = True
        providers_table.visible = False
    
    def show_list(event=None):
        form_state.mode = "list"
        form_container.visible = False
        providers_table.visible = True
        providers_table.value = get_providers_data()
    
    def save_provider(event=None):
        db = get_session()
        try:
            if form_state.mode == "create":
                provider = AIProvider(
                    name=name_input.value,
                    ai_type_id=ai_type_select.value,
                    api_url=api_url_input.value,
                    api_key=api_key_input.value if api_key_input.value else None,
                    is_active=is_active_toggle.value
                )
                db.add(provider)
                db.commit()
                pn.state.notifications.success(f"Provider '{name_input.value}' created!")
            
            show_list()
        except Exception as e:
            db.rollback()
            pn.state.notifications.error(f"Error: {str(e)}")
        finally:
            db.close()
    
    # Buttons
    create_btn = pn.widgets.Button(
        name="➕ New Provider",
        button_type="primary",
        width=150
    )
    create_btn.on_click(show_create_form)
    
    save_btn = pn.widgets.Button(
        name="💾 Save",
        button_type="success",
        width=120
    )
    save_btn.on_click(save_provider)
    
    cancel_btn = pn.widgets.Button(
        name="❌ Cancel",
        button_type="warning",
        width=120
    )
    cancel_btn.on_click(show_list)
    
    # Form layout
    form_container.extend([
        pn.pane.Markdown("### Create New Provider"),
        name_input,
        ai_type_select,
        api_url_input,
        api_key_input,
        is_active_toggle,
        pn.Row(save_btn, cancel_btn)
    ])
    
    return pn.Column(
        pn.pane.Markdown("# 🤖 AI Provider Management"),
        pn.Row(create_btn),
        pn.layout.Spacer(height=20),
        providers_table,
        form_container,
        sizing_mode="stretch_width"
    )

def create_model_management(auth_state: AuthState):
    """Create AI model management page"""
    
    # Get models data
    def get_models_data():
        db = get_session()
        try:
            models = db.query(AIModel).all()
            data = []
            for m in models:
                data.append({
                    "ID": m.id,
                    "Name": m.name,
                    "Model ID": m.model_id,
                    "Provider": m.provider.name if m.provider else "N/A",
                    "Context": m.context_window,
                    "Max Tokens": m.max_tokens,
                    "Active": "✅" if m.is_active else "❌"
                })
            return data
        finally:
            db.close()
    
    models_table = pn.widgets.Tabulator(
        value=get_models_data(),
        pagination="local",
        page_size=10,
        sizing_mode="stretch_width",
        height=400
    )
    
    refresh_btn = pn.widgets.Button(
        name="🔄 Refresh",
        button_type="primary",
        width=120
    )
    
    def refresh_table(event):
        models_table.value = get_models_data()
    
    refresh_btn.on_click(refresh_table)
    
    return pn.Column(
        pn.pane.Markdown("# 🧠 AI Model Management"),
        pn.Row(refresh_btn),
        pn.layout.Spacer(height=20),
        models_table,
        sizing_mode="stretch_width"
    )

def create_users_management(auth_state: AuthState):
    """Create users management page"""
    
    def get_users_data():
        db = get_session()
        try:
            users = db.query(User).all()
            data = []
            for u in users:
                data.append({
                    "ID": u.id,
                    "Username": u.username,
                    "Email": u.email,
                    "Role": u.role.value.upper(),
                    "Active": "✅" if u.is_active else "❌",
                    "Created": u.created_at.strftime("%Y-%m-%d")
                })
            return data
        finally:
            db.close()
    
    users_table = pn.widgets.Tabulator(
        value=get_users_data(),
        pagination="local",
        page_size=15,
        sizing_mode="stretch_width",
        height=500
    )
    
    return pn.Column(
        pn.pane.Markdown("# 👥 Users Management"),
        pn.layout.Spacer(height=20),
        users_table,
        sizing_mode="stretch_width"
    )

def create_prompts_library(auth_state: AuthState):
    """Create system prompts library"""
    
    def get_prompts_data():
        db = get_session()
        try:
            prompts = db.query(SystemPrompt).all()
            cards = []
            for p in prompts:
                visibility = "🌍 Public" if p.is_public else "🔒 Private"
                tags = p.tags if p.tags else "No tags"
                
                card = pn.Card(
                    pn.pane.Markdown(f"**{p.name}**\n\n{p.description}"),
                    pn.pane.Markdown(f"*Tags: {tags}*"),
                    pn.pane.Markdown(f"*{visibility}*"),
                    title=f"📝 {p.name}",
                    collapsible=True,
                    width=350,
                    styles={"margin": "10px"}
                )
                cards.append(card)
            return cards
        finally:
            db.close()
    
    prompts_grid = pn.GridBox(*get_prompts_data(), ncols=3, sizing_mode="stretch_width")
    
    return pn.Column(
        pn.pane.Markdown("# 📝 System Prompts Library"),
        pn.layout.Spacer(height=20),
        prompts_grid,
        sizing_mode="stretch_width"
    )

def create_usage_monitoring(auth_state: AuthState):
    """Create usage monitoring page"""
    
    db = get_session()
    try:
        # Calculate statistics
        usage_logs = db.query(UsageLog).all()
        total_tokens = sum(log.total_tokens for log in usage_logs)
        total_cost = sum(log.cost for log in usage_logs)
        total_conversations = db.query(ChatHistory).count()
        
    finally:
        db.close()
    
    stats = pn.Row(
        create_stat_card("Total Tokens", f"{total_tokens:,}", "🎯", "primary"),
        create_stat_card("Total Cost", f"${total_cost:.2f}", "💰", "secondary"),
        create_stat_card("Conversations", str(total_conversations), "💬", "primary"),
    )
    
    return pn.Column(
        pn.pane.Markdown("# 📊 Usage Monitoring"),
        pn.layout.Spacer(height=20),
        stats,
        pn.layout.Spacer(height=30),
        pn.pane.Markdown("### Usage History\n*Coming soon: Detailed usage charts and analytics*"),
        sizing_mode="stretch_width"
    )

def create_admin_dashboard(auth_state: AuthState):
    """Create complete admin dashboard with tabs"""
    
    # Create tabs for different admin sections
    tabs = pn.Tabs(
        ("📊 Overview", create_admin_overview(auth_state)),
        ("🤖 Providers", create_provider_management(auth_state)),
        ("🧠 Models", create_model_management(auth_state)),
        ("👥 Users", create_users_management(auth_state)),
        ("📝 Prompts", create_prompts_library(auth_state)),
        ("📈 Usage", create_usage_monitoring(auth_state)),
        dynamic=True,
        sizing_mode="stretch_width"
    )
    
    return tabs
