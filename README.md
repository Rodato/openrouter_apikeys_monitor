# openrouterMonitor

Terminal UI to monitor costs and usage across multiple OpenRouter API keys, with Telegram alerts when spending exceeds thresholds.

## Setup

### 1. Install dependencies

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```
OPENROUTER_MANAGEMENT_KEY=sk-or-v1-...   # From openrouter.ai/settings/keys (Management Key)
TELEGRAM_BOT_TOKEN=...                    # Optional: from @BotFather
TELEGRAM_CHAT_ID=...                      # Optional: your chat/group ID
REFRESH_INTERVAL=60                       # Seconds between refreshes in --watch mode
```

### 3. Configure projects

```bash
cp config.yaml.example config.yaml
```

Edit `config.yaml` — the `key_name` must exactly match the **name** field of your API key in OpenRouter:

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

# Custom config file
venv/bin/python3 src/main.py --once --config /path/to/config.yaml
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

To get your `TELEGRAM_CHAT_ID`, send a message to your bot and visit:
`https://api.telegram.org/bot<TOKEN>/getUpdates`
