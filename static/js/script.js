// 异步函数，用于解析域名并获取 IP 地址

async function queryIP(ipInput) {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const resolvedIPsContainer = document.getElementById('resolvedIPsContainer');
    const dnsInput = document.getElementById('dnsInput').value.trim() || "8.8.8.8"; // 获取自定义 DNS，若未填则使用默认
    const serverInput = document.getElementById('serverInput').value.trim() || "http://127.0.0.1:8080"; // 获取服务器地址

    console.log(`用户输入: ${ipInput}`); // 打印用户输入的 IP 地址或域名
    console.log(`自定义 DNS: ${dnsInput}`); // 打印自定义 DNS
    console.log(`后端服务器地址: ${serverInput}`); // 打印后端服务器地址

    loading.style.display = 'block';
    error.style.display = 'none';
    resolvedIPsContainer.innerHTML = ''; // 清空已显示的结果

    try {
        let ips = [];

        // 判断输入是 IP 地址还是域名
// 正则表达式用于匹配 IPv4 地址
        const ipPattern = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;

        if (ipPattern.test(ipInput)) {
            ips.push(ipInput); // 将其视为有效 IP
        } else {
            // 输入为域名，进行解析
            const resolvedIPs = await resolveDomain(ipInput, dnsInput, serverInput); // 传递 DNS 服务器
            if (resolvedIPs) {
                ips = resolvedIPs; // 获取到解析结果
            } else {
                throw new Error('未能解析域名'); // 如果解析结果为空，抛出错误
            }
        }
        async function resolveDomain(domain, dns_server, serverInput) {
            console.log(`解析域名: ${domain} 使用 DNS: ${dns_server}，服务器: ${serverInput}`); // 打印解析信息
            try {
                const response = await fetch(`${serverInput}/api/resolve/${domain}?dns=${dns_server}`);
                if (!response.ok) {
                    throw new Error('无法解析域名');
                }
                const data = await response.json();
                console.log(`解析结果: ${JSON.stringify(data)}`); // 打印解析结果
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
            console.log(`获取到 IP 信息: ${JSON.stringify(jsonResponse)}`); // 打印获取到的 IP 信息

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
        console.error('查询 IP 发生错误:', err); // 打印查询错误信息
        error.style.display = 'block';
    } finally {
        loading.style.display = 'none';
    }
}

window.onload = async () => {
    const localIPElement = document.getElementById('localIP');

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

function clearDns() {
    document.getElementById('dnsInput').value = ''; // 清空 DNS 输入框
}

function clearIp() {
    document.getElementById('ipInput').value = ''; // 清空 IP 输入框
}

function displayResult(data) {
    const resultContainer = document.getElementById('results');
    const resultItem = document.createElement('div');
    resultItem.classList.add('result-item'); // 添加样式类
    resultItem.innerHTML = data; // 根据需要进行数据填充
    resultContainer.appendChild(resultItem);
}

document.getElementById('fetchBtn').onclick = function() {
    const ip = document.getElementById('ipInput').value;
    // 这里应该添加实际的查询逻辑，调用后端 API
    // 然后将结果通过 displayResult(data) 添加到结果容器

    // 示例添加静态数据
    displayResult(`查询结果内容 ${Math.random()}`); // 示例，用随机数模拟数据
};

document.getElementById('fetchBtn').onclick = function() {
    const ip = document.getElementById('ipInput').value;

    // 清空之前的结果
    const resultContainer = document.getElementById('results');
    resultContainer.innerHTML = '';

    // 这里应该添加实际的查询逻辑，调用后端 API
    // 然后将结果通过 displayResult(data) 添加到结果容器

    // 示例添加静态数据
    displayResult(`查询结果内容 ${Math.random()}`); // 示例，用随机数模拟数据
};

// 主题切换功能
document.getElementById('themeToggle').onclick = function() {
    const body = document.body;
    const containers = document.querySelectorAll('.container');
    body.classList.toggle('dark-mode');
    containers.forEach(container => {
        container.classList.toggle('dark-mode');
    });

    if (body.classList.contains('dark-mode')) {
        body.style.backgroundImage = `url(https://api.suyanw.cn/api/ys.php)`;
    } else {
        body.style.backgroundImage = "url(https://picsum.photos/1920/1080/?random)";
    }
};