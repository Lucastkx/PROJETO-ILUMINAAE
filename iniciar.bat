@echo off
cd /d "%~dp0"
start "Backend" cmd /k "cd backend && call .venv\Scripts\activate && uvicorn app.main:app --reload"
start "App Cidadao" cmd /k "cd web-cidadao && npm run dev"
start "Painel Prefeitura" cmd /k "cd web-prefeitura && npm run dev"
timeout /t 8 >nul
start http://localhost:5173
start http://localhost:5174
