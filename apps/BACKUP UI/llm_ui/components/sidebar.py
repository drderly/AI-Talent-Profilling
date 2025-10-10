"""Sidebar components for navigation."""
import reflex as rx
from ..auth import AuthState


def admin_sidebar_item(icon: str, text: str, href: str):
    """Create a sidebar menu item for admin."""
    return rx.link(
        rx.hstack(
            rx.text(icon, font_size="1.5em"),
            rx.text(text, font_size="1em"),
            padding="0.75em",
            border_radius="0.5em",
            _hover={"bg": "rgba(99, 102, 241, 0.1)", "cursor": "pointer"},
            width="100%",
        ),
        href=href,
        text_decoration="none",
        color="inherit",
        width="100%",
    )


def admin_sidebar() -> rx.Component:
    """Create admin sidebar navigation."""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.text("🤖", font_size="2em"),
                rx.text("Admin Panel", font_size="1.5em", font_weight="bold"),
                padding="1em",
                border_bottom="1px solid #e5e7eb",
                width="100%",
            ),
            
            # Navigation items
            rx.vstack(
                admin_sidebar_item("📊", "Dashboard", "/admin/dashboard"),
                admin_sidebar_item("🤖", "AI Providers", "/admin/ai-providers"),
                admin_sidebar_item("🧠", "AI Models", "/admin/ai-models"),
                admin_sidebar_item("📁", "AI Types", "/admin/ai-types"),
                admin_sidebar_item("🎨", "Media Providers", "/admin/media-providers"),
                admin_sidebar_item("🖼️", "Media Models", "/admin/media-models"),
                admin_sidebar_item("📋", "Media Types", "/admin/media-types"),
                admin_sidebar_item("⚙️", "Background Jobs", "/admin/background-jobs"),
                admin_sidebar_item("🔑", "API Keys", "/admin/api-keys"),
                admin_sidebar_item("📝", "Monitoring Logs", "/admin/monitoring-logs"),
                admin_sidebar_item("📈", "Performance Metrics", "/admin/performance-metrics"),
                admin_sidebar_item("📊", "Usage Logs", "/admin/usage-logs"),
                padding="1em",
                width="100%",
                spacing="2",
                align_items="flex-start",
            ),
            
            # Profile at bottom
            rx.spacer(),
            rx.divider(),
            rx.hstack(
                rx.avatar(
                    size="3",
                    fallback=rx.cond(
                        AuthState.username != "",
                        AuthState.username[0:2].upper(),
                        "U"
                    )
                ),
                rx.vstack(
                    rx.text(AuthState.username, font_weight="bold", font_size="0.9em"),
                    rx.text(AuthState.email, font_size="0.8em", color="gray"),
                    align_items="flex-start",
                    spacing="0",
                ),
                rx.spacer(),
                rx.icon_button(
                    rx.icon("log-out"),
                    on_click=AuthState.logout,
                    size="2",
                    variant="ghost",
                ),
                padding="1em",
                width="100%",
            ),
            
            width="100%",
            height="100vh",
            spacing="0",
            align_items="flex-start",
        ),
        width="250px",
        bg="#f9fafb",
        border_right="1px solid #e5e7eb",
        position="fixed",
        left="0",
        top="0",
        height="100vh",
        overflow_y="auto",
    )


def client_sidebar_item(icon: str, text: str, href: str):
    """Create a sidebar menu item for client."""
    return rx.link(
        rx.hstack(
            rx.text(icon, font_size="1.5em"),
            rx.text(text, font_size="1em"),
            padding="0.75em",
            border_radius="0.5em",
            _hover={"bg": "rgba(99, 102, 241, 0.1)", "cursor": "pointer"},
            width="100%",
        ),
        href=href,
        text_decoration="none",
        color="inherit",
        width="100%",
    )


def client_sidebar() -> rx.Component:
    """Create client sidebar navigation."""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.text("💬", font_size="2em"),
                rx.text("LLM Chat", font_size="1.5em", font_weight="bold"),
                padding="1em",
                border_bottom="1px solid #e5e7eb",
                width="100%",
            ),
            
            # Navigation items
            rx.vstack(
                client_sidebar_item("💬", "Chat", "/chat"),
                client_sidebar_item("📁", "Projects", "/projects"),
                client_sidebar_item("📝", "System Prompts", "/prompts"),
                client_sidebar_item("📊", "Usage", "/usage"),
                client_sidebar_item("📝", "Logs", "/logs"),
                client_sidebar_item("⚙️", "Settings", "/settings"),
                padding="1em",
                width="100%",
                spacing="2",
                align_items="flex-start",
            ),
            
            # Profile at bottom
            rx.spacer(),
            rx.divider(),
            rx.hstack(
                rx.avatar(
                    size="3",
                    fallback=rx.cond(
                        AuthState.username != "",
                        AuthState.username[0:2].upper(),
                        "U"
                    )
                ),
                rx.vstack(
                    rx.text(AuthState.username, font_weight="bold", font_size="0.9em"),
                    rx.text(AuthState.email, font_size="0.8em", color="gray"),
                    align_items="flex-start",
                    spacing="0",
                ),
                rx.spacer(),
                rx.icon_button(
                    rx.icon("log-out"),
                    on_click=AuthState.logout,
                    size="2",
                    variant="ghost",
                ),
                padding="1em",
                width="100%",
            ),
            
            width="100%",
            height="100vh",
            spacing="0",
            align_items="flex-start",
        ),
        width="250px",
        bg="#f9fafb",
        border_right="1px solid #e5e7eb",
        position="fixed",
        left="0",
        top="0",
        height="100vh",
        overflow_y="auto",
    )
