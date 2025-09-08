from apscheduler.schedulers.blocking import BlockingScheduler
from .ingest_x import run_once as ingest_x
from .ingest_fb import run_once as ingest_fb
from .import config

def main():
    sched = BlockingScheduler(timezone="UTC")
    sched.add_job(ingest_x, "interval", minutes=config.INGEST_INTERVAL_MIN, id="x_ingest")
    sched.add_job(ingest_fb, "interval", minutes=config.INGEST_INTERVAL_MIN, id="fb_ingest")
    print(f"Scheduler iniciado. Intervalo: {config.INGEST_INTERVAL_MIN}min")
    try:
        sched.start()
    except(KeyboardInterrupt, SystemExit):
        pass

    if __name__ == "__main__":
        main()