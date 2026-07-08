---
title: Check-in System
emoji: 📅
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# 统一签到系统

支持 Web 端自动签到（Puppeteer + stealth 反检测）+ 微信小程序每日签到。

## 功能
- Web 管理后台（Vue 3）：多账号管理、自动签到、签到记录查询
- 微信小程序：每日登录签到、签到日历、签到记录
- Puppeteer + stealth 防检测：模拟真实浏览器行为
- AES-256 + bcrypt 双层密码加密
- 随机时间调度：06:00-22:00 随机分配签到时间
