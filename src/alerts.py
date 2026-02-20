import time
import requests
from typing import Optional

# cooldown_state: {project_key_name: last_alert_timestamp}
_cooldown_state: dict[str, float] = {}


def send_alert(
    bot_token: str,
    chat_id: str,
    project_label: str,
    key_name: str,
    usage_monthly: float,
    threshold: float,
    cooldown_minutes: int,
) -> bool:
    """Send a Telegram alert if not in cooldown. Returns True if sent."""
    now = time.time()
    last_sent = _cooldown_state.get(key_name, 0)
    if now - last_sent < cooldown_minutes * 60:
        return False

    pct = (usage_monthly / threshold * 100) if threshold > 0 else 0
    emoji = "🔴" if pct >= 100 else "⚠️"
    text = (
        f"{emoji} *OpenRouter Alert*\n"
        f"Project: *{project_label}*\n"
        f"Monthly usage: *${usage_monthly:.4f}*\n"
        f"Threshold: *${threshold:.2f}*\n"
        f"Usage: *{pct:.1f}%*"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        resp = requests.post(
            url,
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=10,
        )
        resp.raise_for_status()
        _cooldown_state[key_name] = now
        return True
    except Exception as exc:
        print(f"[alerts] Failed to send Telegram message: {exc}")
        return False


def maybe_alert(
    bot_token: Optional[str],
    chat_id: Optional[str],
    alerts_enabled: bool,
    project_label: str,
    key_name: str,
    usage_monthly: float,
    threshold: float,
    cooldown_minutes: int,
) -> None:
    if not alerts_enabled or not bot_token or not chat_id:
        return
    if threshold <= 0:
        return
    if usage_monthly >= threshold:
        send_alert(
            bot_token=bot_token,
            chat_id=chat_id,
            project_label=project_label,
            key_name=key_name,
            usage_monthly=usage_monthly,
            threshold=threshold,
            cooldown_minutes=cooldown_minutes,
        )
