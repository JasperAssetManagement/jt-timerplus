"""
timer
@author: Dannie Lei
@Modified by: Neo Lin
@date: 2018-11-11
"""
import os
import json
import datetime
import logging
import math
import matlab.engine
import importlib

from apscheduler.schedulers.background import BackgroundScheduler
from jt.utils.db import PgSQLLoader
from jt.utils.fs.utils import Utils
from jt.utils.misc import read_yaml
from jt.utils.time.format import datetime2string
from jt.utils.calendar.api_calendar import TradeCalendarDB

logging.basicConfig()
calendar=TradeCalendarDB()
JOBTYPE = ['matlab', 'python', 'cmd', 'sqlprocedure']

JobContainer = {
    'csv' : ['filepath'],
    'pgsql' : ['db_cfg', 'table']
}

class TimerPlus(object):

    def __init__(self):
        self._sche = BackgroundScheduler()

    def add_jobs(self, job_container_, **kw):
        """
        define job store
        1. csv: filepath
        2. pgsql: db_cfg, table
        """
        self._job_container = job_container_.lower()

        container_=[k for (k,v) in JobContainer.items()]

        assert self._job_container in container_, f'job_container_ should be in {container_}'
        for arg in JobContainer[self._job_container]:
            assert arg in kw, f'{arg} should be included.'

        if self._job_container == 'csv':
            assert os.path.exists(kw['filepath']), f"{kw['filepath']} is not existed."

            config_dict_ = read_yaml(config_name='cfg/csv.yaml', package='timerplus')
            jobs = Utils.read_csv(kw['filepath'], config_dict_.get('import_data'), **config_dict_.get('config'))

        elif self._job_container == 'pgsql':
            _con = PgSQLLoader(kw['db_cfg'])
            _dbtabale = kw['table']

            jobs = _con.read(f'''select job_id,job_name,job_type,job_args,
                                trigger,trigger_args,is_trade_date,exchange from {_dbtabale}''')
        
        # loop adding job         
        for row in jobs.itertuples(): 
            assert getattr(row, 'job_type') in JOBTYPE, f'job type should be in {JOBTYPE}!'
            if isinstance(getattr(row, 'job_args'), str):
                t_job_args = json.loads(getattr(row, 'job_args'))                
            else: #math.isnan(getattr(row, 'job_args')):
                t_job_args = None
    
            self._sche.add_job(func=self._distributor,
                               args=[getattr(row, 'job_type'), getattr(row, 'job_name'),
                                     t_job_args, getattr(row, 'is_trade_date'),
                                     getattr(row, 'exchange')],
                               trigger=getattr(row, 'trigger'),
                               id=getattr(row, 'job_id'),
                               **json.loads(getattr(row, 'trigger_args')))
 

    def print_jobs(self):
        self._sche.print_jobs()

    def start(self):
        self._sche.start()

    def shutdown(self):
        self._sche.shutdown()


    def _distributor(self, job_type_=None, job_name_=None, job_args_=None, is_trade_date_='n', exchange_='sz'):
        today_ = datetime2string(datetime.datetime.now(), r'%Y%m%d')     

        if is_trade_date_.lower()=='y':            
            if not calendar.is_trading_date(today_, exchange_):
                return            
     
        if job_type_=='matlab':
            self.__matlab_executor(job_name_, job_args_)
        elif job_type_=='python':
            self.__python_executor(job_name_, job_args_)                 
        elif job_type_=='sqlprocedure':             
            self.__sqlprocedure_executor(job_name_, job_args_)
        elif job_type_=='cmd':
            pass


    def __matlab_executor(self, job_name_, job_args_):
        """
        execute the user defined matlab function/scripts
        """
        eng = matlab.engine.start_matlab()
        func = getattr(eng, job_name_)
        assert func is not None, f'job_name : {job_name_} is not found!'
        if job_args_ is None:
            func(nargout=0)
        else:
            func(*job_args_, nargout=0)

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

    def __sqlprocedure_executor(self, job_name_, job_args_):
        assert 'db_env' in job_args_, 'db_env should be in job_args'
        pgl = PgSQLLoader(job_args_.get('db_env'))
        pgl.call_procedure(job_name_, job_args_.get('args', []), job_args_.get('proc_has_return', 'n'))
     