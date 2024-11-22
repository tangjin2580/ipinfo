// 使用第三方IP定位服务API获取IP信息
fetch("https://ipapi.co/json/")
    .then(response => response.json())
    .then(data => {
        document.getElementById("ip").textContent = "IP: " + data.ip;
        document.getElementById("location").textContent = "Location: " + data.city + ", " + data.region + ", " + data.country;
    });