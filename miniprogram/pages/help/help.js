const GITHUB_URL = "https://github.com/1127426159/WeChat-Barcode-Scanner";
const AUTHOR_EMAIL = "wechat_scanner@163.com";
const MAC_START_COMMAND = [
  "xattr -dr com.apple.quarantine .",
  "chmod +x START-FOR-MAC.command start-mac.command start.sh setup_env.sh",
  "sh START-FOR-MAC.command"
].join("\n");
const SERVER_PACKAGE_BASE64 = require("../../assets/server/package-data.js");

const SERVER_PACKAGE = {
  fileName: "WeChat-Barcode-Scanner.zip"
};

Page({
  data: {
    githubUrl: GITHUB_URL,
    authorEmail: AUTHOR_EMAIL,
    macStartCommand: MAC_START_COMMAND,
    sharing: ""
  },

  shareServerPackage() {
    const item = SERVER_PACKAGE;
    if (typeof wx.shareFileMessage !== "function") {
      wx.showModal({
        title: "微信版本过低",
        content: "请升级微信后再转发。也可以复制 GitHub 地址，在电脑上打开并下载。",
        showCancel: false
      });
      return;
    }
    if (typeof wx.base64ToArrayBuffer !== "function") {
      wx.showModal({
        title: "微信版本过低",
        content: "请升级微信后再转发。",
        showCancel: false
      });
      return;
    }

    this.setData({ sharing: true });
    try {
      const fs = wx.getFileSystemManager();
      const localPath = wx.env.USER_DATA_PATH + "/" + item.fileName;
      const packageData = wx.base64ToArrayBuffer(SERVER_PACKAGE_BASE64);
      fs.writeFileSync(localPath, packageData);

      wx.shareFileMessage({
        filePath: localPath,
        fileName: item.fileName,
        success: () => {
          this.setData({ sharing: false });
          wx.showModal({
            title: "转发完成",
            content: "在电脑微信中打开“文件传输助手”，点击这个文件并下载。",
            showCancel: false
          });
        },
        fail: (err) => {
          this.setData({ sharing: false });
          const message = err && err.errMsg ? err.errMsg : "转发失败";
          wx.showModal({
            title: "暂时无法转发",
            content: message + "\n请确认在手机微信中使用，并允许发送文件。",
            showCancel: false
          });
        }
      });
    } catch (err) {
      this.setData({ sharing: false });
      wx.showModal({
        title: "文件准备失败",
        content: (err && err.message) || "请升级小程序后重试。",
        showCancel: false
      });
    }
  },

  copyGithub() {
    wx.setClipboardData({ data: GITHUB_URL });
  },

  copyEmail() {
    wx.setClipboardData({ data: AUTHOR_EMAIL });
  },

  copyMacStartCommand() {
    wx.setClipboardData({ data: MAC_START_COMMAND });
  }
});
