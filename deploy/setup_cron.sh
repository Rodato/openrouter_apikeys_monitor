#!/bin/bash
# Setup cron for daily Telegram reports
# Run this on your VPS after deploying

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Daily report at 9 AM
CRON_LINE="0 9 * * * cd $PROJECT_DIR && python3 src/main.py --report >> $PROJECT_DIR/logs/cron.log 2>&1"

# Add to crontab if not already present
(crontab -l 2>/dev/null | grep -v "openrouterMonitor"; echo "$CRON_LINE") | crontab -

echo "✅ Cron job configured: daily report at 9:00 AM"
echo "Logs will be written to: $PROJECT_DIR/logs/cron.log"

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"
