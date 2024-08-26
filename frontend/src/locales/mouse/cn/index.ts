import RequestMessage from './request'
import NavMessage from './nav'
import BrowserMessage from '../../common/cn/browser'

import zhLocale from 'element-ui/lib/locale/lang/zh-CN'

const messages = {
  en: "English",
  cn: "中文",
  login: "登录",
  logout: "退出",
  welcome: "你好",
  theme: {
    light: '浅色',
    dark: '暗色',
    auto: '自动'
  },
  request: RequestMessage,
  nav: NavMessage,
  browser: BrowserMessage,
  ...zhLocale
}

export default messages
