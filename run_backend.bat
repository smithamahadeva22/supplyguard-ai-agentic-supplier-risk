@echo off
cd /d %~dp0
call .venv\Scripts\activate
uvicorn app.api.main:app --reload --port 8000
