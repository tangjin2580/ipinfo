<h1 >调用ipinfo查询ip信息后台接口</h1>
<h2>一、环境准备</h2>

- 安装python3.9+
- 安装依赖包
```ssh
pip install -r requirements.txt
```
## 运行
- 启动服务
```ssh
python server/app.py
```
- 访问接口
```ssh
http://127.0.0.1:8080/ipinfo?ip=8.8.8.8
```
- 访问页面
```ssh
http://127.0.0.1:80/
```
<h2>二、打包运行</h2>
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
      
<h2>三、Docker运行</h2>
- 构建镜像
```ssh
docker build -t ipinfo-api .
```
- 运行容器
```ssh
docker run -p 8080:8080 ipinfo-api
``` 
- 访问接口  
```ssh        
http://127.0.0.1:8080/ipinfo?ip=8.8.8.8
```
- 访问页面
```ssh
http://127.0.0.1:80/
```
<h2>四、接口文档</h2>
- 接口地址
```ssh        
http://127.0.0.1:8080/ipinfo?ip=8.8.8.8   
```
- 请求方式
```ssh
GET
```
- 请求参数
```ssh
ip: ip地址
```
- 返回参数
```ssh
{
    "ip": "8.8.8.8",
    "region": "加利福尼亚州",
    "city": "旧金山",
    "org": "Google LLC"
} 
``` 
<h2>五、注意事项</h2>        
- 接口请求频率限制为100次/分钟，超出限制后会返回429 Too Many Requests。
- 接口请求参数ip为必填参数，不能为空。
  - 接口返回参数region、city、org为可选参数，当ip地址无法查询到相关信息时，相应参数返回null。    