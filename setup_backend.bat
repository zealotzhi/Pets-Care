@echo off
echo Setting up backend environment...

cd backend

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Creating data directory...
if not exist "data" mkdir data
if not exist "data\pets" mkdir data\pets
if not exist "data\care" mkdir data\care
if not exist "data\logs" mkdir data\logs

echo Copying environment file...
if not exist ".env" copy .env.example .env

echo Backend setup complete!
echo.
echo To activate the environment, run: backend\venv\Scripts\activate.bat
echo To start the server, run: python backend\app.py
pause
