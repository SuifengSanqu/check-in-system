const BASE = '/api/web'

async function request(url, options = {}) {
  const token = localStorage.getItem('token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }
  const resp = await fetch(`${BASE}${url}`, { ...options, headers })
  if (resp.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    return
  }
  return resp.json()
}

export const api = {
  register: (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),

  getAccounts: () => request('/accounts'),
  createAccount: (data) => request('/accounts', { method: 'POST', body: JSON.stringify(data) }),
  getAccount: (id) => request(`/accounts/${id}`),
  updateAccount: (id, data) => request(`/accounts/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteAccount: (id) => request(`/accounts/${id}`, { method: 'DELETE' }),
  runAccount: (id) => request(`/accounts/${id}/run`, { method: 'POST' }),

  getRecords: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/records${qs ? '?' + qs : ''}`)
  },
  getStats: () => request('/records/stats'),
}
