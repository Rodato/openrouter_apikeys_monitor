#!/usr/bin/env python3
"""
Scheduler for daily Telegram reports.
Sends a report at 9 AM local time every day.
"""
import time
import subprocess
import sys
from datetime import datetime


def main():
    print("🤖 OpenRouter Monitor Scheduler started")
    print(f"   Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Daily reports will be sent at 9:00 AM")
    print()

    last_report_day = -1

    while True:
        now = datetime.now()

        # Send daily report at 9 AM (only once per day)
        if now.hour == 9 and now.day != last_report_day:
            print(f"📊 [{now.strftime('%Y-%m-%d %H:%M:%S')}] Sending daily report...")
            try:
                result = subprocess.run(
                    ["python3", "src/main.py", "--report"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    print(f"✅ Report sent successfully")
                else:
                    print(f"❌ Report failed with code {result.returncode}")
                    print(f"   stdout: {result.stdout}")
                    print(f"   stderr: {result.stderr}")
            except Exception as exc:
                print(f"❌ Exception sending report: {exc}")

            last_report_day = now.day

        # Heartbeat every hour to show we're alive
        if now.minute == 0:
            print(f"💓 [{now.strftime('%H:%M')}] Scheduler alive, next report: tomorrow 9 AM" if now.hour != 9 else f"💓 [{now.strftime('%H:%M')}] Report sent, next: tomorrow 9 AM")

        # Sleep 5 minutes before next check
        time.sleep(300)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Scheduler stopped by user")
        sys.exit(0)
    except Exception as exc:
        print(f"💥 Scheduler crashed: {exc}")
        sys.exit(1)
