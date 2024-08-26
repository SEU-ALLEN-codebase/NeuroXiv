import { CookieStorage, LocalStore } from '@/utils/storages'

// 防止 CSRF 攻击的 token
const tokenStore = new CookieStorage('home_page_token', '/', 365)

// 保存语言设置
const langSettingStore = new LocalStore('home_page_lang')

// 保存用户信息
const userInfoStore = new LocalStore('home_page_userInfo')

// 保存主题设置
const themeStore = new LocalStore('home_page_theme')

export { tokenStore, langSettingStore, userInfoStore, themeStore }
