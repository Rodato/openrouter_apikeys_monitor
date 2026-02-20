from datetime import datetime
from typing import Optional

from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.console import Group
from rich import box

from api import OpenRouterClient
from config import AppConfig
from alerts import maybe_alert


def _fmt_usd(value) -> str:
    try:
        return f"${float(value):.4f}"
    except (TypeError, ValueError):
        return "—"


def _status_text(pct: float) -> Text:
    if pct >= 100:
        return Text("🔴 ALERT", style="bold red")
    elif pct >= 80:
        return Text("⚠ WARNING", style="bold yellow")
    else:
        return Text("OK", style="bold green")


def build_renderable(config: AppConfig) -> tuple[Group, list[str]]:
    """Fetch data and return a Rich renderable + list of error strings."""
    client = OpenRouterClient(config.management_key)
    errors: list[str] = []

    # Fetch API data
    keys_by_name: dict[str, dict] = {}
    try:
        keys = client.get_keys()
        for k in keys:
            name = k.get("name") or k.get("label") or ""
            keys_by_name[name] = k
    except Exception as exc:
        errors.append(f"keys fetch error: {exc}")

    credits_info: dict = {}
    try:
        credits_info = client.get_credits()
    except Exception as exc:
        errors.append(f"credits fetch error: {exc}")

    # Build table
    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        expand=True,
    )
    table.add_column("Project", style="bold")
    table.add_column("Uso hoy", justify="right")
    table.add_column("Uso semana", justify="right")
    table.add_column("Uso mes", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Límite restante", justify="right")
    table.add_column("Estado", justify="center")

    for proj in config.projects:
        key_data = keys_by_name.get(proj.key_name, {})
        usage_daily = key_data.get("usage_daily") or 0
        usage_weekly = key_data.get("usage_weekly") or 0
        usage_monthly = key_data.get("usage_monthly") or 0
        usage_total = key_data.get("usage") or 0
        limit_remaining = key_data.get("limit_remaining")
        disabled = key_data.get("disabled", False)

        pct = (usage_monthly / proj.alert_monthly_usd * 100) if proj.alert_monthly_usd > 0 else 0
        status = _status_text(pct)
        if disabled:
            status = Text("DISABLED", style="bold magenta")

        limit_str = _fmt_usd(limit_remaining) if limit_remaining is not None else "∞"

        table.add_row(
            proj.label,
            _fmt_usd(usage_daily),
            _fmt_usd(usage_weekly),
            _fmt_usd(usage_monthly),
            _fmt_usd(usage_total),
            limit_str,
            status,
        )

        # Trigger alerts if needed
        maybe_alert(
            bot_token=config.telegram_bot_token,
            chat_id=config.telegram_chat_id,
            alerts_enabled=config.alerts.enabled,
            project_label=proj.label,
            key_name=proj.key_name,
            usage_monthly=float(usage_monthly),
            threshold=proj.alert_monthly_usd,
            cooldown_minutes=config.alerts.cooldown_minutes,
        )

    # Header info
    total_purchased = credits_info.get("total_purchased") or credits_info.get("purchased") or 0
    total_consumed = credits_info.get("total_consumed") or credits_info.get("consumed") or 0
    remaining = float(total_purchased) - float(total_consumed)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header_text = (
        f"[bold]OpenRouter Monitor[/bold]  •  "
        f"Last refresh: [cyan]{now_str}[/cyan]  •  "
        f"Account credits: purchased [green]${float(total_purchased):.4f}[/green]  "
        f"consumed [red]${float(total_consumed):.4f}[/red]  "
        f"remaining [yellow]${remaining:.4f}[/yellow]"
    )
    header = Panel(header_text, style="dim")

    renderables: list = [header, table]
    if errors:
        from rich.text import Text as RText
        err_text = RText("\n".join(errors), style="bold red")
        renderables.append(Panel(err_text, title="Errors", border_style="red"))

    return Group(*renderables), errors
