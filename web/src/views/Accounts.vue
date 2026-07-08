<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">签到账号管理</h1>
      <button @click="openCreate" class="btn-primary">添加账号</button>
    </div>

    <div v-if="showForm" class="modal-mask" @click.self="showForm = false">
      <div class="modal">
        <h3>{{ editing ? '编辑账号' : '添加账号' }}</h3>
        <form @submit.prevent="handleSubmit">
          <!-- ── 基础信息 ── -->
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
            <input v-model="form.login_password" type="password" :required="!editing" />
          </div>
          <div class="form-group">
            <label>登录流程</label>
            <select v-model="form.login_flow">
              <option value="single">单页登录（账号密码同一页）</option>
              <option value="two_step">两步登录（先输账号，下一步再输密码）</option>
            </select>
          </div>

          <!-- ── 高级配置折叠区 ── -->
          <div class="advanced-toggle" @click="showAdvanced = !showAdvanced">
            <span>高级配置（选择器 / 导航 / 弹窗处理）</span>
            <span class="toggle-arrow">{{ showAdvanced ? '▲' : '▼' }}</span>
          </div>

          <div v-if="showAdvanced" class="advanced-section">
            <div class="section-title">登录表单选择器（留空则自动检测）</div>
            <div class="form-group">
              <label>用户名输入框选择器</label>
              <input v-model="form.login_username_selector" placeholder="如：#username, input[name=email]" />
            </div>
            <div class="form-group">
              <label>密码输入框选择器</label>
              <input v-model="form.login_password_selector" placeholder="如：#password, input[type=password]" />
            </div>
            <div class="form-group">
              <label>登录按钮选择器</label>
              <input v-model="form.login_button_selector" placeholder="如：button[type=submit], .login-btn" />
            </div>

            <div class="section-title">签到相关</div>
            <div class="form-group">
              <label>登录后导航 URL（登录后需跳转到签到页时填写）</label>
              <input v-model="form.checkin_nav_url" placeholder="https://example.com/checkin" />
            </div>
            <div class="form-group">
              <label>签到按钮选择器 (CSS)</label>
              <input v-model="form.checkin_selector" placeholder="如：.checkin-btn, #sign-btn" />
            </div>
            <div class="form-group">
              <label>签到按钮文本（多个用 | 分隔）</label>
              <input v-model="form.checkin_text" placeholder="如：签到领积分|加100" />
            </div>
            <div class="form-group">
              <label>签到前额外步骤 (JSON)</label>
              <textarea v-model="form.checkin_extra_steps" rows="3"
                placeholder='[{"action":"click","selector":".nav-avatar"},{"action":"wait","ms":2000}]' />
            </div>

            <div class="section-title">弹窗 / 广告处理</div>
            <div class="form-group">
              <label>Cookie 弹窗关闭按钮选择器</label>
              <input v-model="form.cookie_banner_selector" placeholder="如：#onetrust-accept-btn-handler" />
            </div>
            <div class="form-group">
              <label>额外弹窗选择器 (JSON 数组)</label>
              <textarea v-model="form.popup_selectors" rows="2"
                placeholder='[".modal-close", ".ad-dismiss"]' />
            </div>
          </div>

          <!-- ── 时间窗口 ── -->
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
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.enabled" />
              启用自动签到
            </label>
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
            <span v-if="acc.login_flow === 'two_step'" class="tag-info">两步登录</span>
            <span v-if="acc.login_username_selector" class="tag-info">自定义选择器</span>
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

const emptyForm = () => ({
  name: '', site_url: '', login_url: '', login_username: '', login_password: '',
  login_flow: 'single',
  login_username_selector: '', login_password_selector: '', login_button_selector: '',
  checkin_nav_url: '', checkin_selector: '', checkin_text: '', checkin_extra_steps: '',
  cookie_banner_selector: '', popup_selectors: '',
  time_window_start: '06:00', time_window_end: '22:00',
  enabled: true,
})

export default {
  data() {
    return {
      accounts: [],
      loading: true,
      showForm: false,
      showAdvanced: false,
      editing: null,
      form: emptyForm(),
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
    openCreate() {
      this.editing = null
      this.form = emptyForm()
      this.showAdvanced = false
      this.showForm = true
    },
    editAccount(acc) {
      this.editing = acc.id
      const copy = { ...acc, login_password: '' }
      copy.enabled = !!copy.enabled
      this.form = copy
      this.showAdvanced = !!(copy.login_username_selector || copy.login_button_selector ||
        copy.checkin_nav_url || copy.checkin_extra_steps || copy.cookie_banner_selector || copy.popup_selectors)
      this.showForm = true
    },
    async handleSubmit() {
      const data = { ...this.form }
      if (this.editing && !data.login_password) delete data.login_password
      if (this.editing) {
        await api.updateAccount(this.editing, data)
      } else {
        await api.createAccount(data)
      }
      this.showForm = false
      this.editing = null
      this.form = emptyForm()
      this.showAdvanced = false
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
.tag-info { display: inline-block; margin-left: 6px; padding: 1px 6px; background: #dbeafe; color: #4a6cf7; font-size: 12px; border-radius: 3px; }
.acc-actions { display: flex; align-items: center; }
.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; justify-content: center; align-items: flex-start; padding-top: 40px; z-index: 100; }
.modal { background: #fff; padding: 28px; border-radius: 8px; width: 580px; max-height: 85vh; overflow-y: auto; }
.modal h3 { margin-bottom: 20px; font-size: 18px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; margin-bottom: 4px; font-size: 13px; color: #666; }
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; font-family: inherit; box-sizing: border-box; }
.form-group textarea { resize: vertical; }
.checkbox-label { display: flex !important; align-items: center; gap: 8px; }
.checkbox-label input { width: auto; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.advanced-toggle { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; background: #f7f8fa; border-radius: 6px; margin-bottom: 16px; cursor: pointer; font-size: 14px; color: #4a6cf7; user-select: none; }
.advanced-toggle:hover { background: #eef0f5; }
.toggle-arrow { font-size: 12px; }
.advanced-section { background: #fafbfc; border: 1px solid #e8eaed; border-radius: 6px; padding: 16px; margin-bottom: 16px; }
.section-title { font-size: 13px; font-weight: 600; color: #555; margin: 12px 0 8px; padding-top: 8px; border-top: 1px solid #eee; }
.section-title:first-child { border-top: none; padding-top: 0; margin-top: 0; }
.loading, .empty { text-align: center; padding: 60px; color: #999; }
</style>
