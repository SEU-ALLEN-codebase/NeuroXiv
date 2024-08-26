import RequestMessage from './request'
import NavMessage from './nav'
import BrowserMessage from '../../common/en/browser'

import enLocale from 'element-ui/lib/locale/lang/en'

const messages = {
  en: "English",
  cn: "中文",
  login: "Login",
  logout: "Logout",
  welcome: "Hello",
  theme: {
    light: 'light',
    dark: 'dark',
    auto: 'auto'
  },
  request: RequestMessage,
  nav: NavMessage,
  browser: BrowserMessage,
  ...enLocale
}

export default messages
