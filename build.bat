@echo off
python -m pip install -r requirements.txt
pyinstaller --onefile --windowed wifi_gui.py