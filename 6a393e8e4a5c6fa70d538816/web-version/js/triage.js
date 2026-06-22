const LOCATION_MAP = {
  '头': '头痛', '胸': '胸痛', '腹': '腹痛', '腰背': '腰背痛',
  '四肢关节': '关节痛', '全身': '全身多发痛'
};

const NATURE_MAP = {
  '撕裂痛': '撕裂痛', '绞痛': '绞痛', '烧灼痛': '烧灼痛',
  '刺痛': '刺痛', '钝痛': '钝痛', '酸痛': '酸痛'
};

const RISK_RULES = [
  {
    level: 'Ⅰ级', label: '极高危', desc: '立即急诊抢救',
    color: 'risk-1',
    conditions: [
      { location: '胸', nature: '撕裂痛' },
      { location: '胸', nature: '绞痛', symptoms: ['大汗'] },
      { location: '腹', nature: '撕裂痛' },
      { location: '腰背', nature: '撕裂痛' }
    ]
  },
  {
    level: 'Ⅱ级', label: '高危', desc: '优先就诊，10分钟内接诊',
    color: 'risk-2',
    conditions: [
      { location: '头', nature: '撕裂痛', symptoms: ['呕吐'] },
      { location: '腹', symptoms: ['发热'] },
      { location: '四肢关节', symptoms: ['肿胀'] }
    ]
  },
  {
    level: 'Ⅲ级', label: '普通急症', desc: '当日全科优先',
    color: 'risk-3',
    conditions: [
      { duration: '突发几小时' },
      { duration: '持续数日' }
    ]
  }
];

function triage(data) {
  const location = data.location || '';
  const nature = data.nature || '';
  const duration = data.duration || '';
  const symptoms = data.symptoms || [];
  const description = data.description || '';

  let matchedRisk = null;

  for (const rule of RISK_RULES) {
    for (const cond of rule.conditions) {
      let match = true;
      if (cond.location && !location.includes(cond.location)) match = false;
      if (cond.nature && nature !== cond.nature) match = false;
      if (cond.duration && duration !== cond.duration) match = false;
      if (cond.symptoms) {
        for (const s of cond.symptoms) {
          if (!symptoms.includes(s)) { match = false; break; }
        }
      }
      if (match) { matchedRisk = rule; break; }
    }
    if (matchedRisk) break;
  }

  if (!matchedRisk) {
    matchedRisk = { level: 'Ⅳ级', label: '慢性慢病', desc: '常规排队，慢病管理', color: 'risk-4' };
  }

  const locationCategory = LOCATION_MAP[location] || location || '未明确';
  const natureCategory = NATURE_MAP[nature] || nature || '未明确';

  let department = '全科';
  if (matchedRisk.level === 'Ⅰ级') department = '急诊科';
  else if (location === '头') department = '神经内科';
  else if (location === '四肢关节') department = '骨科';
  else if (location === '胸') department = '心内科/胸外科';
  else if (location === '腹') department = '普外科/消化内科';
  else if (location === '腰背') department = '骨科/康复科';

  const summary = `患者主诉${location || '某部位'}疼痛，性质倾向为${nature || '未明确'}，病程为${duration || '未明确'}，诱发/缓解因素为${data.factor || '未明确'}，伴随症状：${symptoms.join('、') || '无'}。AI 初步判断为${locationCategory}，风险等级为${matchedRisk.level}（${matchedRisk.label}）。`;

  return {
    location: locationCategory,
    nature: natureCategory,
    risk: matchedRisk,
    department,
    summary
  };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { triage };
}
