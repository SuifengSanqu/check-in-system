App({
  globalData: {
    token: '',
    userInfo: null,
    apiBase: 'https://your-server.com/api/miniapp',
  },
  onLaunch() {
    const token = wx.getStorageSync('token')
    if (token) {
      this.globalData.token = token
    }
  },
})
