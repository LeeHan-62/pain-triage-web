const API_BASE_URL = window.PAIN_TRIAGE_API_BASE_URL || 'http://127.0.0.1:8000';

async function callBackendTriage(formData) {
  const response = await fetch(`${API_BASE_URL}/api/triage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  });

  if (!response.ok) {
    throw new Error(`后端接口返回异常：${response.status}`);
  }

  return response.json();
}

async function smartTriage(formData) {
  try {
    const backend = await callBackendTriage(formData);
    return {
      result: backend.result,
      warnings: backend.warnings || [],
      backendUsed: true
    };
  } catch (error) {
    return {
      result: triage(formData),
      warnings: [`后端模型服务暂不可用，已切换为浏览器本地规则：${error.message}`],
      backendUsed: false
    };
  }
}
