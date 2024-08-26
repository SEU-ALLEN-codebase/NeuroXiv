import VueI18n from 'vue-i18n'

/**
 * 获取可用的语言列表
 */
function getAvailableLocales () {
  // 文件夹下面如果存在 index.ts, 下面的语句执行结果就会多出几个文件
  // console.log(require.context('@/locales/common', true).keys())
  // 因为不能判断是否为文件夹, 并且出现 index.ts 的时候会很麻烦, 所以这里暂时直接返回 ['en', 'cn']
  return ['en', 'cn']
  // return require.context('@/locales', true, /\.\/\w+$/i).keys().map(item => {
  //   return item.match(/([A-Za-z0-9-_]+)/i)![1]
  // })
}

// 一次性全部加载语言文件
/* function loadLocaleMessages (): LocaleMessages {
  const locales = require.context('./locales', true, /[A-Za-z0-9-_,\s]+\.json$/i)
  const messages: LocaleMessages = {}
  locales.keys().forEach(key => {
    const matched = key.match(/([A-Za-z0-9-_]+)\./i)
    if (matched && matched.length > 1) {
      const locale = matched[1]
      messages[locale] = locales(key)
    }
  })
  return messages
} */

/**
 * 异步加载语言
 * @param i18n i18n 实例
 * @param path 语言文件路径
 * @param lang 要加载的语言
 */
function loadLanguageAsync (i18n: VueI18n, path: string, lang: string) {
  if (i18n.availableLocales.includes(lang)) {
    return Promise.resolve(lang)
  }
  return import(/* webpackChunkName: "lang-[request]" */ `@/locales/${path}/${lang}/index.ts`).then(
    messages => {
      i18n.setLocaleMessage(lang, messages.default)
      return lang
    }
  )
}

/**
 * 切换语言
 * @param i18n i18n 实例
 * @param path 语言文件路径
 * @param lang 要加载的语言
 */
export async function changeLocale (i18n: VueI18n, path: string, lang: string) {
  await loadLanguageAsync(i18n, path, lang)
  i18n.locale = lang
  document.documentElement.setAttribute('lang', lang)
  return lang
}

export const AVAILABLE_LOCALES = getAvailableLocales()
