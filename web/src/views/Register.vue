<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>账号</label>
          <input v-model="username" type="text" required minlength="3" placeholder="3-64 位字符" />
        </div>
        <div class="form-group">
          <label>昵称</label>
          <input v-model="nickname" type="text" placeholder="选填" />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="password" type="password" required minlength="6" placeholder="至少 6 位" />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <p class="switch">已有账号？<router-link to="/login">登录</router-link></p>
    </div>
  </div>
</template>

<script>
import { api } from '../api/index.js'

export default {
  data() {
    return { username: '', nickname: '', password: '', error: '', loading: false }
  },
  methods: {
    async handleRegister() {
      this.error = ''
      this.loading = true
      try {
        const data = await api.register({
          username: this.username,
          password: this.password,
          nickname: this.nickname,
        })
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))
        this.$router.push('/dashboard')
      } catch (e) {
        this.error = '注册失败，请重试'
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
