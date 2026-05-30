# openrouterMonitor

Terminal UI to monitor costs and usage across multiple OpenRouter API keys, with Telegram alerts when spending exceeds thresholds.

## Setup

### 1. Install dependencies

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in the project root:

```
OPENROUTER_MANAGEMENT_KEY=sk-or-v1-...   # From openrouter.ai/settings/keys (Management Key)
TELEGRAM_BOT_TOKEN=...                    # Optional: from @BotFather
TELEGRAM_CHAT_ID=...                      # Optional: your chat/group ID
REFRESH_INTERVAL=60                       # Seconds between refreshes in --watch mode
```

- `OPENROUTER_MANAGEMENT_KEY` — create a **Management Key** at [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys) (not a regular API key)
- `TELEGRAM_BOT_TOKEN` — create a bot via [@BotFather](https://t.me/BotFather) on Telegram
- `TELEGRAM_CHAT_ID` — send a message to your bot, then visit `https://api.telegram.org/bot<TOKEN>/getUpdates` and look for `chat.id`

### 3. Configure projects

Create a `config.yaml` file in the project root — the `key_name` must exactly match the **name** field of your API key in OpenRouter:

```yaml
projects:
  - key_name: "transcriptor"
    label: "Transcriptor"
    alert_monthly_usd: 10.0
  - key_name: "octopus-api"
    label: "Octopus"
    alert_monthly_usd: 5.0

alerts:
  enabled: true
  cooldown_minutes: 60
```

## Usage

```bash
# One-shot snapshot
venv/bin/python3 src/main.py --once

# Continuous watch (default interval from .env)
venv/bin/python3 src/main.py --watch

# Watch with custom interval
venv/bin/python3 src/main.py --watch --interval 30

# Send status report to Telegram (for cron)
venv/bin/python3 src/main.py --report

# Custom config file
venv/bin/python3 src/main.py --once --config /path/to/config.yaml
```

### Mock Mode (Preview)

To see the TUI in action with realistic sample data without needing an API key:

```bash
venv/bin/python3 src/mock_main.py
```

## Cloud Deployment

### Railway (Recommended - 5 minutes setup)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/new)

1. Click the button above or go to [railway.app](https://railway.app)
2. Deploy from GitHub: `Rodato/openrouter_apikeys_monitor`
3. Add environment variables (see `.env` section above)
4. Set start command: `python3 src/scheduler.py` (for daily reports at 9 AM)

**Cost**: ~$2-3/month (fits in Railway's $5 free tier)

See [deploy/RAILWAY.md](deploy/RAILWAY.md) for detailed instructions.

### VPS (Traditional)

For VPS deployment with cron or systemd, see [deploy/README.md](deploy/README.md).

**Quick start:**

```bash
git clone https://github.com/Rodato/openrouter_apikeys_monitor.git
cd openrouter_apikeys_monitor
pip3 install --user -r requirements.txt
nano .env  # Configure credentials
./deploy/setup_cron.sh  # Setup daily report at 9 AM
python3 src/main.py --report  # Test
```

## Status indicators

| Status | Meaning |
|--------|---------|
| `OK` (green) | Monthly usage below 80% of threshold |
| `⚠ WARNING` (yellow) | Monthly usage between 80–100% of threshold |
| `🔴 ALERT` (red) | Monthly usage exceeded threshold |
| `DISABLED` (magenta) | Key is disabled in OpenRouter |

## Telegram alerts

When `usage_monthly` exceeds `alert_monthly_usd` for a project, a Telegram message is sent. Alerts respect the `cooldown_minutes` setting to avoid spam.

---

⭐ **Star this repo** if you find it useful for managing your AI budgets!
