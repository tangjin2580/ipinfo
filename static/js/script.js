async function fetchLocalIP() {
    try {
        const response = await fetch('https://api.ipify.org?format=json');
        if (!response.ok) {
            throw new Error('无法获取本地 IP 地址');
        }
        const data = await response.json();
        return data.ip;  // 返回 IP 地址
    } catch (error) {
        console.error(error);
        return null;  // 返回 null 如果失败
    }
}

function getSystemInfo() {
    const userAgent = navigator.userAgent;
    return userAgent; // 返回 userAgent 中的系统信息（可以做进一步解析）
}



async function queryIP(ipInput) {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const resolvedIPsContainer = document.getElementById('resolvedIPsContainer');
    const dnsInput = document.getElementById('dnsInput').value.trim() || "8.8.8.8"; // 获取自定义 DNS，若未填则使用默认
    const serverInput = document.getElementById('serverInput').value.trim() || "http://192.168.0.105:8080"; // 获取服务器地址

    loading.style.display = 'block';
    error.style.display = 'none';
    resolvedIPsContainer.innerHTML = ''; // 清空已显示的结果

    try {
        let ips = [];

        // 判断输入是 IP 地址还是域名
        if (ipInput.includes('.')) { // 判断是否为 IP 地址
            ips.push(ipInput); // 将其视为有效 IP
        } else {
            // 输入为域名，进行解析
            const resolvedIPs = await resolveDomain(ipInput, dnsInput,serverInput); // 传递 DNS 服务器
            if (resolvedIPs) {
                ips = resolvedIPs; // 获取到解析结果
            } else {
                throw new Error('未能解析域名'); // 如果解析结果为空，抛出错误
            }
        }
        async function resolveDomain(domain, dnsServer) {
            try {
                const response = await fetch(`http://127.0.0.1:8080/api/resolve/${domain}?dns=${dnsServer}`);
                if (!response.ok) {
                    throw new Error('无法解析域名');
                }
                const data = await response.json();
                return data.ip;  // 返回解析出的 IP 地址数组
            } catch (error) {
                console.error(error);
                return null;  // 返回 null 如果失败
            }
        }
        // 收集信息并显示在页面
        for (const ip of ips) {
            const response = await fetch(`${serverInput}/api/ipinfo/${ip}`);
            if (!response.ok) {
                throw new Error('无法获取 IP 信息');
            }
            const jsonResponse = await response.json();

            jsonResponse.forEach(info => {
                // 创建一个新的盒子用于展示该 IP 的信息
                const ipBox = document.createElement('div');
                ipBox.className = 'ip-info-box';
                ipBox.innerHTML = `
                    <p>您查询的信息: <strong>${info.ip}</strong></p>
                    <p>国家: <span>${info.country || '未知'}</span></p>
                    <p>城市: <span>${info.city || '未知'}</span></p>
                `;
                resolvedIPsContainer.appendChild(ipBox);
            });
        }
    } catch (err) {
        error.textContent = err.message;
        error.style.display = 'block';
    } finally {
        loading.style.display = 'none';
    }
}

window.onload = async () => {
    const localIPElement = document.getElementById('localIP');
    const localIP = await fetchLocalIP();

    if (localIP) {
        localIPElement.textContent = localIP;  // 显示本地 IP
    }
    startClock(); // 启动时钟
};

function startClock() {
    const clockElement = document.getElementById('clock');
    setInterval(() => {
        const now = new Date();
        clockElement.textContent = now.toLocaleTimeString(); // 显示时钟
    }, 1000);
}

document.getElementById('fetchBtn').addEventListener('click', async () => {
    const ipInput = document.getElementById('ipInput').value;
    await queryIP(ipInput); // 查询域名或 IP
});
