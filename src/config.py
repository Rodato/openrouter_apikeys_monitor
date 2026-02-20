import os
import sys
import yaml
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import Optional

load_dotenv()


@dataclass
class ProjectConfig:
    key_name: str
    label: str
    alert_monthly_usd: float


@dataclass
class AlertsConfig:
    enabled: bool = True
    cooldown_minutes: int = 60


@dataclass
class AppConfig:
    management_key: str
    telegram_bot_token: Optional[str]
    telegram_chat_id: Optional[str]
    refresh_interval: int
    projects: list[ProjectConfig]
    alerts: AlertsConfig


def load_config(config_path: str = "config.yaml") -> AppConfig:
    management_key = os.getenv("OPENROUTER_MANAGEMENT_KEY", "").strip()
    if not management_key:
        print("ERROR: OPENROUTER_MANAGEMENT_KEY is not set in .env", file=sys.stderr)
        sys.exit(1)

    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip() or None
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip() or None

    try:
        refresh_interval = int(os.getenv("REFRESH_INTERVAL", "60"))
    except ValueError:
        refresh_interval = 60

    if not os.path.exists(config_path):
        print(f"ERROR: config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    projects = []
    for p in raw.get("projects", []):
        projects.append(ProjectConfig(
            key_name=p["key_name"],
            label=p.get("label", p["key_name"]),
            alert_monthly_usd=float(p.get("alert_monthly_usd", 0)),
        ))

    raw_alerts = raw.get("alerts", {})
    alerts = AlertsConfig(
        enabled=raw_alerts.get("enabled", True),
        cooldown_minutes=int(raw_alerts.get("cooldown_minutes", 60)),
    )

    return AppConfig(
        management_key=management_key,
        telegram_bot_token=telegram_bot_token,
        telegram_chat_id=telegram_chat_id,
        refresh_interval=refresh_interval,
        projects=projects,
        alerts=alerts,
    )
