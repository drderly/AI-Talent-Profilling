"""Reflex configuration file."""
import reflex as rx
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

config = rx.Config(
    app_name="llm_ui",
    db_url=os.getenv("DATABASE_URL", "sqlite:///llm_ui.db"),
    env=rx.Env.DEV,
    # Port configuration (avoid conflict with LLM API on 8000)
    backend_port=8001,
    frontend_port=3000,
    # Disable sitemap plugin to avoid warning
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    # Tailwind config for modern styling
    tailwind={
        "theme": {
            "extend": {
                "colors": {
                    "primary": "#6366f1",
                    "secondary": "#8b5cf6",
                    "accent": "#ec4899",
                    "dark": "#1f2937",
                    "light": "#f9fafb",
                },
            },
        },
    },
)
