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

logger = Logger(module_name_='timer')
calendar=TradeCalendarDB()

class JobContainer(Enum):
    csv = ['file']
    pgsql = ['db_cfg', 'table']

JOBTYPE = ['matlab', 'python', 'cmd']

class Timer(object):

    def __init__(self):
        self._sche = BackgroundScheduler(logger=logger)

    def add_jobs(self, job_container_, **kw):
        """
        define job store
        1. csv: file
        2. pgsql: db_cfg
        """
        self._job_container = job_container_.lower()

        assert self._job_container in [
            js.name for js in JobContainer], f'job_container_ should be in {[js.name for js in JobContainer]}'
        for arg in JobContainer[self._job_container].value:
            assert arg in kw, f'{arg} should be included.'

        if self._job_container == 'csv':
            assert os.path.exists(kw['file']), f"{kw['file']} is not existed."

            config_dict_ = read_yaml(config_name='cfg/csv.yaml', package='timer')
            jobs = Utils.read_csv(kw['file'], config_dict_.get('import_data'), **config_dict_.get('config'))

        elif self._job_container == 'pgsql':
            _con = PgSQLLoader(kw['db_cfg'])
            _dbtabale = kw['table']

            jobs = _con.read(f'''select job_id,job_name,job_type,job_args,job_address,
                                triggers,trigger_args,is_trade_date,market from {_dbtabale}''')
        
        # loop adding job 
        for row in jobs.itertuples(): 
            assert getattr(row, 'job_type') in JOBTYPE, f'job type should be in {JOBTYPE}!'
            self._sche.add_job(func=self._distributor(job_type_=getattr(row, 'job_type'), job_address_=getattr(row, 'job_address'),
                                                      job_name_=getattr(row, 'job_name'), job_args_=getattr(row, 'job_args')), 
                                                      trigger=getattr(row, 'trigger'), id=getattr(row, 'job_id'), **eval(getattr(row, 'trigger_args')))   
 

    def _distributor(self, job_type_=None, job_address_=None, job_name_=None, job_args_=None, is_trade_date_='N', exchange_='sz'):
        today_ = datetime2string(datetime.datetime.now(), r'%Y%m%d')
        
        if is_trade_date_=='Y':            
            if calendar.is_trading_date(today_, exchange_):
                if job_type_=='matlab':
                    self.__matlab_executor(job_address_, job_name_, job_args_)
                elif job_type_=='python':
                    pass
                elif job_type_=='sqlprocedure':
                    pass
                elif job_type_=='cmd':
                    pass


    def __matlab_executor(self, *args, **kw):
        pass
    
    def __cmd_executor(self, *args, **kw):
        pass

    def __sqlprocedure_executor(self, *args, **kw):
        pass