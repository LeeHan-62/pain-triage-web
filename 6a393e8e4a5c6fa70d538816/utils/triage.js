const locationMap = {
  '头': '头痛',
  '颈肩': '颈肩痛',
  '胸': '胸痛',
  '上腹': '上腹痛',
  '下腹': '下腹痛',
  '腰背': '腰背痛',
  '关节': '关节痛',
  '肌肉': '肌肉痛',
  '会阴': '会阴痛',
  '全身': '全身多发痛'
}

const departmentMap = {
  '头痛': '神经内科 / 全科',
  '颈肩痛': '骨科 / 全科',
  '胸痛': '急诊 / 全科',
  '上腹痛': '全科 / 消化内科',
  '下腹痛': '全科 / 普外科',
  '腰背痛': '骨科 / 全科',
  '关节痛': '骨科 / 风湿免疫科',
  '肌肉痛': '全科',
  '会阴痛': '泌尿外科 / 妇科',
  '全身多发痛': '全科'
}

function inferPart(form) {
  const text = `${form.location || ''}${form.description || ''}`
  const key = Object.keys(locationMap).find(item => text.includes(item))
  return key ? locationMap[key] : '全身多发痛'
}

function inferNature(form) {
  if (form.nature) return form.nature
  const text = form.description || ''
  const natures = ['撕裂痛', '绞痛', '烧灼痛', '刺痛', '钝痛', '酸痛']
  return natures.find(item => text.includes(item.replace('痛', ''))) || '钝痛'
}

function hasAny(form, words) {
  const text = `${form.description || ''}${(form.symptoms || []).join('')}${form.factor || ''}${form.duration || ''}`
  return words.some(word => text.includes(word))
}

function classifyRisk(part, nature, form) {
  if (
    (part === '胸痛' && (nature === '撕裂痛' || hasAny(form, ['压榨', '大汗', '胸闷']))) ||
    (part.includes('腹痛') && hasAny(form, ['刀割', '剧烈', '呕血'])) ||
    (part === '腰背痛' && hasAny(form, ['突发', '剧烈', '撕裂']))
  ) {
    return {
      level: 'Ⅰ级',
      label: '极高危',
      color: '#d93025',
      action: '立即弹窗红色预警，护士引导至急诊抢救区',
      queue: '急诊抢救区'
    }
  }

  if (
    (part === '头痛' && hasAny(form, ['持续', '剧烈', '呕吐'])) ||
    (part.includes('腹痛') && hasAny(form, ['压痛', '发热'])) ||
    hasAny(form, ['下肢肿痛', '肿痛'])
  ) {
    return {
      level: 'Ⅱ级',
      label: '高危',
      color: '#f97316',
      action: '置顶排队号，建议 10 分钟内优先接诊',
      queue: '优先诊室'
    }
  }

  if (hasAny(form, ['急性', '扭伤', '新发', '一过性'])) {
    return {
      level: 'Ⅲ级',
      label: '普通急症',
      color: '#2563eb',
      action: '进入当日全科或相关专科优先队列',
      queue: departmentMap[part] || '全科'
    }
  }

  return {
    level: 'Ⅳ级',
    label: '慢性慢病',
    color: '#16a34a',
    action: '常规排队，写入慢病随访提醒',
    queue: departmentMap[part] || '全科'
  }
}

function buildSummary(form, part, nature, risk) {
  const symptoms = form.symptoms && form.symptoms.length ? form.symptoms.join('、') : '未选择明显伴随症状'
  return `患者主诉${form.location || part}疼痛，性质倾向为${nature}，病程为${form.duration || '未明确'}，诱发/缓解因素为${form.factor || '未明确'}，伴随症状：${symptoms}。AI 初步判断为${part}，风险等级为${risk.level}（${risk.label}）。`
}

function triage(form) {
  const part = inferPart(form)
  const nature = inferNature(form)
  const risk = classifyRisk(part, nature, form)
  return {
    id: Date.now(),
    createdAt: new Date().toLocaleString(),
    patientName: form.patientName || '匿名患者',
    part,
    nature,
    risk,
    department: risk.queue,
    summary: buildSummary(form, part, nature, risk),
    raw: form
  }
}

module.exports = {
  triage
}
