import { api } from '../../utils/api'

Page({
  data: {
    year: 0, month: 0,
    weekdays: ['日', '一', '二', '三', '四', '五', '六'],
    cells: [],
  },
  onShow() {
    const now = new Date()
    this.loadCalendar(now.getFullYear(), now.getMonth() + 1)
  },
  async loadCalendar(year, month) {
    const today = new Date()
    const todayStr = `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`

    try {
      const data = await api.calendar(year, month)
      const checked = new Set(data.checked_days.map(String))

      const firstDay = new Date(year, month - 1, 1).getDay()
      const daysInMonth = new Date(year, month, 0).getDate()

      const cells = []
      for (let i = 0; i < firstDay; i++) {
        cells.push({ day: '', empty: true })
      }
      for (let d = 1; d <= daysInMonth; d++) {
        const dateStr = `${year}-${month}-${d}`
        cells.push({
          day: d,
          checked: checked.has(String(d)),
          isToday: dateStr === todayStr,
          empty: false,
        })
      }

      this.setData({ year, month, cells })
    } catch (_) {}
  },
  prevMonth() {
    let { year, month } = this.data
    if (month === 1) { year--; month = 12 } else { month-- }
    this.loadCalendar(year, month)
  },
  nextMonth() {
    let { year, month } = this.data
    if (month === 12) { year++; month = 1 } else { month++ }
    this.loadCalendar(year, month)
  },
})
