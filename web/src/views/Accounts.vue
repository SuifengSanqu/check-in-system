<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">签到账号管理</h1>
      <button @click="showForm = true" class="btn-primary">添加账号</button>
    </div>

    <div v-if="showForm" class="modal-mask" @click.self="showForm = false">
      <div class="modal">
        <h3>{{ editing ? '编辑账号' : '添加账号' }}</h3>
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>账号名称</label>
            <input v-model="form.name" required placeholder="如：公司打卡" />
          </div>
          <div class="form-group">
            <label>目标网站 URL</label>
            <input v-model="form.site_url" required placeholder="https://example.com" />
          </div>
          <div class="form-group">
            <label>登录页 URL</label>
            <input v-model="form.login_url" required placeholder="https://example.com/login" />
          </div>
          <div class="form-group">
            <label>登录账号</label>
            <input v-model="form.login_username" required />
          </div>
          <div class="form-group">
            <label>登录密码</label>
            <input v-model="form.login_password" type="password" required />
          </div>
          <div class="form-group">
            <label>签到按钮选择器 (CSS)</label>
            <input v-model="form.checkin_selector" placeholder="如：.checkin-btn #sign-btn" />
          </div>
          <div class="form-group">
            <label>签到按钮文本 (多个用 | 分隔)</label>
            <input v-model="form.checkin_text" placeholder="如：签到领积分|加100" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>时间窗口起始</label>
              <input v-model="form.time_window_start" type="time" />
            </div>
            <div class="form-group">
              <label>时间窗口结束</label>
              <input v-model="form.time_window_end" type="time" />
            </div>
          </div>
          <div class="form-actions">
            <button type="button" @click="showForm = false" class="btn-cancel">取消</button>
            <button type="submit" class="btn-primary">{{ editing ? '保存' : '创建' }}</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="accounts.length === 0" class="empty">
      还没有签到账号，点击"添加账号"开始。
    </div>

    <div v-else class="account-list">
      <div v-for="acc in accounts" :key="acc.id" class="account-card">
        <div class="acc-info">
          <div class="acc-name">{{ acc.name }}</div>
          <div class="acc-detail">{{ acc.login_username }} @ {{ acc.site_url }}</div>
          <div class="acc-detail">
            时间窗口: {{ acc.time_window_start }} - {{ acc.time_window_end }}
            <span :class="acc.enabled ? 'tag-on' : 'tag-off'">{{ acc.enabled ? '已启用' : '已停用' }}</span>
          </div>
        </div>
        <div class="acc-actions">
          <button @click="runCheckin(acc.id)" class="btn-sm btn-green">立即签到</button>
          <button @click="editAccount(acc)" class="btn-sm">编辑</button>
          <button @click="handleDelete(acc.id)" class="btn-sm btn-danger">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '../api/index.js'

export default {
  data() {
    return {
      accounts: [],
      loading: true,
      showForm: false,
      editing: null,
      form: {
        name: '', site_url: '', login_url: '', login_username: '', login_password: '',
        checkin_selector: '', checkin_text: '', time_window_start: '06:00', time_window_end: '22:00',
      }
    }
  },
  async mounted() { await this.loadAccounts() },
  methods: {
    async loadAccounts() {
      this.loading = true
      try {
        const data = await api.getAccounts()
        this.accounts = data.accounts
      } finally { this.loading = false }
    },
    editAccount(acc) {
      this.editing = acc.id
      this.form = { ...acc, login_password: '' }
      this.showForm = true
    },
    async handleSubmit() {
      if (this.editing) {
        const data = { ...this.form }
        if (!data.login_password) delete data.login_password
        await api.updateAccount(this.editing, data)
      } else {
        await api.createAccount(this.form)
      }
      this.showForm = false
      this.editing = null
      this.form = {
        name: '', site_url: '', login_url: '', login_username: '', login_password: '',
        checkin_selector: '', checkin_text: '', time_window_start: '06:00', time_window_end: '22:00',
      }
      await this.loadAccounts()
    },
    async handleDelete(id) {
      if (!confirm('确认删除此账号及其签到记录？')) return
      await api.deleteAccount(id)
      await this.loadAccounts()
    },
    async runCheckin(id) {
      const result = await api.runAccount(id)
      if (result.status === 'success') {
        alert('签到成功')
      } else if (result.status === 'error') {
        alert('签到执行出错：' + (result.message || result.error || '未知错误'))
      } else {
        alert('签到结果：' + JSON.stringify(result))
      }
    }
  }
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-title { font-size: 22px; }
.btn-primary { padding: 8px 20px; background: #4a6cf7; color: #fff; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; }
.btn-primary:hover { background: #3b5de7; }
.btn-cancel { padding: 8px 20px; background: #eee; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; }
.btn-sm { padding: 5px 14px; border: 1px solid #ddd; background: #fff; border-radius: 4px; cursor: pointer; font-size: 13px; margin-right: 6px; }
.btn-green { background: #27ae60; color: #fff; border-color: #27ae60; }
.btn-danger { color: #e74c3c; border-color: #e74c3c; }
.account-list { display: flex; flex-direction: column; gap: 12px; }
.account-card { background: #fff; padding: 16px 20px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); display: flex; justify-content: space-between; align-items: center; }
.acc-name { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.acc-detail { font-size: 13px; color: #888; margin-top: 2px; }
.tag-on { display: inline-block; margin-left: 8px; padding: 1px 8px; background: #d4edda; color: #27ae60; font-size: 12px; border-radius: 3px; }
.tag-off { display: inline-block; margin-left: 8px; padding: 1px 8px; background: #f8d7da; color: #e74c3c; font-size: 12px; border-radius: 3px; }
.acc-actions { display: flex; align-items: center; }
.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; justify-content: center; align-items: center; z-index: 100; }
.modal { background: #fff; padding: 28px; border-radius: 8px; width: 520px; max-height: 90vh; overflow-y: auto; }
.modal h3 { margin-bottom: 20px; font-size: 18px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; margin-bottom: 4px; font-size: 13px; color: #666; }
.form-group input { width: 100%; padding: 8px 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.loading, .empty { text-align: center; padding: 60px; color: #999; }
</style>
