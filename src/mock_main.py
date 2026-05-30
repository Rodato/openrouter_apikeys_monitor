#!/usr/bin/env python3
import sys
import os
import time
from typing import Optional

# Ensure src/ is in path
sys.path.insert(0, os.path.dirname(__file__))

from rich.live import Live
from rich.console import Console

from config import AppConfig, ProjectConfig, AlertsConfig
from monitor import build_renderable

class MockOpenRouterClient:
    def get_keys(self) -> list[dict]:
        return [
            {
                "name": "Project Alpha",
                "usage_daily": 1.25,
                "usage_weekly": 8.50,
                "usage_monthly": 45.20,
                "usage": 150.75,
                "limit_remaining": 54.80,
                "disabled": False
            },
            {
                "name": "Project Beta",
                "usage_daily": 0.45,
                "usage_weekly": 2.10,
                "usage_monthly": 12.30,
                "usage": 80.10,
                "limit_remaining": None,
                "disabled": False
            },
            {
                "name": "R&D Experiments",
                "usage_daily": 4.50,
                "usage_weekly": 15.20,
                "usage_monthly": 85.00,
                "usage": 210.00,
                "limit_remaining": 15.00,
                "disabled": False
            },
            {
                "name": "Legacy Bot",
                "usage_daily": 0.00,
                "usage_weekly": 0.00,
                "usage_monthly": 0.00,
                "usage": 45.00,
                "limit_remaining": 0.00,
                "disabled": True
            }
        ]

    def get_credits(self) -> dict:
        return {
            "total_purchased": 1000.00,
            "total_consumed": 486.35
        }

    def get_activity(self) -> list[dict]:
        return [
            {"model": "anthropic/claude-3-opus", "requests": 150, "prompt_tokens": 450000, "completion_tokens": 120000, "usage": 15.50},
            {"model": "openai/gpt-4-turbo", "requests": 1200, "prompt_tokens": 1200000, "completion_tokens": 800000, "usage": 12.00},
            {"model": "meta-llama/llama-3-70b-instruct", "requests": 5000, "prompt_tokens": 8000000, "completion_tokens": 2000000, "usage": 8.40},
            {"model": "google/gemini-pro-1.5", "requests": 800, "prompt_tokens": 600000, "completion_tokens": 300000, "usage": 4.20},
            {"model": "mistralai/mixtral-8x7b-instruct", "requests": 1500, "prompt_tokens": 2000000, "completion_tokens": 500000, "usage": 1.50},
        ]

def main():
    # Setup mock config
    config = AppConfig(
        management_key="mock-key",
        refresh_interval=5,
        telegram_bot_token=None,
        telegram_chat_id=None,
        projects=[
            ProjectConfig(label="Project Alpha", key_name="Project Alpha", alert_monthly_usd=50.0),
            ProjectConfig(label="Project Beta", key_name="Project Beta", alert_monthly_usd=100.0),
            ProjectConfig(label="R&D Experiments", key_name="R&D Experiments", alert_monthly_usd=90.0),
            ProjectConfig(label="Legacy Bot", key_name="Legacy Bot", alert_monthly_usd=10.0),
        ],
        alerts=AlertsConfig(enabled=False, cooldown_minutes=60)
    )

    client = MockOpenRouterClient()
    console = Console()

    # Just run once for a clean screenshot-ready output
    renderable, _ = build_renderable(config, client=client)
    console.print(renderable)

if __name__ == "__main__":
    main()
