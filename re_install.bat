call activate env_36

python setup.py bdist_wheel --universal

pip uninstall jt -y

pip install dist\jt-0.0.2-py2.py3-none-any.whl