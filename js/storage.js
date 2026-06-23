const STORAGE_KEY = 'pain_records';

function getRecords() {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch (e) {
    return [];
  }
}

function saveRecord(record) {
  const records = getRecords();
  record.id = Date.now();
  record.date = new Date().toLocaleString('zh-CN');
  records.unshift(record);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
  return record;
}

function getStats() {
  const records = getRecords();
  const stats = {
    total: records.length,
    byLocation: {},
    byRisk: {},
    byDepartment: {}
  };

  records.forEach(r => {
    const loc = r.result?.location || '未分类';
    const risk = r.result?.risk?.level || '未分级';
    const dept = r.result?.department || '未分配';

    stats.byLocation[loc] = (stats.byLocation[loc] || 0) + 1;
    stats.byRisk[risk] = (stats.byRisk[risk] || 0) + 1;
    stats.byDepartment[dept] = (stats.byDepartment[dept] || 0) + 1;
  });

  return stats;
}

function clearAll() {
  localStorage.removeItem(STORAGE_KEY);
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { getRecords, saveRecord, getStats, clearAll };
}
