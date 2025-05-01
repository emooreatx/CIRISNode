from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cirisnode.matrix.bot import send_audit_root
import asyncio

scheduler = AsyncIOScheduler()

async def daily_audit_task():
    """Task to run daily: hash results and post audit root to Matrix."""
    run_ids = []  # Placeholder for collecting run IDs, to be implemented
    audit_message = await send_audit_root(run_ids)
    print(f"Daily audit completed: {audit_message['sha256']}")

def setup_scheduler():
    """Setup the scheduler with daily audit task."""
    scheduler.add_job(daily_audit_task, 'interval', days=1, start_date='2025-05-01 00:00:00')
    scheduler.start()
    print("Scheduler started with daily audit task.")

if __name__ == "__main__":
    setup_scheduler()
    asyncio.get_event_loop().run_forever()
