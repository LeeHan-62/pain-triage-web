Page({
  data: {
    result: null
  },

  onLoad() {
    this.setData({
      result: wx.getStorageSync('latestTriageResult')
    })
  },

  backHome() {
    wx.switchTab({
      url: '/pages/home/home'
    })
  },

  goRecords() {
    wx.switchTab({
      url: '/pages/records/records'
    })
  }
})
