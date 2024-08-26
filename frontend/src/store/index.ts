import Vue from 'vue'
import Vuex from 'vuex'
import { tokenStore, langSettingStore, userInfoStore, themeStore } from '@/utils'
import { getSystemLang } from '@/utils/util'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    // 各种设置和信息的本地保存
    stores: { tokenStore, langSettingStore, userInfoStore, themeStore },
    token: tokenStore.get() || '', // 防止 XSRF 攻击的 token
    lang: langSettingStore.get() || getSystemLang() // 用户设置的语言或者系统设置语言
  },
  mutations: {
    /**
     * update request token
     * @param state { object } vuex state
     * @param token { string } request token
     */
    updateToken (state, token) {
      state.token = token
    },

    /**
     * update language
     * @param state { object } vuex state
     * @param lang { string } user select language
     */
    updateLang (state, lang) {
      state.lang = lang
    }
  },
  actions: {
    /**
     * update token action
     * @param commit { function } vuex mutation
     * @param token { string } request token
     */
    updateToken ({ commit }, token) {
      commit('updateToken', token)
      tokenStore.set(token)
    },

    /**
     * update language action
     * @param commit { function } vuex mutation
     * @param lang { string } user select language
     */
    updateLang ({ commit }, lang) {
      commit('updateLang', lang)
      langSettingStore.set(lang)
    }
  },
  modules: {
  }
})
