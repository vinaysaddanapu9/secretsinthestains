from apscheduler.schedulers.background import BackgroundScheduler
from database.db import get_connection

def update_expired_webinars():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE webinars
                SET status='Expired'
                WHERE status='Active'
                  AND (webinar_date::timestamp + webinar_time) <= CURRENT_TIMESTAMP
            """)
        conn.commit()
    print("Scheduler executed successfully.")

def start_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        update_expired_webinars,
        trigger="interval",
        minutes=5
    )

    #scheduler.add_job(
        #update_expired_webinars,
        #trigger="interval",
        #minutes=1
    #)

    scheduler.start()