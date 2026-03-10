@echo off
echo Setting up mobile environment...

cd mobile

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Mobile setup complete!
echo.
echo To activate the environment, run: mobile\venv\Scripts\activate.bat
echo To start the app, run: python mobile\main.py
pause
