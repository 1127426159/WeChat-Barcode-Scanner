const hostUtil = require("../../utils/host.js");
const LOCAL_ONLY_KEY = "scannerLocalOnly";

Page({
  data: {
    connected: false,
    connecting: false,
    hostName: "",
    hostIp: "",
    lastCode: "",
    lastStatus: "",
    lastStatusType: "",
    history: [],
    manualInput: "",
    showManual: false,
    sendCount: 0,
    localOnly: false
  },

  onLoad() {
    if (wx.getStorageSync(LOCAL_ONLY_KEY)) {
      this.setData({
        localOnly: true,
        lastStatus: "离线模式：扫码后不会发送到电脑",
        lastStatusType: "info"
      });
      return;
    }
    const saved = hostUtil.loadTarget();
    if (saved) {
      this.setData({
        hostName: saved.name || "电脑",
        hostIp: saved.ip + ":" + saved.port
      });
      this.connect(saved, true);
    }
  },

  async connect(target, silent) {
    if (this.data.connecting) {
      return;
    }
    wx.removeStorageSync(LOCAL_ONLY_KEY);
    this.setData({
      localOnly: false,
      connecting: true,
      lastStatus: silent ? "正在重连…" : "正在查找电脑…",
      lastStatusType: "info"
    });
    try {
      const host = await hostUtil.findReachableHost(target);
      hostUtil.saveTarget(host);
      const app = getApp();
      if (app) {
        app.globalData.target = host;
      }
      this.setData({
        connected: true,
        connecting: false,
        hostName: host.name,
        hostIp: host.ip + ":" + host.port,
        lastStatus: "已连接 " + host.name,
        lastStatusType: "ok"
      });
    } catch (e) {
      this.setData({
        connected: false,
        connecting: false,
        lastStatus: e.message,
        lastStatusType: "error"
      });
    }
  },

  scanHostQr() {
    wx.scanCode({
      onlyFromCamera: false,
      scanType: ["qrCode"],
      success: (res) => {
        let target;
        try {
          target = hostUtil.parsePayload(res.result);
        } catch (e) {
          wx.showModal({ title: "二维码无效", content: e.message, showCancel: false });
          return;
        }
        this.setData({ showManual: false });
        this.connect(target, false);
      }
    });
  },

  openHelp() {
    wx.navigateTo({ url: "/pages/help/help" });
  },

  useLocalMode() {
    hostUtil.clearTarget();
    const app = getApp();
    if (app) {
      app.globalData.target = null;
    }
    wx.setStorageSync(LOCAL_ONLY_KEY, true);
    this.setData({
      localOnly: true,
      connected: false,
      connecting: false,
      hostName: "",
      hostIp: "",
      lastStatus: "离线模式：扫码后不会发送到电脑",
      lastStatusType: "info"
    });
  },

  enableComputerMode() {
    wx.removeStorageSync(LOCAL_ONLY_KEY);
    this.setData({
      localOnly: false,
      lastStatus: "请连接电脑",
      lastStatusType: "info"
    });
  },

  toggleManual() {
    this.setData({ showManual: !this.data.showManual });
  },

  onManualInput(e) {
    this.setData({ manualInput: e.detail.value });
  },

  connectManual() {
    let target;
    try {
      target = hostUtil.parsePayload(this.data.manualInput);
    } catch (e) {
      wx.showToast({ title: e.message, icon: "none" });
      return;
    }
    this.connect(target, false);
  },

  disconnect() {
    hostUtil.clearTarget();
    wx.removeStorageSync(LOCAL_ONLY_KEY);
    const app = getApp();
    if (app) {
      app.globalData.target = null;
    }
    this.setData({
      connected: false,
      localOnly: false,
      hostName: "",
      hostIp: "",
      lastStatus: "已断开",
      lastStatusType: "info"
    });
  },

  scanOnce() {
    wx.scanCode({
      onlyFromCamera: false,
      scanType: ["barCode", "qrCode", "datamatrix", "pdf417"],
      success: (res) => {
        this.handleCode(res.result, res.scanType);
      },
      fail: () => {}
    });
  },

  async handleCode(code, scanType) {
    const text = String(code || "").trim();
    if (!text) {
      return;
    }
    wx.vibrateShort({ type: "light" });

    if (this.data.localOnly) {
      this.setData({
        lastCode: text,
        lastStatus: "已记录（未发送到电脑）",
        lastStatusType: "ok",
        sendCount: this.data.sendCount + 1
      });
      this.pushHistory(text, scanType, true);
      return;
    }

    this.setData({ lastCode: text, lastStatus: "发送中…", lastStatusType: "info" });

    const host = hostUtil.loadTarget();
    if (!host) {
      this.setData({ lastStatus: "尚未连接电脑", lastStatusType: "error" });
      return;
    }

    try {
      const res = await hostUtil.sendCode(host, text);
      const data = res.data || {};
      if (res.statusCode === 200 && data.ok) {
        this.setData({
          lastStatus: data.duplicate ? "已忽略重复条码" : "已发送到电脑",
          lastStatusType: "ok",
          sendCount: this.data.sendCount + 1
        });
        this.pushHistory(text, scanType, true);
      } else {
        this.setData({
          lastStatus: data.error || "发送失败",
          lastStatusType: "error"
        });
        this.pushHistory(text, scanType, false);
        if (data.needs_admin) {
          wx.showModal({
            title: "电脑端需要管理员权限",
            content: data.error,
            showCancel: false
          });
        }
      }
    } catch (e) {
      this.setData({ lastStatus: "连接中断：" + e.message, lastStatusType: "error" });
      this.pushHistory(text, scanType, false);
      this.connect(host, true);
    }
  },

  pushHistory(code, scanType, ok) {
    const item = {
      code,
      type: scanType || "",
      ok,
      time: this.formatTime(new Date())
    };
    const history = [item].concat(this.data.history).slice(0, 30);
    this.setData({ history });
  },

  formatTime(date) {
    const pad = (n) => (n < 10 ? "0" + n : String(n));
    return pad(date.getHours()) + ":" + pad(date.getMinutes()) + ":" + pad(date.getSeconds());
  },

  copyHistory() {
    if (!this.data.history.length) {
      wx.showToast({ title: "暂无记录", icon: "none" });
      return;
    }
    const text = this.data.history.map((it) => it.code).join("\n");
    wx.setClipboardData({ data: text });
  },

  clearHistory() {
    this.setData({ history: [], sendCount: 0 });
  }
});
