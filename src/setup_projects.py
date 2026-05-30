#!/usr/bin/env python3
"""
Interactive setup script to detect and select OpenRouter projects to monitor.
Fetches all keys from your OpenRouter account and lets you choose which ones to track.
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from api import OpenRouterClient
from config import load_config
import yaml


def main():
    print("🔍 OpenRouter Project Setup\n")

    # Load current config to get management key
    try:
        config = load_config("config.yaml")
        management_key = config.management_key
    except Exception:
        # Fallback to .env
        from dotenv import load_dotenv
        load_dotenv()
        management_key = os.getenv("OPENROUTER_MANAGEMENT_KEY")

    if not management_key:
        print("❌ Error: OPENROUTER_MANAGEMENT_KEY not found in config.yaml or .env")
        print("   Add it to your .env file first.")
        sys.exit(1)

    print(f"✅ Management key found: {management_key[:20]}...")
    print("\n📡 Fetching all API keys from OpenRouter...\n")

    # Fetch all keys
    client = OpenRouterClient(management_key)
    try:
        keys = client.get_keys()
    except Exception as exc:
        print(f"❌ Error fetching keys: {exc}")
        sys.exit(1)

    if not keys:
        print("⚠️  No API keys found in your OpenRouter account.")
        print("   Create some keys at https://openrouter.ai/settings/keys first.")
        sys.exit(0)

    print(f"Found {len(keys)} API keys:\n")

    # Display all keys with current usage
    for idx, key in enumerate(keys, 1):
        name = key.get("name") or key.get("label") or "Unnamed"
        usage_monthly = key.get("usage_monthly") or 0
        usage_total = key.get("usage") or 0
        disabled = key.get("disabled", False)

        status = "🚫 DISABLED" if disabled else f"💰 ${usage_monthly:.4f} this month"

        print(f"  {idx}. {name}")
        print(f"     {status} (${usage_total:.4f} total)")
        print()

    print("─" * 60)
    print("\n📋 Current config.yaml projects:")

    # Load current config
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path) as f:
            current_config = yaml.safe_load(f)

        current_projects = current_config.get("projects", [])
        if current_projects:
            for proj in current_projects:
                print(f"  • {proj['label']} ({proj['key_name']}) - ${proj['alert_monthly_usd']:.2f} threshold")
        else:
            print("  (none)")
    else:
        current_config = {"projects": [], "alerts": {"enabled": True, "cooldown_minutes": 60}}
        current_projects = []

    print("\n─" * 60)
    print("\n🎯 Select projects to monitor:")
    print("   Enter numbers separated by spaces (e.g., '1 3 5')")
    print("   Or 'all' to monitor all keys")
    print("   Or 'skip' to keep current config\n")

    selection = input("Your selection: ").strip().lower()

    if selection == "skip":
        print("\n✅ Keeping current config unchanged.")
        return

    # Parse selection
    if selection == "all":
        selected_indices = list(range(len(keys)))
    else:
        try:
            selected_indices = [int(x) - 1 for x in selection.split()]
            # Validate
            if any(i < 0 or i >= len(keys) for i in selected_indices):
                print("\n❌ Invalid selection. Numbers must be between 1 and", len(keys))
                sys.exit(1)
        except ValueError:
            print("\n❌ Invalid input. Enter numbers separated by spaces.")
            sys.exit(1)

    if not selected_indices:
        print("\n⚠️  No projects selected. Exiting.")
        return

    print(f"\n✅ Selected {len(selected_indices)} projects.\n")

    # Build new projects list
    new_projects = []
    for idx in selected_indices:
        key = keys[idx]
        name = key.get("name") or key.get("label") or f"project_{idx}"

        # Check if already exists in current config
        existing = next((p for p in current_projects if p["key_name"] == name), None)

        if existing:
            # Keep existing threshold
            threshold = existing["alert_monthly_usd"]
            label = existing["label"]
            print(f"  ✓ {label} - keeping threshold ${threshold:.2f}")
        else:
            # New project - ask for threshold
            label = input(f"  Display name for '{name}': ").strip() or name
            while True:
                try:
                    threshold_str = input(f"  Monthly alert threshold (USD) for '{label}': ").strip()
                    threshold = float(threshold_str)
                    if threshold <= 0:
                        print("    Threshold must be > 0")
                        continue
                    break
                except ValueError:
                    print("    Please enter a valid number")

        new_projects.append({
            "key_name": name,
            "label": label,
            "alert_monthly_usd": threshold
        })

    # Update config
    current_config["projects"] = new_projects

    # Write to config.yaml
    print(f"\n💾 Writing to config.yaml...")
    with open(config_path, "w") as f:
        yaml.dump(current_config, f, default_flow_style=False, sort_keys=False)

    print("\n✅ Config updated successfully!\n")
    print("📋 New config.yaml projects:")
    for proj in new_projects:
        print(f"  • {proj['label']} ({proj['key_name']}) - ${proj['alert_monthly_usd']:.2f} threshold")

    print("\n🚀 Next steps:")
    print("  1. Test locally: python3 src/main.py --once")
    print("  2. Push to Railway: git add config.yaml && git commit -m 'Update projects' && git push")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user.")
        sys.exit(0)
