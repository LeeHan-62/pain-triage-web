Page({
  data: {
    records: []
  },

  onShow() {
    this.setData({
      records: wx.getStorageSync('painRecords') || []
    })
  },

  clearRecords() {
    wx.showModal({
      title: '确认清空',
      content: '清空后将删除本地模拟档案记录。',
      success: res => {
        if (res.confirm) {
          wx.setStorageSync('painRecords', [])
          this.setData({ records: [] })
        }
      }
    })
  }
})
