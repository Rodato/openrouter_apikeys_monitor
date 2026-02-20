#!/usr/bin/env python3
import argparse
import sys
import os
import time

# Ensure src/ is in path when running from project root
sys.path.insert(0, os.path.dirname(__file__))

from rich.live import Live
from rich.console import Console

from config import load_config
from monitor import build_renderable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monitor OpenRouter API key usage and costs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 src/main.py --once
  python3 src/main.py --watch
  python3 src/main.py --watch --interval 30
        """,
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--once", action="store_true", help="Print snapshot and exit")
    mode.add_argument("--watch", action="store_true", help="Continuously refresh display")
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Refresh interval in seconds (overrides .env REFRESH_INTERVAL)",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config.yaml (default: config.yaml)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    if args.interval is not None:
        config.refresh_interval = args.interval

    console = Console()

    if args.once:
        renderable, errors = build_renderable(config)
        console.print(renderable)
        sys.exit(1 if errors else 0)

    # --watch mode
    with Live(console=console, refresh_per_second=1, screen=False) as live:
        while True:
            try:
                renderable, _ = build_renderable(config)
                live.update(renderable)
            except KeyboardInterrupt:
                break
            except Exception as exc:
                console.print(f"[bold red]Unexpected error:[/bold red] {exc}")

            try:
                time.sleep(config.refresh_interval)
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    main()
