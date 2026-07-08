<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>账号</label>
          <input v-model="username" type="text" required placeholder="请输入账号" />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="password" type="password" required placeholder="请输入密码" />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <p class="switch">还没有账号？<router-link to="/register">注册</router-link></p>
    </div>
  </div>
</template>

<script>
import { api } from '../api/index.js'

export default {
  data() {
    return { username: '', password: '', error: '', loading: false }
  },
  methods: {
    async handleLogin() {
      this.error = ''
      this.loading = true
      try {
        const data = await api.login({ username: this.username, password: this.password })
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))
        this.$router.push('/dashboard')
      } catch (e) {
        this.error = '登录失败，请检查账号密码'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.auth-page { display: flex; justify-content: center; align-items: center; min-height: calc(100vh - 56px); }
.auth-card { background: #fff; padding: 36px 32px; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); width: 380px; }
.auth-card h2 { text-align: center; margin-bottom: 24px; font-size: 22px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-size: 14px; color: #666; }
.form-group input { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; outline: none; }
.form-group input:focus { border-color: #4a6cf7; }
.btn-primary { width: 100%; padding: 10px; background: #4a6cf7; color: #fff; border: none; border-radius: 6px; font-size: 15px; cursor: pointer; margin-top: 8px; }
.btn-primary:hover { background: #3b5de7; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: #e74c3c; font-size: 13px; margin-bottom: 8px; }
.switch { text-align: center; margin-top: 16px; font-size: 13px; color: #999; }
.switch a { color: #4a6cf7; }
</style>
