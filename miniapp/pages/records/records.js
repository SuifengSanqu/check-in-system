import { api } from '../../utils/api'

Page({
  data: { records: [] },
  onShow() {
    this.loadRecords()
  },
  async loadRecords() {
    try {
      const data = await api.records()
      this.setData({ records: data.records })
    } catch (_) {}
  },
})
