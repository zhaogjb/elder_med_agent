@echo off
chcp 65001
echo 正在启动老年用药智能体
cd /d "C:\Users\赵佳豪\Desktop\elder_med_agent"
D:\python\python.exe -m streamlit run app.py
start http://127.0.0.1:8501
pause
