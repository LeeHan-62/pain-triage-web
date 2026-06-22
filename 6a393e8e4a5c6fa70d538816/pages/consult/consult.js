const { triage } = require('../../utils/triage')

Page({
  data: {
    locations: ['头', '颈肩', '胸', '上腹', '下腹', '腰背', '关节', '肌肉', '会阴', '全身'],
    natures: ['撕裂痛', '绞痛', '烧灼痛', '刺痛', '钝痛', '酸痛'],
    durations: ['突发几小时', '持续数日', '慢性反复发作'],
    factors: ['运动加重', '饭后疼痛', '休息缓解', '夜间加重', '无明显诱因'],
    symptoms: ['胸闷', '大汗', '呕血', '呕吐', '头晕', '肢体麻木', '发热', '腹部压痛', '下肢肿痛'],
    form: {
      patientName: '',
      location: '',
      nature: '',
      duration: '',
      factor: '',
      symptoms: [],
      description: ''
    }
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({
      [`form.${field}`]: e.detail.value
    })
  },

  onPickerChange(e) {
    const field = e.currentTarget.dataset.field
    const list = e.currentTarget.dataset.list
    this.setData({
      [`form.${field}`]: this.data[list][Number(e.detail.value)]
    })
  },

  onSymptomsChange(e) {
    this.setData({
      'form.symptoms': e.detail.value
    })
  },

  useVoiceMock() {
    this.setData({
      'form.description': '胸部压榨样疼痛，突发数小时，伴胸闷和大汗，休息后没有明显缓解'
    })
    wx.showToast({
      title: '已填入语音示例',
      icon: 'none'
    })
  },

  submit() {
    if (!this.data.form.location && !this.data.form.description) {
      wx.showToast({
        title: '请填写疼痛位置或主诉描述',
        icon: 'none'
      })
      return
    }

    const result = triage(this.data.form)
    wx.setStorageSync('latestTriageResult', result)

    const records = wx.getStorageSync('painRecords') || []
    records.unshift(result)
    wx.setStorageSync('painRecords', records)

    wx.navigateTo({
      url: '/pages/result/result'
    })
  }
})
