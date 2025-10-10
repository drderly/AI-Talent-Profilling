"""Main Reflex application."""
import reflex as rx
from .pages import auth, chat, admin, client


def index() -> rx.Component:
    """Home page with login/register options."""
    return rx.center(
        rx.vstack(
            rx.text("🤖", font_size="5em"),
            rx.heading("LLM Service Dashboard", size="9"),
            rx.text(
                "Manage your AI models and chat with advanced LLMs",
                size="4",
                color="gray",
            ),
            rx.hstack(
                rx.link(
                    rx.button("Sign In", size="4", color_scheme="blue"),
                    href="/login",
                ),
                rx.link(
                    rx.button("Sign Up", size="4", variant="outline"),
                    href="/register",
                ),
                spacing="4",
            ),
            spacing="6",
            align_items="center",
        ),
        height="100vh",
        background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    )


# Create app
app = rx.App()

# Home and auth routes
app.add_page(index, route="/")
app.add_page(auth.login_page, route="/login")
app.add_page(auth.register_page, route="/register")

# Client routes
app.add_page(chat.chat_page, route="/chat")
app.add_page(client.profile_page, route="/profile")
app.add_page(client.settings_page, route="/settings")
app.add_page(client.projects_page, route="/projects")
app.add_page(client.prompts_page, route="/prompts")
app.add_page(client.usage_page, route="/usage")
app.add_page(client.logs_page, route="/logs")

# Admin routes
app.add_page(admin.admin_dashboard, route="/admin/dashboard")
app.add_page(admin.admin_ai_providers, route="/admin/ai-providers")
app.add_page(admin.admin_ai_models, route="/admin/ai-models")
app.add_page(admin.admin_ai_types, route="/admin/ai-types")
app.add_page(admin.admin_media_providers, route="/admin/media-providers")
app.add_page(admin.admin_media_models, route="/admin/media-models")
app.add_page(admin.admin_media_types, route="/admin/media-types")
app.add_page(admin.admin_background_jobs, route="/admin/background-jobs")
app.add_page(admin.admin_api_keys, route="/admin/api-keys")
app.add_page(admin.admin_monitoring_logs, route="/admin/monitoring-logs")
app.add_page(admin.admin_performance_metrics, route="/admin/performance-metrics")
app.add_page(admin.admin_usage_logs, route="/admin/usage-logs")
