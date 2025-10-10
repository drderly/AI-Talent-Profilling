"""Authentication pages (login and register)."""
import reflex as rx
from ..auth import AuthState


def login_page() -> rx.Component:
    """Login page."""
    return rx.center(
        rx.card(
            rx.vstack(
                # Logo and Title
                rx.hstack(
                    rx.text("🤖", font_size="3em"),
                    rx.heading("LLM Service", size="8"),
                    spacing="2",
                    align_items="center",
                ),
                rx.text(
                    "Sign in to your account",
                    color="gray",
                    size="3",
                ),
                
                # Error/Success Messages
                rx.cond(
                    AuthState.error_message != "",
                    rx.callout(
                        AuthState.error_message,
                        icon="triangle-alert",
                        color_scheme="red",
                        role="alert",
                    ),
                ),
                rx.cond(
                    AuthState.success_message != "",
                    rx.callout(
                        AuthState.success_message,
                        icon="check",
                        color_scheme="green",
                        role="status",
                    ),
                ),
                
                # Login Form
                rx.vstack(
                    rx.text("Email", size="2", weight="bold"),
                    rx.input(
                        placeholder="Enter your email",
                        type="email",
                        value=AuthState.login_email,
                        on_change=AuthState.set_login_email,
                        size="3",
                        width="100%",
                    ),
                    rx.text("Password", size="2", weight="bold"),
                    rx.input(
                        placeholder="Enter your password",
                        type="password",
                        value=AuthState.login_password,
                        on_change=AuthState.set_login_password,
                        size="3",
                        width="100%",
                    ),
                    rx.button(
                        "Sign In",
                        on_click=AuthState.login,
                        size="3",
                        width="100%",
                        color_scheme="blue",
                    ),
                    width="100%",
                    spacing="2",
                ),
                
                # Register Link
                rx.divider(),
                rx.hstack(
                    rx.text("Don't have an account?", size="2"),
                    rx.link("Sign up", href="/register", color="blue"),
                ),
                
                width="100%",
                spacing="5",
            ),
            size="4",
            max_width="400px",
        ),
        height="100vh",
        background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    )


def register_page() -> rx.Component:
    """Register page."""
    return rx.center(
        rx.card(
            rx.vstack(
                # Logo and Title
                rx.hstack(
                    rx.text("🤖", font_size="3em"),
                    rx.heading("Create Account", size="8"),
                    spacing="2",
                    align_items="center",
                ),
                rx.text(
                    "Join the LLM Service",
                    color="gray",
                    size="3",
                ),
                
                # Error/Success Messages
                rx.cond(
                    AuthState.error_message != "",
                    rx.callout(
                        AuthState.error_message,
                        icon="triangle-alert",
                        color_scheme="red",
                        role="alert",
                    ),
                ),
                rx.cond(
                    AuthState.success_message != "",
                    rx.callout(
                        AuthState.success_message,
                        icon="check",
                        color_scheme="green",
                        role="status",
                    ),
                ),
                
                # Register Form
                rx.vstack(
                    rx.text("Email", size="2", weight="bold"),
                    rx.input(
                        placeholder="Enter your email",
                        type="email",
                        value=AuthState.register_email,
                        on_change=AuthState.set_register_email,
                        size="3",
                        width="100%",
                    ),
                    rx.text("Username", size="2", weight="bold"),
                    rx.input(
                        placeholder="Choose a username",
                        value=AuthState.register_username,
                        on_change=AuthState.set_register_username,
                        size="3",
                        width="100%",
                    ),
                    rx.text("Password", size="2", weight="bold"),
                    rx.input(
                        placeholder="Create a password",
                        type="password",
                        value=AuthState.register_password,
                        on_change=AuthState.set_register_password,
                        size="3",
                        width="100%",
                    ),
                    rx.text("Confirm Password", size="2", weight="bold"),
                    rx.input(
                        placeholder="Confirm your password",
                        type="password",
                        value=AuthState.register_confirm_password,
                        on_change=AuthState.set_register_confirm_password,
                        size="3",
                        width="100%",
                    ),
                    rx.button(
                        "Sign Up",
                        on_click=AuthState.register,
                        size="3",
                        width="100%",
                        color_scheme="blue",
                    ),
                    width="100%",
                    spacing="2",
                ),
                
                # Login Link
                rx.divider(),
                rx.hstack(
                    rx.text("Already have an account?", size="2"),
                    rx.link("Sign in", href="/login", color="blue"),
                ),
                
                width="100%",
                spacing="5",
            ),
            size="4",
            max_width="400px",
        ),
        height="100vh",
        background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    )
