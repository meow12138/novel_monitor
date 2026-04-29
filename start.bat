@echo off
echo ====================================
echo  Novel Monitor - 海外爆款小说监控系统
echo ====================================
echo.

echo [1/3] 安装后端依赖...
cd server
pip install -r requirements.txt -q
echo.

echo [2/3] 安装前端依赖...
cd ..\web
call npm install --silent
echo.

echo [3/3] 启动服务...
echo 后端: http://127.0.0.1:8001
echo 前端: http://127.0.0.1:3000
echo API文档: http://127.0.0.1:8001/docs
echo.

cd ..\server
start "Novel Monitor Backend" cmd /c "python run.py"

cd ..\web
start "Novel Monitor Frontend" cmd /c "npm run dev"

echo.
echo 服务已启动，请在浏览器中访问 http://localhost:3000
pause
