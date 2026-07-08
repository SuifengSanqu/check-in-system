<template>
  <div id="app-container">
    <nav v-if="isLoggedIn" class="top-nav">
      <div class="nav-brand">统一签到系统</div>
      <div class="nav-links">
        <router-link to="/dashboard">仪表盘</router-link>
        <router-link to="/accounts">账号管理</router-link>
        <router-link to="/records">签到记录</router-link>
        <button @click="logout" class="btn-logout">退出</button>
      </div>
    </nav>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('token')
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    }
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; color: #333; }
.top-nav { display: flex; justify-content: space-between; align-items: center; padding: 0 24px; height: 56px; background: #1a1a2e; color: #fff; }
.top-nav .nav-brand { font-size: 18px; font-weight: 600; }
.top-nav .nav-links { display: flex; align-items: center; gap: 20px; }
.top-nav .nav-links a { color: #ccc; text-decoration: none; font-size: 14px; transition: color 0.2s; }
.top-nav .nav-links a:hover, .top-nav .nav-links a.router-link-active { color: #fff; }
.btn-logout { background: none; border: 1px solid #666; color: #ccc; padding: 4px 14px; border-radius: 4px; cursor: pointer; font-size: 13px; }
.btn-logout:hover { border-color: #fff; color: #fff; }
main { max-width: 1100px; margin: 0 auto; padding: 24px; }
</style>
