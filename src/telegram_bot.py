#!/usr/bin/env python3
"""
Interactive Telegram bot to manage OpenRouter monitoring.
Commands:
  /start - Welcome message
  /list - Show all available OpenRouter keys
  /add - Add a project to monitoring
  /remove - Remove a project from monitoring
  /status - Show currently monitored projects
  /threshold - Change alert threshold for a project
  /report - Send immediate status report
"""
import sys
import os
import time
import requests
import yaml
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from api import OpenRouterClient
from monitor import build_telegram_report


CONFIG_PATH = Path("config.yaml")


def load_config() -> dict:
    """Load config.yaml"""
    if not CONFIG_PATH.exists():
        return {"projects": [], "alerts": {"enabled": True, "cooldown_minutes": 60}}
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def save_config(config: dict) -> None:
    """Save config.yaml"""
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def get_env(key: str) -> Optional[str]:
    """Get environment variable"""
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv(key)


def send_message(bot_token: str, chat_id: str, text: str, parse_mode: str = "Markdown") -> bool:
    """Send a message via Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        resp = requests.post(
            url,
            json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except Exception as exc:
        print(f"[bot] Failed to send message: {exc}")
        return False


def handle_start(bot_token: str, chat_id: str) -> None:
    """Handle /start command"""
    text = """
🤖 *OpenRouter Monitor Bot*

Gestiona tus proyectos de OpenRouter desde Telegram.

*Comandos disponibles:*

/list — Ver todos tus API keys de OpenRouter
/add — Agregar proyecto al monitoreo
/remove — Quitar proyecto del monitoreo
/status — Ver proyectos monitoreados
/threshold — Cambiar umbral de alerta
/report — Enviar reporte inmediato

*Ejemplo de uso:*
1. /list → Ve tus proyectos
2. /add → Selecciona qué monitorear
3. /status → Confirma que está activo
4. /report → Recibe reporte inmediato
"""
    send_message(bot_token, chat_id, text)


def handle_list(bot_token: str, chat_id: str, management_key: str) -> None:
    """Handle /list command - show all OpenRouter keys"""
    send_message(bot_token, chat_id, "🔍 Consultando tus API keys...")

    client = OpenRouterClient(management_key)
    try:
        keys = client.get_keys()
    except Exception as exc:
        send_message(bot_token, chat_id, f"❌ Error consultando OpenRouter: {exc}")
        return

    if not keys:
        send_message(bot_token, chat_id, "⚠️ No se encontraron API keys en tu cuenta de OpenRouter.")
        return

    lines = [
        f"📋 *Tus API keys en OpenRouter ({len(keys)}):*",
        ""
    ]

    for idx, key in enumerate(keys, 1):
        name = key.get("name") or key.get("label") or "Unnamed"
        usage_monthly = float(key.get("usage_monthly") or 0)
        usage_total = float(key.get("usage") or 0)
        disabled = key.get("disabled", False)

        if disabled:
            status = "🚫 DISABLED"
        elif usage_monthly > 0:
            status = f"💰 ${usage_monthly:.4f} este mes"
        else:
            status = "💤 Sin uso este mes"

        lines.append(f"{idx}. *{name}*")
        lines.append(f"   {status} (${usage_total:.4f} total)")
        lines.append("")

    lines.append("Para agregar al monitoreo: /add")

    send_message(bot_token, chat_id, "\n".join(lines))


def handle_status(bot_token: str, chat_id: str) -> None:
    """Handle /status command - show monitored projects"""
    config = load_config()
    projects = config.get("projects", [])

    if not projects:
        send_message(
            bot_token,
            chat_id,
            "⚠️ No hay proyectos monitoreados.\n\nUsa /list para ver tus keys y /add para agregar."
        )
        return

    lines = [
        f"✅ *Proyectos monitoreados ({len(projects)}):*",
        ""
    ]

    for proj in projects:
        lines.append(f"• *{proj['label']}*")
        lines.append(f"  Key: `{proj['key_name']}`")
        lines.append(f"  Umbral: ${proj['alert_monthly_usd']:.2f}/mes")
        lines.append("")

    lines.append("Comandos: /add /remove /threshold /report")

    send_message(bot_token, chat_id, "\n".join(lines))


def handle_report(bot_token: str, chat_id: str, management_key: str) -> None:
    """Handle /report command - send immediate status report"""
    send_message(bot_token, chat_id, "📊 Generando reporte...")

    from config import AppConfig
    config_obj = AppConfig(
        management_key=management_key,
        telegram_bot_token=bot_token,
        telegram_chat_id=chat_id,
        refresh_interval=60,
        projects=[],
        alerts=type('obj', (object,), {'enabled': True, 'cooldown_minutes': 60})()
    )

    # Load projects from config.yaml
    config = load_config()
    from config import ProjectConfig
    config_obj.projects = [
        ProjectConfig(
            key_name=p["key_name"],
            label=p["label"],
            alert_monthly_usd=p["alert_monthly_usd"]
        )
        for p in config.get("projects", [])
    ]

    from monitor import send_telegram_report
    ok = send_telegram_report(config_obj)

    if not ok:
        send_message(bot_token, chat_id, "❌ Error generando reporte")


def handle_add_interactive(bot_token: str, chat_id: str, management_key: str) -> None:
    """Handle /add command - interactive project addition"""
    text = """
