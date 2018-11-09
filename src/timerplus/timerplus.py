#
# timer.py
# @author Neo Lin
# @description Create a scheduler
# @created Wed Nov 07 2018 13:40:34 GMT+0800 (中国标准时间)
# @last-modified Wed Nov 07
#
import os
import json
import datetime
import logging
import matlab.engine
import importlib

from apscheduler.schedulers.background import BackgroundScheduler
from enum import Enum
from jt.utils.db import PgSQLLoader
from jt.utils.fs.utils import Utils
from jt.utils.misc import read_yaml
from jt.utils.misc.log import Logger
from jt.utils.time.format import datetime2string
from jt.utils.calendar.api_calendar import TradeCalendarDB

logger = Logger(module_name_='timer')
logger._log.setLevel(logging.DEBUG)
calendar=TradeCalendarDB()
JOBTYPE = ['matlab', 'python', 'cmd']

class JobContainer(Enum):
    csv = ['filepath']
    pgsql = ['db_cfg', 'table']


class TimerPlus(object):

    def __init__(self):
        self._sche = BackgroundScheduler(logger=logger)

    def add_jobs(self, job_container_, **kw):
        """
        define job store
        1. csv: filepath
        2. pgsql: db_cfg
        """
        self._job_container = job_container_.lower()

        assert self._job_container in [jobcon.name for jobcon in JobContainer], f'job_container_ should be in {[jobcon.name for jobcon in JobContainer]}'
        for arg in JobContainer[self._job_container].value:
            assert arg in kw, f'{arg} should be included.'

        if self._job_container == 'csv':
            assert os.path.exists(kw['filepath']), f"{kw['filepath']} is not existed."

            config_dict_ = read_yaml(config_name='cfg/csv.yaml', package='timer')
            jobs = Utils.read_csv(kw['filepath'], config_dict_.get('import_data'), **config_dict_.get('config'))

        elif self._job_container == 'pgsql':
            _con = PgSQLLoader(kw['db_cfg'])
            _dbtabale = kw['table']

            jobs = _con.read(f'''select job_id,job_name,job_type,job_args,job_address,
                                triggers,trigger_args,is_trade_date,market from {_dbtabale}''')
        
        # loop adding job         
        for row in jobs.itertuples(): 
            assert getattr(row, 'job_type') in JOBTYPE, f'job type should be in {JOBTYPE}!'
            print(getattr(row, 'job_id'))
            print(getattr(row, 'job_args'))            
            self._sche.add_job(func=self._distributor,
                               args=[getattr(row, 'job_type'), getattr(row, 'job_name'),
                                     json.loads(getattr(row, 'job_args')), getattr(row, 'is_trade_date'),
                                     getattr(row, 'exchange')],
                               trigger=getattr(row, 'trigger'),
                               id=getattr(row, 'job_id'),
                               #   hour='14', minute='50', second='0')
                               **json.loads(getattr(row, 'trigger_args')))
 

    def print_jobs(self):
        self._sche.print_jobs()

    def shutdown(self):
        self._sche.shutdown()


    def _distributor(self, job_type_=None, job_name_=None, job_args_=None, is_trade_date_='N', exchange_='sz'):        
        today_ = datetime2string(datetime.datetime.now(), r'%Y%m%d')

        if is_trade_date_=='Y':            
            if ~calendar.is_trading_date(today_, exchange_):
                return
            
        if job_type_=='matlab':
            self.__matlab_executor(job_name_, job_args_)
        elif job_type_=='python':
            self.__python_executor(job_name_, job_args_)                 
        elif job_type_=='sqlprocedure':
            pass
        elif job_type_=='cmd':
            pass


    def __matlab_executor(self, job_name_, job_args_):         
        """
        execute the user defined matlab function
        """       
        eng = matlab.engine.start_matlab(async=True)
        func = getattr(eng, job_name_)
        assert func is not None, f'job_name : {job_name_} is not found!'
        func(job_args_)
        eng.quit()

    def __python_executor(self, job_name_, job_args_):
        assert isinstance(job_name_, str), 'job_name_ should be a String!'
        
        module_name = job_name_[0:job_name_.rfind('.')]
        spec = importlib.util.find_spec(module_name)
        assert spec is not None, f'job_name : {job_name_} is not found!'
        
        module = importlib.util.module_from_spec(spec)
        func_name = job_name_[job_name_.rfind('.'):len(job_name_)]
        func = getattr(module, func_name)
        assert func is not None, f'job_name : {job_name_} is not found!'
        assert hasattr(func, '__call__'), f'{job_name_} is not callable!'

        func(**job_args_)     
    
    def __cmd_executor(self, *args, **kw):
        pass

    def __sqlprocedure_executor(self, *args, **kw):
        pass
