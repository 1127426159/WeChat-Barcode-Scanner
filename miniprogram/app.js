App({
  onLaunch() {
    const saved = wx.getStorageSync("hostTarget");
    if (saved && saved.host) {
      this.globalData.target = saved.host;
    }
  },
  globalData: {
    target: null
  }
});
