import importlib
import os

from timerplus.timerplus import TimerPlus

if __name__ == "__main__":
    t = TimerPlus()

    # job_container_='csv'
    # filepath=r'E:\timerplus\test\joblist.csv'
    # t.add_jobs(job_container_=job_container_, filepath=filepath)

    job_container_='pgsql'
    db_cfg='jtder'
    table='timer_joblist'
    t.add_jobs(job_container_=job_container_, db_cfg=db_cfg, table=table)   

    t.print_jobs()
    t.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
    # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        t.shutdown()
