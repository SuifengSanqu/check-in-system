import { api } from '../../utils/api'

Page({
  data: {
    todayStr: '',
    checkedIn: false,
    checkinTime: '',
    consecutiveDays: 0,
    totalDays: 0,
  },
  onShow() {
    this.setToday()
    this.checkToday()
  },
  setToday() {
    const d = new Date()
    this.setData({ todayStr: `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日` })
  },
  async ensureLogin() {
    if (wx.getStorageSync('token')) return
    try {
      const { code } = await wx.login()
      const data = await api.login(code)
      wx.setStorageSync('token', data.token)
    } catch (_) {}
  },
  async checkToday() {
    await this.ensureLogin()
    try {
      const data = await api.today()
      this.setData({
        checkedIn: data.checked_in,
        checkinTime: data.check_in_time ? new Date(data.check_in_time).toLocaleTimeString() : '',
        consecutiveDays: data.consecutive_days,
      })
    } catch (_) {}
  },
  async doCheckin() {
    await this.ensureLogin()
    try {
      const data = await api.checkin()
      if (data.already_checked_in) {
        wx.showToast({ title: '今日已签到', icon: 'none' })
      } else {
        wx.showToast({ title: '签到成功', icon: 'success' })
      }
      this.setData({
        checkedIn: true,
        checkinTime: new Date(data.check_in_time).toLocaleTimeString(),
        consecutiveDays: data.consecutive_days,
        totalDays: data.total_days,
      })
    } catch (_) {
      wx.showToast({ title: '签到失败', icon: 'none' })
    }
  },
})