📝 *Agregar proyecto al monitoreo*

Para agregar un proyecto, necesito:
1. El nombre exacto de la key (usa /list para verlo)
2. Un nombre bonito para mostrar
3. El umbral mensual en USD

*Formato:*
`/add nombre_key | Nombre Bonito | 10.0`

*Ejemplo:*
`/add AMABot_Bruno | Chat Bot AMA | 200.0`

Esto monitoreará "AMABot_Bruno" y enviará alerta cuando supere $200/mes.
"""
    send_message(bot_token, chat_id, text)


def handle_add_project(bot_token: str, chat_id: str, text: str) -> None:
    """Handle /add with parameters"""
    # Parse: /add key_name | label | threshold
    parts = text.replace("/add ", "").split("|")
    if len(parts) != 3:
        handle_add_interactive(bot_token, chat_id, "")
        return

    key_name = parts[0].strip()
    label = parts[1].strip()
    try:
        threshold = float(parts[2].strip())
        if threshold <= 0:
            send_message(bot_token, chat_id, "❌ El umbral debe ser mayor a 0")
            return
    except ValueError:
        send_message(bot_token, chat_id, "❌ El umbral debe ser un número válido")
        return

    # Load config
    config = load_config()
    projects = config.get("projects", [])

    # Check if already exists
    if any(p["key_name"] == key_name for p in projects):
        send_message(bot_token, chat_id, f"⚠️ Ya existe un proyecto con key_name: {key_name}")
        return

    # Add new project
    projects.append({
        "key_name": key_name,
        "label": label,
        "alert_monthly_usd": threshold
    })

    config["projects"] = projects
    save_config(config)

    send_message(
        bot_token,
        chat_id,
        f"✅ Proyecto agregado:\n\n*{label}*\nKey: `{key_name}`\nUmbral: ${threshold:.2f}/mes\n\nUsa /status para verificar."
    )


def handle_remove_interactive(bot_token: str, chat_id: str) -> None:
    """Handle /remove command - show current projects"""
    config = load_config()
    projects = config.get("projects", [])

    if not projects:
        send_message(bot_token, chat_id, "⚠️ No hay proyectos para remover.")
        return

    lines = [
        "🗑️ *Remover proyecto del monitoreo*",
        "",
        "Proyectos actuales:",
        ""
    ]

    for idx, proj in enumerate(projects, 1):
        lines.append(f"{idx}. {proj['label']} (`{proj['key_name']}`)")

    lines.append("")
    lines.append("*Formato:*")
    lines.append("`/remove nombre_key`")
    lines.append("")
    lines.append("*Ejemplo:*")
    lines.append("`/remove AMABot_Bruno`")

    send_message(bot_token, chat_id, "\n".join(lines))


def handle_remove_project(bot_token: str, chat_id: str, text: str) -> None:
    """Handle /remove with key_name"""
    key_name = text.replace("/remove ", "").strip()

    config = load_config()
    projects = config.get("projects", [])

    # Find and remove
    original_len = len(projects)
    projects = [p for p in projects if p["key_name"] != key_name]

    if len(projects) == original_len:
        send_message(bot_token, chat_id, f"❌ No se encontró proyecto con key: {key_name}")
        return

    config["projects"] = projects
    save_config(config)

    send_message(bot_token, chat_id, f"✅ Proyecto `{key_name}` removido del monitoreo.")


def handle_threshold_interactive(bot_token: str, chat_id: str) -> None:
    """Handle /threshold command - show usage"""
    text = """
⚙️ *Cambiar umbral de alerta*

*Formato:*
`/threshold nombre_key | nuevo_umbral`

*Ejemplo:*
`/threshold AMABot_Bruno | 250.0`

Esto cambiará el umbral de alerta a $250/mes.

