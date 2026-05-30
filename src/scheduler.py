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
    print(f"   Reports will be sent at 8:00 AM and 5:00 PM")
    print()

    last_report_morning = -1
    last_report_evening = -1

    while True:
        now = datetime.now()

        # Send morning report at 8 AM
        if now.hour == 8 and now.day != last_report_morning:
            print(f"🌅 [{now.strftime('%Y-%m-%d %H:%M:%S')}] Sending morning report...")
            try:
                result = subprocess.run(
                    ["python3", "src/main.py", "--report"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    print(f"✅ Morning report sent successfully")
                else:
                    print(f"❌ Report failed with code {result.returncode}")
                    print(f"   stdout: {result.stdout}")
                    print(f"   stderr: {result.stderr}")
            except Exception as exc:
                print(f"❌ Exception sending report: {exc}")

            last_report_morning = now.day

        # Send evening report at 5 PM (17:00)
        if now.hour == 17 and now.day != last_report_evening:
            print(f"🌆 [{now.strftime('%Y-%m-%d %H:%M:%S')}] Sending evening report...")
            try:
                result = subprocess.run(
                    ["python3", "src/main.py", "--report"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    print(f"✅ Evening report sent successfully")
                else:
                    print(f"❌ Report failed with code {result.returncode}")
                    print(f"   stdout: {result.stdout}")
                    print(f"   stderr: {result.stderr}")
            except Exception as exc:
                print(f"❌ Exception sending report: {exc}")

            last_report_evening = now.day

        # Heartbeat every hour to show we're alive
        if now.minute == 0:
            next_report = "today 5 PM" if now.hour < 17 else "tomorrow 8 AM"
            if now.hour == 8:
                next_report = "today 5 PM"
            elif now.hour == 17:
                next_report = "tomorrow 8 AM"
            print(f"💓 [{now.strftime('%H:%M')}] Scheduler alive, next report: {next_report}")

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
