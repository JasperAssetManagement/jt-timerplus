"""
@author Neo
@time 2018/11/06
"""

from setuptools import setup, find_packages

setup(
    name='timer',
    version='0.0.1',
    description="timer",
    author='Neo',
    author_email='neo.lin@jaspercapital.com',
    # namespace_packages=['jt'],
    packages=find_packages('src'),
    package_dir={"": "src"},
    package_data={
        'timer': [
            'cfg/*.yaml',           
          
        ]        
    },
    install_requires=[  
        'apscheduler',
        'jt'
    ],
    zip_safe=False,
)