Usa /status para ver tus proyectos actuales.
"""
    send_message(bot_token, chat_id, text)


def handle_threshold_change(bot_token: str, chat_id: str, text: str) -> None:
    """Handle /threshold with parameters"""
    parts = text.replace("/threshold ", "").split("|")
    if len(parts) != 2:
        handle_threshold_interactive(bot_token, chat_id)
        return

    key_name = parts[0].strip()
    try:
        new_threshold = float(parts[1].strip())
        if new_threshold <= 0:
            send_message(bot_token, chat_id, "❌ El umbral debe ser mayor a 0")
            return
    except ValueError:
        send_message(bot_token, chat_id, "❌ El umbral debe ser un número válido")
        return

    config = load_config()
    projects = config.get("projects", [])

    # Find and update
    found = False
    for proj in projects:
        if proj["key_name"] == key_name:
            old_threshold = proj["alert_monthly_usd"]
            proj["alert_monthly_usd"] = new_threshold
            found = True
            break

    if not found:
        send_message(bot_token, chat_id, f"❌ No se encontró proyecto con key: {key_name}")
        return

    config["projects"] = projects
    save_config(config)

    send_message(
        bot_token,
        chat_id,
        f"✅ Umbral actualizado:\n\n*{key_name}*\nAnterior: ${old_threshold:.2f}\nNuevo: ${new_threshold:.2f}"
    )


def process_message(bot_token: str, chat_id: str, management_key: str, message: dict) -> None:
    """Process incoming message"""
    text = message.get("text", "").strip()

    if not text:
        return

    # Route commands
    if text == "/start":
        handle_start(bot_token, chat_id)
    elif text == "/list":
        handle_list(bot_token, chat_id, management_key)
    elif text == "/status":
        handle_status(bot_token, chat_id)
    elif text == "/report":
        handle_report(bot_token, chat_id, management_key)
    elif text == "/add":
        handle_add_interactive(bot_token, chat_id, management_key)
    elif text.startswith("/add "):
        handle_add_project(bot_token, chat_id, text)
    elif text == "/remove":
        handle_remove_interactive(bot_token, chat_id)
    elif text.startswith("/remove "):
        handle_remove_project(bot_token, chat_id, text)
    elif text == "/threshold":
        handle_threshold_interactive(bot_token, chat_id)
    elif text.startswith("/threshold "):
        handle_threshold_change(bot_token, chat_id, text)
    else:
        send_message(
            bot_token,
            chat_id,
            "❓ Comando no reconocido.\n\nUsa /start para ver la lista de comandos."
        )


def get_updates(bot_token: str, offset: int = 0) -> list:
    """Get updates from Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        resp = requests.get(url, params={"offset": offset, "timeout": 30}, timeout=35)
        resp.raise_for_status()
        data = resp.json()
        return data.get("result", [])
    except Exception as exc:
        print(f"[bot] Error getting updates: {exc}")
        return []


def main():
    """Main bot loop"""
    bot_token = get_env("TELEGRAM_BOT_TOKEN")
    chat_id = get_env("TELEGRAM_CHAT_ID")
    management_key = get_env("OPENROUTER_MANAGEMENT_KEY")

    if not all([bot_token, chat_id, management_key]):
        print("❌ Missing environment variables:")
        print(f"   TELEGRAM_BOT_TOKEN: {'✓' if bot_token else '✗'}")
        print(f"   TELEGRAM_CHAT_ID: {'✓' if chat_id else '✗'}")
        print(f"   OPENROUTER_MANAGEMENT_KEY: {'✓' if management_key else '✗'}")
        sys.exit(1)

    print("🤖 OpenRouter Telegram Bot started")
    print(f"   Bot token: {bot_token[:20]}...")
    print(f"   Chat ID: {chat_id}")
    print("   Polling for messages...\n")

    offset = 0

    while True:
        try:
            updates = get_updates(bot_token, offset)

            for update in updates:
                offset = update["update_id"] + 1
                message = update.get("message", {})

                # Only process messages from authorized chat
                if str(message.get("chat", {}).get("id")) != str(chat_id):
                    print(f"[bot] Ignoring message from unauthorized chat: {message.get('chat', {}).get('id')}")
                    continue

                print(f"[bot] Processing: {message.get('text', '')[:50]}...")
                process_message(bot_token, chat_id, management_key, message)

            time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n👋 Bot stopped by user")
            break
        except Exception as exc:
            print(f"[bot] Error in main loop: {exc}")
            time.sleep(5)


if __name__ == "__main__":
    main()
