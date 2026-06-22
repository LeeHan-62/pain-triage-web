App({
  globalData: {
    appName: '疼痛智能分诊小程序'
  },

  onLaunch() {
    const records = wx.getStorageSync('painRecords')
    if (!records) {
      wx.setStorageSync('painRecords', [])
    }
  }
})
