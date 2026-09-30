"""Entry point.  python main.py            -> menu
                python main.py --schedule -> automatic daily email"""
import sys
import time
from datetime import datetime

try:
    import schedule # pyright: ignore[reportMissingImports]
except ImportError:  # pragma: no cover - fallback for environments without the package
    class _FallbackJob:
        def __init__(self, scheduler, interval=1):
            self.scheduler = scheduler
            self.interval = interval
            self.unit = "minutes"
            self.at_time = None
            self.func = None

        def minutes(self):
            self.unit = "minutes"
            return self

        def day(self):
            self.unit = "day"
            return self

        def at(self, time_value):
            self.at_time = time_value
            return self

        def do(self, func):
            self.func = func
            self.scheduler.jobs.append(self)
            self._schedule_next_run()
            return self

        def _schedule_next_run(self):
            now = datetime.now()
            if self.unit == "day":
                if self.at_time:
                    hour, minute = map(int, self.at_time.split(":"))
                    next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if next_run <= now:
                        next_run = next_run.replace(day=next_run.day + 1)
                else:
                    next_run = now
            else:
                next_run = now
            self.next_run = next_run

        def should_run(self, now):
            if self.unit == "day":
                if self.at_time is None:
                    return False
                hour, minute = map(int, self.at_time.split(":"))
                return now.hour == hour and now.minute == minute and now.second < 30
            return (now - self.next_run).total_seconds() >= 0

        def run(self):
            if self.func is not None:
                self.func()
                self._schedule_next_run()

    class _FallbackScheduler:
        def __init__(self):
            self.jobs = []

        def every(self, interval=1):
            return _FallbackJob(self, interval)

        def run_pending(self):
            now = datetime.now()
            for job in list(self.jobs):
                if job.should_run(now):
                    job.run()

    schedule = _FallbackScheduler()

from api_client import get_weather, get_news
from scraper import scrape_quotes
from dashboard import build_dashboard
from emailer import send_email
from utils import log


def job():
    """The automated task: build dashboard and email it."""
    report = build_dashboard()
    ok = send_email("Your Daily Dashboard", report)
    print("Email sent" if ok else "Email failed - see automation.log")


def run_scheduler():
    schedule.every().day.at("08:00").do(job)
    # For testing use: schedule.every(1).minutes.do(job)
    print("Scheduler running (daily 08:00). Ctrl+C to stop.")
    log.info("Scheduler started")
    while True:
        schedule.run_pending()
        time.sleep(30)


def menu():
    while True:
        print("\n1) Weather  2) News  3) Scrape quotes  4) Full dashboard"
              "\n5) Email dashboard  6) Start scheduler  0) Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            print(get_weather(input("City: ").strip() or "Lahore") or "Not available")
        elif choice == "2":
            for n in get_news(5):
                print("-", n["title"])
        elif choice == "3":
            for q in scrape_quotes(5):
                print(f"\"{q['text']}\" - {q['author']}")
        elif choice == "4":
            print(build_dashboard())
        elif choice == "5":
            job()
        elif choice == "6":
            run_scheduler()
        elif choice == "0":
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    run_scheduler() if "--schedule" in sys.argv else menu()
