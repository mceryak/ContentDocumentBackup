from apscheduler.schedulers.blocking import BlockingScheduler
from run_backup import prep_backup

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(func=prep_backup, trigger='cron', day_of_week=1, hour=14, minute=0, second=0)
    scheduler.print_jobs()
    scheduler.start()