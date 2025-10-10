"""Admin pages."""
import reflex as rx
from ..components.sidebar import admin_sidebar
from ..states.admin_state import AdminDashboardState, AIProviderState, AIModelState
from ..models import AIProvider, AIModel


def admin_layout(content: rx.Component) -> rx.Component:
    """Admin layout wrapper with sidebar."""
    return rx.hstack(
        admin_sidebar(),
        rx.box(
            content,
            margin_left="250px",
            width="calc(100% - 250px)",
            padding="2em",
            height="100vh",
            overflow_y="auto",
        ),
        width="100%",
        height="100vh",
        spacing="0",
    )


def admin_dashboard() -> rx.Component:
    """Admin dashboard page."""
    return admin_layout(
        rx.vstack(
            rx.heading("Dashboard", size="8"),
            
            # Statistics cards
            rx.grid(
                rx.card(
                    rx.vstack(
                        rx.text("👥", font_size="3em"),
                        rx.heading(AdminDashboardState.total_users, size="7"),
                        rx.text("Total Users", color="gray"),
                        align_items="center",
                    ),
                ),
                rx.card(
                    rx.vstack(
                        rx.text("💬", font_size="3em"),
                        rx.heading(AdminDashboardState.total_chats, size="7"),
                        rx.text("Total Chats", color="gray"),
                        align_items="center",
                    ),
                ),
                rx.card(
                    rx.vstack(
                        rx.text("🔄", font_size="3em"),
                        rx.heading(AdminDashboardState.total_api_calls, size="7"),
                        rx.text("API Calls", color="gray"),
                        align_items="center",
                    ),
                ),
                rx.card(
                    rx.vstack(
                        rx.text("🎯", font_size="3em"),
                        rx.heading(AdminDashboardState.total_tokens, size="7"),
                        rx.text("Total Tokens", color="gray"),
                        align_items="center",
                    ),
                ),
                columns="4",
                spacing="4",
                width="100%",
            ),
            
            # Recent activity
            rx.card(
                rx.vstack(
                    rx.heading("Recent Activity", size="6"),
                    rx.text("Recent logs and system events will appear here", color="gray"),
                    width="100%",
                    align_items="flex-start",
                ),
            ),
            
            width="100%",
            spacing="6",
            align_items="flex-start",
        ),
    )


