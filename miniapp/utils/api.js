const BASE = 'https://your-server.com/api/miniapp'

function request(url, options = {}) {
  const token = wx.getStorageSync('token')
  return new Promise((resolve, reject) => {
    wx.request({
      url: BASE + url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: 'Bearer ' + token } : {}),
      },
      success(res) {
        if (res.statusCode === 401) {
          wx.removeStorageSync('token')
          wx.reLaunch({ url: '/pages/index/index' })
          return
        }
        resolve(res.data)
      },
      fail: reject,
    })
  })
}

export const api = {
  login: (code) => request('/auth/login', { method: 'POST', data: { code } }),
  checkin: () => request('/checkin', { method: 'POST' }),
  today: () => request('/checkin/today'),
  calendar: (year, month) => request(`/checkin/calendar?year=${year}&month=${month}`),
  records: (limit = 30) => request(`/records?limit=${limit}`),
}
