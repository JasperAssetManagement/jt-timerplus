call activate env_36

python setup.py bdist_wheel --universal

pip uninstall jt.timerplus -y

pip install dist\jt.timerplus-0.1.1-py2.py3-none-any.whl

::twine upload --repository-url http://192.168.1.195:8071/repository/jasperpypi-hosted/ dist\jt.timerplus-0.1.1-py2.py3-none-any.whl -u jasper -p jasper123