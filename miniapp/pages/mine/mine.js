import { api } from '../../utils/api'

Page({
  data: {
    avatarUrl: '',
    nickname: '',
    totalDays: 0,
    consecutiveDays: 0,
  },
  onShow() {
    this.loadInfo()
  },
  async loadInfo() {
    try {
      const data = await api.today()
      this.setData({
        consecutiveDays: data.consecutive_days,
      })
      const recs = await api.records(365)
      this.setData({ totalDays: recs.records.length })
    } catch (_) {}
  },
})
