@echo off
setlocal

if not exist .venv (
  python -m venv .venv
)

call .venv\Scripts\activate.bat

pip install -r requirements.txt

if not defined FANPAY_DATA_SOURCE set FANPAY_DATA_SOURCE=mock
if not defined FANPAY_SAMPLE_DATA set FANPAY_SAMPLE_DATA=fanpay_bot/data/sample_data.json

python -m fanpay_bot.web_app
