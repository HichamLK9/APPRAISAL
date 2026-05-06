#!/usr/bin/env python3
"""Convenience entry-point: runs the API server.

Usage:
  python -m backend.run                        # API server (production)
  python -m backend.run --collect              # Run one collection now then exit
  python -m backend.run --collect --date 2026-05-01  # Collect for a specific date
"""
import argparse
import datetime as dt
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Entity Radar – run modes")
    parser.add_argument("--collect", action="store_true", help="Run one collection and exit")
    parser.add_argument("--date", default="", help="Target date YYYY-MM-DD (default: today)")
    parser.add_argument("--use-mock", action="store_true", help="Force mock source")
    args = parser.parse_args()

    if args.use_mock:
        import os
        os.environ["ENABLED_SOURCES"] = "mock"

    target = args.date or dt.date.today().isoformat()

    if args.collect:
        from backend.db.database import init_db
        from backend.scheduler.jobs import run_daily_collection
        init_db()
        n = run_daily_collection(target_date=target)
        print(f"Done — {n} new entities stored for {target}.")
        sys.exit(0)

    # Default: start API server
    import uvicorn
    from backend.config import settings
    uvicorn.run(
        "backend.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )


if __name__ == "__main__":
    main()