def admin_ai_providers() -> rx.Component:
    """AI Providers management page."""
    return admin_layout(
        rx.vstack(
            rx.heading("AI Providers", size="8"),
            
            # Success/Error messages
            rx.cond(
                AIProviderState.error_message != "",
                rx.callout(
                    AIProviderState.error_message,
                    icon="triangle-alert",
                    color_scheme="red",
                ),
            ),
            rx.cond(
                AIProviderState.success_message != "",
                rx.callout(
                    AIProviderState.success_message,
                    icon="check",
                    color_scheme="green",
                ),
            ),
            
            # Form
            rx.card(
                rx.vstack(
                    rx.heading("Add/Edit Provider", size="5"),
                    rx.grid(
                        rx.vstack(
                            rx.text("Name", weight="bold"),
                            rx.input(
                                placeholder="Provider name",
                                value=AIProviderState.form_name,
                                on_change=AIProviderState.set_form_name,
                                width="100%",
                            ),
                            width="100%",
                            align_items="flex-start",
                        ),
                        rx.vstack(
                            rx.text("API URL", weight="bold"),
                            rx.input(
                                placeholder="http://localhost:11434",
                                value=AIProviderState.form_api_url,
                                on_change=AIProviderState.set_form_api_url,
                                width="100%",
                            ),
                            width="100%",
                            align_items="flex-start",
                        ),
                        rx.vstack(
                            rx.text("API Key (Optional)", weight="bold"),
                            rx.input(
                                placeholder="API Key",
                                type="password",
                                value=AIProviderState.form_api_key,
                                on_change=AIProviderState.set_form_api_key,
                                width="100%",
                            ),
                            width="100%",
                            align_items="flex-start",
                        ),
                        rx.vstack(
                            rx.text("Provider Type", weight="bold"),
                            rx.select(
                                ["ollama", "openai", "anthropic", "google", "huggingface"],
                                value=AIProviderState.form_provider_type,
                                on_change=AIProviderState.set_form_provider_type,
                                width="100%",
                            ),
                            width="100%",
                            align_items="flex-start",
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.button(
                            "Save Provider",
                            on_click=AIProviderState.save_provider,
                            color_scheme="blue",
                        ),
                        rx.button(
                            "Clear",
                            on_click=AIProviderState.clear_form,
                            variant="outline",
                        ),
                    ),
                    width="100%",
                    align_items="flex-start",
                    spacing="4",
                ),
            ),
            
            # Providers list
            rx.card(
                rx.vstack(
                    rx.heading("Existing Providers", size="5"),
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Name"),
                                rx.table.column_header_cell("Type"),
                                rx.table.column_header_cell("API URL"),
                                rx.table.column_header_cell("Status"),
                                rx.table.column_header_cell("Actions"),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(
                                AIProviderState.providers,
                                lambda provider: rx.table.row(
                                    rx.table.cell(provider.name),
                                    rx.table.cell(provider.provider_type),
                                    rx.table.cell(provider.api_url),
                                    rx.table.cell(
                                        rx.badge(
                                            rx.cond(provider.is_active, "Active", "Inactive"),
                                            color_scheme=rx.cond(provider.is_active, "green", "gray"),
                                        ),
                                    ),
                                    rx.table.cell(
                                        rx.hstack(
                                            rx.icon_button(
                                                rx.icon("edit"),
                                                on_click=lambda: AIProviderState.edit_provider(provider.id),
                                                size="1",
                                                variant="ghost",
                                            ),
                                            rx.icon_button(
                                                rx.icon("trash-2"),
                                                on_click=lambda: AIProviderState.delete_provider(provider.id),
                                                size="1",
                                                variant="ghost",
                                                color_scheme="red",
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    width="100%",
                    align_items="flex-start",
                    spacing="4",
                ),
            ),
            
            width="100%",
            spacing="6",
            align_items="flex-start",
        ),
    )


def admin_ai_models() -> rx.Component:
    """AI Models management page."""
    return admin_layout(
        rx.vstack(
            rx.heading("AI Models", size="8"),
            
            rx.card(
                rx.vstack(
                    rx.heading("Model Configuration", size="5"),
                    rx.text("Manage AI models and their configurations", color="gray"),
                    rx.button(
                        "Load Models",
                        on_click=AIModelState.load_models,
                        color_scheme="blue",
                    ),
                    width="100%",
                    align_items="flex-start",
                ),
            ),
            
            # Models list (simplified)
            rx.card(
                rx.vstack(
                    rx.heading("Existing Models", size="5"),
                    rx.text("Model management interface", color="gray"),
                    width="100%",
                    align_items="flex-start",
                ),
            ),
            
            width="100%",
            spacing="6",
            align_items="flex-start",
        ),
    )


def admin_ai_types() -> rx.Component:
    """AI Types management page."""
    return admin_layout(
        rx.vstack(
            rx.heading("AI Types", size="8"),
            rx.card(
                rx.text("Manage AI types and categories"),
            ),
            width="100%",
            spacing="6",
        ),
    )


def admin_media_providers() -> rx.Component:
    """Media Providers management page."""
    return admin_layout(
        rx.vstack(
            rx.heading("Media Providers", size="8"),
            rx.card(
                rx.text("Manage media generation providers (Stable Diffusion, DALL-E, etc.)"),
            ),
            width="100%",
            spacing="6",
        ),
    )


def admin_media_models() -> rx.Component:
    """Media Models management page."""
    return admin_layout(
        rx.vstack(
            rx.heading("Media Models", size="8"),
            rx.card(
                rx.text("Manage media generation models"),
            ),
            width="100%",
            spacing="6",
        ),
    )


def admin_media_types() -> rx.Component:
    """Media Types management page."""
    return admin_layout(
        rx.vstack(
            rx.heading("Media Types", size="8"),
            rx.card(
                rx.text("Manage media types and categories"),
            ),
            width="100%",
            spacing="6",
        ),
    )


def admin_background_jobs() -> rx.Component:
    """Background Jobs management page."""
    return admin_layout(
        rx.vstack(
            rx.heading("Background Jobs", size="8"),
            rx.card(
                rx.text("Monitor and manage background tasks"),
            ),
            width="100%",
            spacing="6",
        ),
    )


def admin_api_keys() -> rx.Component:
    """API Keys management page."""
    return admin_layout(
        rx.vstack(
            rx.heading("API Keys", size="8"),
            rx.card(
                rx.text("Manage API keys for users"),
            ),
            width="100%",
            spacing="6",
        ),
    )


def admin_monitoring_logs() -> rx.Component:
    """Monitoring Logs page."""
    return admin_layout(
        rx.vstack(
            rx.heading("Monitoring Logs", size="8"),
            rx.card(
                rx.text("View system logs and monitoring events"),
            ),
            width="100%",
            spacing="6",
        ),
    )


def admin_performance_metrics() -> rx.Component:
    """Performance Metrics page."""
    return admin_layout(
        rx.vstack(
            rx.heading("Performance Metrics", size="8"),
            rx.card(
                rx.text("View system performance metrics and analytics"),
            ),
            width="100%",
            spacing="6",
        ),
    )


def admin_usage_logs() -> rx.Component:
    """Usage Logs page."""
    return admin_layout(
        rx.vstack(
            rx.heading("Usage Logs", size="8"),
            rx.card(
                rx.text("View API usage logs and statistics"),
            ),
            width="100%",
            spacing="6",
        ),
    )
