import Vue from 'vue'
import VueI18n from 'vue-i18n'
import { changeLocale } from './common'

import Element from 'element-ui'

Vue.use(VueI18n)

const path = 'mouse'

const i18n = new VueI18n({
  locale: process.env.VUE_APP_I18N_LOCALE || 'en',
  fallbackLocale: process.env.VUE_APP_I18N_FALLBACK_LOCALE || 'en',
  messages: {}
})

Vue.use(Element,{
  i18n: (key: string, value: VueI18n.Values | undefined) => i18n.t(key, value)
})

export default i18n

/**
 * 切换语言
 * @param lang language
 */
export async function setI18nLanguage (lang: string) {
  await changeLocale(i18n, path, lang)
}
