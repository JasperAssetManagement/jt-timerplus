call activate env_36

python setup.py bdist_wheel --universal

pip uninstall timerplus -y

pip install dist\timerplus-0.0.1-py2.py3-none-any.whl