#
# timer.py
# @author Neo Lin
# @description Create a scheduler
# @created Wed Nov 07 2018 13:40:34 GMT+0800 (中国标准时间)
# @last-modified Wed Nov 07
#
import os
import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from enum import Enum
from jt.utils.db import PgSQLLoader
from jt.utils.fs.utils import Utils
from jt.utils.misc import read_yaml
from jt.utils.misc.log import Logger
from jt.utils.time.format import datetime2string
from jt.utils.calendar.api_calendar import TradeCalendarDB


class Jobstore(Enum):
    csv = ['file']
    pgsql = ['db_cfg', 'table']


class Timer(object):

    def __init__(self):
        self._sche = BackgroundScheduler()

    def add_jobs(self, jobstore_, **kw):
        """
        define job store
        1. csv: file
        2. pgsql: db_cfg
        """
        self._jobstore = jobstore_.lower()

        assert self._jobstore in [
            js.name for js in Jobstore], f'jobstore_ should be in {[js.name for js in Jobstore]}'
        for arg in Jobstore[self._jobstore].value:
            assert arg in kw, f'{arg} should be included.'

        if self._jobstore == 'csv':
            assert os.path.exists(kw['file']), f"{kw['file']} is not existed."

            config_dict_ = read_yaml(config_name='cfg/csv.yaml', package='timer')
            jobs = Utils.read_csv(kw['file'], config_dict_.get('import_data'), **config_dict_.get('config'))

        elif self._jobstore == 'pgsql':
            _con = PgSQLLoader(kw['db_cfg'])
            _dbtabale = kw['table']

            jobs = _con.read(f'''select job_id,job_name,job_type,job_args,job_address,
                                triggers,trigger_args,is_trade_date,market from {_dbtabale}''')
        
        # loop adding job 
        for index, row in jobs.iterrows():
            pass
    
    def __executor(self):
        pass

    def _distributor(ftype=None, address=None, f_matlab=None, func=None, *args):
        today_ = datetime2string(datetime.datetime.now(),r'%Y%m%d')
        
        if TradeCalendar_api().is_trading_date(date):
            print('jyr')
            if ftype=='matlab':
                pythoncom.CoInitialize()#多线程
                h = Dispatch("Matlab.application")
                h.execute(address)
                h.execute("ans={}".format(f_matlab))
                print(h.GetVariable("ans", "base"))
            else:
                func(*args)

