const STORAGE_KEY = "hostTarget";
const CONNECT_TIMEOUT = 2500;
const SEND_TIMEOUT = 4000;

function parsePayload(text) {
  const raw = String(text || "").trim();
  if (!raw) {
    throw new Error("内容为空");
  }
  if (raw.startsWith("{")) {
    let data;
    try {
      data = JSON.parse(raw);
    } catch (e) {
      throw new Error("二维码内容格式错误");
    }
    const port = Number(data.port);
    if (!port) {
      throw new Error("二维码缺少端口");
    }
    let ips = data.ips;
    if (!Array.isArray(ips) || !ips.length) {
      ips = data.ip ? [data.ip] : [];
    }
    ips = ips.filter((ip) => typeof ip === "string" && /^\d{1,3}(\.\d{1,3}){3}$/.test(ip));
    if (!ips.length) {
      throw new Error("二维码缺少有效 IP");
    }
    return { name: data.name || "电脑", port, ips };
  }
  const match = raw.match(/^(\d{1,3}(?:\.\d{1,3}){3})(?::(\d+))?$/);
  if (match) {
    return { name: match[1], port: Number(match[2] || 47653), ips: [match[1]] };
  }
  throw new Error("请扫描电脑端二维码，或输入 IP:端口");
}

function request(options, timeout) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("连接超时")), timeout);
    wx.request({
      ...options,
      timeout,
      success(res) {
        clearTimeout(timer);
        resolve(res);
      },
      fail(err) {
        clearTimeout(timer);
        reject(new Error(err && err.errMsg ? err.errMsg : "网络错误"));
      }
    });
  });
}

async function pingHost(ip, port) {
  const res = await request(
    { url: "http://" + ip + ":" + port + "/ping", method: "GET", dataType: "json" },
    CONNECT_TIMEOUT
  );
  if (res.statusCode !== 200 || !res.data || res.data.service !== "WeChat-Barcode-Scanner") {
    throw new Error("目标不是扫码接收端");
  }
  return res.data;
}

async function findReachableHost(target) {
  const errors = [];
  for (let i = 0; i < target.ips.length; i += 1) {
    const ip = target.ips[i];
    try {
      const info = await pingHost(ip, target.port);
      return { ip, port: target.port, name: info.device || target.name, deviceId: info.id };
    } catch (e) {
      errors.push(ip + "：" + e.message);
    }
  }
  throw new Error("无法连接任何地址\n" + errors.join("\n"));
}

function saveTarget(host) {
  wx.setStorageSync(STORAGE_KEY, { host });
}

function loadTarget() {
  const saved = wx.getStorageSync(STORAGE_KEY);
  return saved && saved.host ? saved.host : null;
}

function clearTarget() {
  wx.removeStorageSync(STORAGE_KEY);
}

function sendCode(host, code) {
  const seq = String(Date.now()) + "-" + Math.random().toString(36).slice(2, 8);
  return request(
    {
      url: "http://" + host.ip + ":" + host.port + "/scan",
      method: "POST",
      header: { "content-type": "application/json" },
      dataType: "json",
      data: { code, seq }
    },
    SEND_TIMEOUT
  );
}

module.exports = {
  parsePayload,
  findReachableHost,
  saveTarget,
  loadTarget,
  clearTarget,
  sendCode
};
