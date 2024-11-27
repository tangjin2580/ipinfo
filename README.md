调用ipinfo查询ip信息后台接口
- 打包
```ssh
pyinstaller --onefile --add-data "./server/.env:." ./server/app.py
```
- 运行
  - linux/macos
    - ```ssh
      ./server/dist/app
  - windows
    - ```cmd
       ./server/dist/app.exe
    