import Vue from 'vue'
import Vuex from 'vuex'
import { tokenStore, langSettingStore, userInfoStore, themeStore } from '@/utils/mouse'
import { getSystemLang } from '@/utils/util'
import { UserInfo } from '@/types/User'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    userInfo: JSON.parse(userInfoStore.get() || `{
      "username": "",
      "avatar": ""
    }`),
    // 各种设置和信息的本地保存
    stores: { tokenStore, langSettingStore, userInfoStore, themeStore },
    token: tokenStore.get() || '', // 防止 XSRF 攻击的 token
    lang: langSettingStore.get() || getSystemLang(), // 用户设置的语言或者系统设置语言
    // 判断是否登录的变量, 每次发送接口请求都会更新, 这个变量可以防止没有登录的时候不断发送定时请求
    // 注意这里初始值要设置为 true, 否则已经登录的情况下刷新页面之后, 有可能出现一些接口请求不发送的问题
    // 即使真的没有登录也没问题, 只是多发送一次请求而已, 之后马上就会更新这个变量
    isLogin: true,
    // 当前atlas
    // atlas: 'fMOST'
    atlas: 'CCFv3'
  },
  mutations: {
    /**
     * update current user info
     * @param state { object } vuex state
     * @param userInfo { json } user info
     */
    updateUserInfo (state, userInfo) {
      state.userInfo = userInfo
    },

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
    },

    /**
     * 更新登录状态
     * @param state vuex state
     * @param status login status
     */
    updateLoginStatus (state: any, status: boolean) {
      state.isLogin = status
    },

    /**
     * 更新当前网页atlas
     * @param state vuex state
     * @param atlasName atlas名称，CCFv3或者fMOST
     */
    updateAtlas (state: any, atlasName: string) {
      state.atlas = atlasName
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
    },

    /**
     * update userInfo action
     * @param commit { function } vuex mutation
     * @param userInfo 用户信息
     */
    updateUserInfo ({ commit }, userInfo: UserInfo) {
      commit('updateUserInfo', userInfo)
      userInfoStore.set(JSON.stringify(userInfo))
    }
  },
  modules: {
  }
})
