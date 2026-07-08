<template>
  <div>
    <h1 class="page-title">签到记录</h1>

    <div class="filters">
      <select v-model="filterAccount" @change="loadRecords">
        <option value="">全部账号</option>
        <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
      </select>
      <input v-model="filterFrom" type="date" @change="loadRecords" placeholder="起始日期" />
      <input v-model="filterTo" type="date" @change="loadRecords" placeholder="结束日期" />
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <table v-else-if="records.length > 0" class="record-table">
      <thead>
        <tr>
          <th>账号</th>
          <th>执行时间</th>
          <th>状态</th>
          <th>备注</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in records" :key="r.id">
          <td>{{ r.account_name }}</td>
          <td>{{ formatTime(r.execute_time) }}</td>
          <td><span :class="r.status === 'success' ? 'tag-success' : 'tag-fail'">{{ r.status === 'success' ? '成功' : '失败' }}</span></td>
          <td class="error-cell">{{ r.error_message }}</td>
        </tr>
      </tbody>
    </table>

    <div v-else class="empty">暂无签到记录</div>
  </div>
</template>

<script>
import { api } from '../api/index.js'

export default {
  data() {
    return {
      records: [], accounts: [], loading: true,
      filterAccount: '', filterFrom: '', filterTo: '',
    }
  },
  async mounted() {
    const accData = await api.getAccounts()
    this.accounts = accData.accounts
    await this.loadRecords()
  },
  methods: {
    async loadRecords() {
      this.loading = true
      try {
        const params = {}
        if (this.filterAccount) params.account_id = this.filterAccount
        if (this.filterFrom) params.from_date = this.filterFrom
        if (this.filterTo) params.to_date = this.filterTo
        const data = await api.getRecords(params)
        this.records = data.records
      } finally { this.loading = false }
    },
    formatTime(t) {
      if (!t) return '-'
      return new Date(t).toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.page-title { font-size: 22px; margin-bottom: 20px; }
.filters { display: flex; gap: 12px; margin-bottom: 20px; }
.filters select, .filters input { padding: 6px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px; }
.record-table { width: 100%; background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); border-collapse: collapse; }
.record-table th { text-align: left; padding: 12px 16px; border-bottom: 1px solid #eee; font-size: 13px; color: #888; }
.record-table td { padding: 12px 16px; border-bottom: 1px solid #f5f5f5; font-size: 14px; }
.tag-success { padding: 2px 10px; background: #d4edda; color: #27ae60; border-radius: 3px; font-size: 12px; }
.tag-fail { padding: 2px 10px; background: #f8d7da; color: #e74c3c; border-radius: 3px; font-size: 12px; }
.error-cell { max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #999; font-size: 13px; }
.loading, .empty { text-align: center; padding: 60px; color: #999; }
</style>
