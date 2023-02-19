@ECHO OFF
echo install Divar app

pip install -r requirements.txt
mkdir Data

echo python main.pyc > Run.bat

echo OK!
del install.cmd
PAUSE