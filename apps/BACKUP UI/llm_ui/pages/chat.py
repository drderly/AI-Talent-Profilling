"""Chat page with SSE streaming support."""
import reflex as rx
from ..states.chat_state import ChatState, Message
from ..components.sidebar import client_sidebar


def message_bubble(message: Message) -> rx.Component:
    """Render a chat message bubble."""
    is_user = message.role == "user"
    
    return rx.box(
        rx.hstack(
            rx.cond(
                is_user,
                rx.spacer(),
                rx.box(),
            ),
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.avatar(
                            fallback=rx.cond(is_user, "U", "AI"),
                            size="2",
                            color_scheme=rx.cond(is_user, "blue", "purple"),
                        ),
                        rx.text(
                            rx.cond(is_user, "You", "Assistant"),
                            font_weight="bold",
                            size="2",
                        ),
                        rx.spacer(),
                        rx.text(
                            message.timestamp,
                            size="1",
                            color="gray",
                        ),
                        width="100%",
                    ),
                    rx.text(
                        message.content,
                        size="3",
                        line_height="1.6",
                    ),
                    width="100%",
                    spacing="2",
                    align_items="flex-start",
                ),
                size="2",
                background=rx.cond(is_user, "#e0e7ff", "#f3e8ff"),
            ),
            rx.cond(
                is_user,
                rx.box(),
                rx.spacer(),
            ),
            width="100%",
            max_width="800px",
        ),
        padding="0.5em",
        width="100%",
    )


def chat_interface() -> rx.Component:
    """Main chat interface."""
    return rx.vstack(
        # Chat messages area
        rx.box(
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(
                        ChatState.messages,
                        message_bubble,
                    ),
                    # Streaming message
                    rx.cond(
                        ChatState.is_streaming,
                        rx.box(
                            rx.card(
                                rx.vstack(
                                    rx.hstack(
                                        rx.avatar(fallback="AI", size="2", color_scheme="purple"),
                                        rx.text("Assistant", font_weight="bold", size="2"),
                                        rx.spinner(size="1"),
                                        width="100%",
                                    ),
                                    rx.text(
                                        ChatState.current_response,
                                        size="3",
                                        line_height="1.6",
                                    ),
                                    width="100%",
                                    spacing="2",
                                    align_items="flex-start",
                                ),
                                size="2",
                                background="#f3e8ff",
                            ),
                            padding="0.5em",
                            width="100%",
                        ),
                    ),
                    width="100%",
                    spacing="2",
                    align_items="center",
                ),
                width="100%",
                height="100%",
            ),
            flex_grow="1",
            overflow="auto",
            width="100%",
        ),
        
        # Error message
        rx.cond(
            ChatState.error_message != "",
            rx.callout(
                ChatState.error_message,
                icon="triangle-alert",
                color_scheme="red",
                width="100%",
            ),
        ),
        
        # Input area
        rx.box(
            rx.vstack(
                # Model selector and settings
                rx.hstack(
                    rx.select(
                        ["smollm2:1.7b", "mistral:7b-instruct", "llama3:8b-instruct"],
                        value=ChatState.selected_model,
                        on_change=ChatState.set_selected_model,
                        size="2",
                    ),
                    rx.badge(
                        rx.cond(ChatState.thinking_mode, "🤔 Thinking", "Thinking"),
                        color_scheme=rx.cond(ChatState.thinking_mode, "purple", "gray"),
                        on_click=ChatState.toggle_thinking_mode,
                        cursor="pointer",
                    ),
                    rx.badge(
                        rx.cond(ChatState.browsing_mode, "🌐 Browsing", "Browsing"),
                        color_scheme=rx.cond(ChatState.browsing_mode, "blue", "gray"),
                        on_click=ChatState.toggle_browsing_mode,
                        cursor="pointer",
                    ),
                    rx.badge(
                        rx.cond(ChatState.attach_mode, "📎 Attach", "Attach"),
                        color_scheme=rx.cond(ChatState.attach_mode, "green", "gray"),
                        on_click=ChatState.toggle_attach_mode,
                        cursor="pointer",
                    ),
                    rx.spacer(),
                    rx.icon_button(
                        rx.icon("trash-2"),
                        on_click=ChatState.clear_chat,
                        size="2",
                        variant="ghost",
                    ),
                    width="100%",
                    spacing="2",
                ),
                
                # Input field
                rx.hstack(
                    rx.text_area(
                        placeholder="Type your message...",
                        value=ChatState.current_input,
                        on_change=ChatState.set_current_input,
                        size="3",
                        min_height="60px",
                        width="100%",
                        disabled=ChatState.is_streaming,
                    ),
                    rx.button(
                        rx.icon("send"),
                        on_click=ChatState.send_message,
                        size="3",
                        color_scheme="blue",
                        disabled=ChatState.is_streaming,
                    ),
                    width="100%",
                    spacing="2",
                    align_items="flex-end",
                ),
                
                # Metrics display
                rx.cond(
                    ChatState.last_metrics != {},
                    rx.hstack(
                        rx.text(
                            f"TTFT: {ChatState.last_metrics.get('ttft', 'N/A')}s",
                            size="1",
                            color="gray",
                        ),
                        rx.text(
                            f"Latency: {ChatState.last_metrics.get('total_latency', 'N/A')}s",
                            size="1",
                            color="gray",
                        ),
                        rx.text(
                            f"Speed: {ChatState.last_metrics.get('output_tokens_per_second', 'N/A')} tok/s",
                            size="1",
                            color="gray",
                        ),
                        rx.text(
                            f"Tokens: {ChatState.last_metrics.get('input_tokens', 0)} + {ChatState.last_metrics.get('output_tokens', 0)}",
                            size="1",
                            color="gray",
                        ),
                        spacing="4",
                    ),
                ),
                
                width="100%",
                spacing="3",
            ),
            padding="1em",
            border_top="1px solid #e5e7eb",
            background="white",
            width="100%",
        ),
        
        width="100%",
        height="100vh",
        spacing="0",
    )


def chat_page() -> rx.Component:
    """Chat page with sidebar."""
    return rx.hstack(
        client_sidebar(),
        rx.box(
            chat_interface(),
            margin_left="250px",
            width="calc(100% - 250px)",
            height="100vh",
        ),
        width="100%",
        height="100vh",
        spacing="0",
    )
