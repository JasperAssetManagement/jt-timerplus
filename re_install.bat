call activate env_36

python setup.py bdist_wheel --universal

pip uninstall jt.timerplus -y

pip install dist\jt.timerplus-0.0.2-py2.py3-none-any.whl