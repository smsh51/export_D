@ECHO OFF
echo install Divar app

pip install -r requirements.txt
del requirements.txt

mkdir Data
ren __pycache__\main.cpython-311.pyc main.pyc

echo @ECHO off > Run.bat
echo python __pycache__\main.pyc >> Run.bat

echo OK!
del installer.cmd
PAUSE