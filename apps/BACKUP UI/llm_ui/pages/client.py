"""Client pages."""
import reflex as rx
from ..components.sidebar import client_sidebar
from ..auth import AuthState


def client_layout(content: rx.Component) -> rx.Component:
    """Client layout wrapper with sidebar."""
    return rx.hstack(
        client_sidebar(),
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


def profile_page() -> rx.Component:
    """User profile page."""
    return client_layout(
        rx.vstack(
            rx.heading("Profile", size="8"),
            
            rx.card(
                rx.vstack(
                    rx.avatar(
                        size="9",
                        fallback=rx.cond(
                            AuthState.username != "",
                            AuthState.username[0:2].upper(),
                            "U"
                        ),
                    ),
                    rx.heading(AuthState.username, size="6"),
                    rx.text(AuthState.email, color="gray"),
                    align_items="center",
                    spacing="4",
                ),
            ),
            
            rx.card(
                rx.vstack(
                    rx.heading("Account Information", size="5"),
                    rx.grid(
                        rx.vstack(
                            rx.text("Username", weight="bold", size="2"),
                            rx.text(AuthState.username, size="3"),
                            align_items="flex-start",
                        ),
                        rx.vstack(
                            rx.text("Email", weight="bold", size="2"),
                            rx.text(AuthState.email, size="3"),
                            align_items="flex-start",
                        ),
                        rx.vstack(
                            rx.text("Role", weight="bold", size="2"),
                            rx.badge(
                                rx.cond(AuthState.is_admin, "Admin", "User"),
                                color_scheme=rx.cond(AuthState.is_admin, "purple", "blue"),
                            ),
                            align_items="flex-start",
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
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


def settings_page() -> rx.Component:
    """Settings page."""
    return client_layout(
        rx.vstack(
            rx.heading("Settings", size="8"),
            
            rx.card(
                rx.vstack(
                    rx.heading("Chat Settings", size="5"),
                    rx.vstack(
                        rx.hstack(
                            rx.text("Default Model", weight="bold"),
                            rx.select(
                                ["smollm2:1.7b", "mistral:7b-instruct", "llama3:8b-instruct"],
                                default_value="smollm2:1.7b",
                                width="300px",
                            ),
                            width="100%",
                            justify="between",
                        ),
                        rx.hstack(
                            rx.text("Context Window", weight="bold"),
                            rx.input(
                                type="number",
                                default_value="4096",
                                width="300px",
                            ),
                            width="100%",
                            justify="between",
                        ),
                        rx.hstack(
                            rx.text("Temperature", weight="bold"),
                            rx.slider(
                                default_value=[0.7],
                                min=0,
                                max=2,
                                step=0.1,
                                width="300px",
                            ),
                            width="100%",
                            justify="between",
                        ),
                        rx.hstack(
                            rx.text("Max Tokens", weight="bold"),
                            rx.input(
                                type="number",
                                default_value="2048",
                                width="300px",
                            ),
                            width="100%",
                            justify="between",
                        ),
                        width="100%",
                        spacing="4",
                    ),
                    rx.button(
                        "Save Settings",
                        color_scheme="blue",
                    ),
                    width="100%",
                    align_items="flex-start",
                    spacing="4",
                ),
            ),
            
            rx.card(
                rx.vstack(
                    rx.heading("Appearance", size="5"),
                    rx.hstack(
                        rx.text("Theme", weight="bold"),
                        rx.select(
                            ["Light", "Dark", "System"],
                            default_value="Light",
                            width="300px",
                        ),
                        width="100%",
                        justify="between",
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


def projects_page() -> rx.Component:
    """Projects page for organizing chats."""
    return client_layout(
        rx.vstack(
            rx.heading("Projects", size="8"),
            
            rx.hstack(
                rx.input(
                    placeholder="Search projects...",
                    width="300px",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("plus"),
                    "New Project",
                    color_scheme="blue",
                ),
                width="100%",
            ),
            
            rx.grid(
                rx.card(
                    rx.vstack(
                        rx.text("📁", font_size="3em"),
                        rx.heading("Default", size="5"),
                        rx.text("5 chats", color="gray", size="2"),
                        align_items="center",
                        spacing="2",
                    ),
                    _hover={"cursor": "pointer", "box_shadow": "lg"},
                ),
                rx.card(
                    rx.vstack(
                        rx.text("💼", font_size="3em"),
                        rx.heading("Work", size="5"),
                        rx.text("12 chats", color="gray", size="2"),
                        align_items="center",
                        spacing="2",
                    ),
                    _hover={"cursor": "pointer", "box_shadow": "lg"},
                ),
                rx.card(
                    rx.vstack(
                        rx.text("🔬", font_size="3em"),
                        rx.heading("Research", size="5"),
                        rx.text("8 chats", color="gray", size="2"),
                        align_items="center",
                        spacing="2",
                    ),
                    _hover={"cursor": "pointer", "box_shadow": "lg"},
                ),
                columns="3",
                spacing="4",
                width="100%",
            ),
            
            width="100%",
            spacing="6",
            align_items="flex-start",
        ),
    )


def prompts_page() -> rx.Component:
    """System prompts page."""
    return client_layout(
        rx.vstack(
            rx.heading("System Prompts", size="8"),
            
            rx.hstack(
                rx.input(
                    placeholder="Search prompts...",
                    width="300px",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("plus"),
                    "New Prompt",
                    color_scheme="blue",
                ),
                width="100%",
            ),
            
            rx.vstack(
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Code Assistant", size="4"),
                            rx.spacer(),
                            rx.badge("Public", color_scheme="green"),
                            width="100%",
                        ),
                        rx.text(
                            "You are an expert programmer. Help users write clean, efficient code...",
                            color="gray",
                            size="2",
                        ),
                        rx.hstack(
                            rx.badge("coding"),
                            rx.badge("programming"),
                            spacing="2",
                        ),
                        width="100%",
                        align_items="flex-start",
                        spacing="2",
                    ),
                ),
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Creative Writer", size="4"),
                            rx.spacer(),
                            rx.badge("Private", color_scheme="gray"),
                            width="100%",
                        ),
                        rx.text(
                            "You are a creative writing assistant. Help users craft engaging stories...",
                            color="gray",
                            size="2",
                        ),
                        rx.hstack(
                            rx.badge("writing"),
                            rx.badge("creative"),
                            spacing="2",
                        ),
                        width="100%",
                        align_items="flex-start",
                        spacing="2",
                    ),
                ),
                width="100%",
                spacing="4",
            ),
            
            width="100%",
            spacing="6",
            align_items="flex-start",
        ),
    )


def usage_page() -> rx.Component:
    """Usage monitoring page."""
    return client_layout(
        rx.vstack(
            rx.heading("Usage", size="8"),
            
            rx.grid(
                rx.card(
                    rx.vstack(
                        rx.text("📊", font_size="2em"),
                        rx.heading("1,234", size="6"),
                        rx.text("Total Tokens", color="gray"),
                        align_items="center",
                    ),
                ),
                rx.card(
                    rx.vstack(
                        rx.text("💬", font_size="2em"),
                        rx.heading("45", size="6"),
                        rx.text("Conversations", color="gray"),
                        align_items="center",
                    ),
                ),
                rx.card(
                    rx.vstack(
                        rx.text("💰", font_size="2em"),
                        rx.heading("$0.12", size="6"),
                        rx.text("Total Cost", color="gray"),
                        align_items="center",
                    ),
                ),
                columns="3",
                spacing="4",
                width="100%",
            ),
            
            rx.card(
                rx.vstack(
                    rx.heading("Usage History", size="5"),
                    rx.text("Detailed usage statistics will appear here", color="gray"),
                    width="100%",
                    align_items="flex-start",
                ),
            ),
            
            width="100%",
            spacing="6",
            align_items="flex-start",
        ),
    )


def logs_page() -> rx.Component:
    """Logs page."""
    return client_layout(
        rx.vstack(
            rx.heading("Logs", size="8"),
            
            rx.card(
                rx.vstack(
                    rx.heading("Activity Logs", size="5"),
                    rx.text("Your activity logs will appear here", color="gray"),
                    width="100%",
                    align_items="flex-start",
                ),
            ),
            
            width="100%",
            spacing="6",
            align_items="flex-start",
        ),
    )
