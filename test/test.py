from timerplus.timerplus import TimerPlus

if __name__ == "__main__":
    t = TimerPlus()
    job_container_='csv'
    filepath=r'E:\timer\test\joblist.csv'
    
    t.add_jobs(job_container_, filepath=filepath)
    t.print_jobs()
    t.shutdown()
