function countBy(records, getter) {
  return records.reduce((acc, item) => {
    const key = getter(item)
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})
}

function toList(map) {
  return Object.keys(map).map(name => ({
    name,
    count: map[name]
  }))
}

Page({
  data: {
    total: 0,
    riskList: [],
    partList: [],
    natureList: [],
    highRiskCount: 0
  },

  onShow() {
    const records = wx.getStorageSync('painRecords') || []
    const riskMap = countBy(records, item => `${item.risk.level} ${item.risk.label}`)
    const partMap = countBy(records, item => item.part)
    const natureMap = countBy(records, item => item.nature)
    const highRiskCount = records.filter(item => item.risk.level === 'Ⅰ级' || item.risk.level === 'Ⅱ级').length

    this.setData({
      total: records.length,
      riskList: toList(riskMap),
      partList: toList(partMap),
      natureList: toList(natureMap),
      highRiskCount
    })
  }
})
