// 通用的请求代码, 添加自动显示隐藏 loading, 显示成功或者失败提示

import { ElLoadingComponent } from 'element-ui/types/loading'
import { Loading, Notification, MessageBox } from 'element-ui' // 引入消息通知组件, loading 组件
import RequestFactory from './RequestFactory'
import { ResponseData, RequestDetail } from '@/types/Request'
// @ts-ignore
import APP_CONFIG from '@/../config.json'
import APIError from '@/CustomExceptions/APIError'
// import { tokenStore } from '@/utils/mouse'
import NotLoginError from '@/CustomExceptions/NotLoginError'
// import router from "@/router/mouse"

const URLENCODED_HEADER = { 'Content-type': 'application/json', 'Accept': 'application/json' }
const TIMEOUT = -1
const COMMON_OPTIONS = { // 通用请求选项, 例如请求 method、credentials 设置等, 可以被覆盖
  method: 'post',
  headers: URLENCODED_HEADER,
  credentials: 'include',
  mode: 'cors'
}
let LOADING_COUNT = 0

const ORIGIN = `${location.origin}${APP_CONFIG.API_PATH}`
let loginConfirmDialogShowed = false // 是否显示了登录确认对话框, 使用这个变量防止多次弹出

/**
 * 要loading的数目加一
 */
function increaseLoadingCount () {
  LOADING_COUNT += 1
}

/**
 * 要loading的数目减一
 */
function decreaseLoadingCount () {
  LOADING_COUNT -= 1
}

/**
 * 判断是否可以关闭Loading的ui
 */
function LoadingZero () {
  return LOADING_COUNT === 0
}

/**
 * 请求成功之后对 code 做处理, 并把实际的数据提取出来
 * @param rawData { json } 原始数据, 外层带有 code、message 等信息, 格式为 { code: 0, msg: '', data: [] }
 */
function processDataByCode (rawData: ResponseData) {
  // 判断外层是否有包装
  if (!rawData.hasOwnProperty('code')) {
    return rawData
  }
  // 更新登录状态
  let isLogin = !(rawData.msg && rawData.msg.includes('not login'))
  window.vm.$store.commit('updateLoginStatus', isLogin)
  if (rawData.code === 0) { // 数据正常
    return Promise.resolve(rawData.data)
  } else {
    if (rawData.msg && rawData.msg.includes('not login')) {
      return Promise.reject(new NotLoginError(rawData.msg))
    } else {
      return Promise.reject(new APIError(rawData.msg || ''))
    }
  }
}

/**
 * request url 添加防 XSRF 攻击的 token
 * @param url { string } request url
 */
function addTokenToURL (url: string) {
  const newUrl = new URL(url)
  // 因为 RequestWrapper 需要在多个页面使用, 所以这里不能直接 import 某个页面的 tokenStore
  const tokenStore = window.vm.$store.state.stores.tokenStore
  newUrl.searchParams.append('token', tokenStore.get() || '')
  return newUrl.href
}

/**
 * show loading
 * @param target 要显示 loading 的 element
 */
function showLoading (target: HTMLElement) {
  return Loading.service({
    target,
    text: 'loading data...',
    background: 'transparent'
  })
}

/**
 * 显示成功或者失败提示
 * @param type 消息类型, success | error
 * @param title 消息标题
 * @param msg 消息内容
 */
function showNotification (type: 'success' | 'error', title: string = '', msg: string = '') {
  Notification[type]({
    title,
    message: msg
  })
}

/**
 * 跳转到登录页面
 */
function gotoLogin () {
  const router = window.vm.$router
  return router.push({
    // @ts-ignore
    path: `/${router.history.current.params.lang}/login`,
    // @ts-ignore
    query: { redirect: router.history.current.fullPath }
  })
}

/**
 * 给请求添加 loading 和消息提示
 * @param requestPromise request function
 * @param showLoadingFunc 显示 loading 的方法
 * @param showSuccessMsgFunc 显示成功提示的方法
 * @param showErrorMsgFunc 显示失败提示的方法
 */
function requestWithLoadingAndMessage (requestPromise: Function, showLoadingFunc: Function | undefined, showSuccessMsgFunc: Function | undefined, showErrorMsgFunc: Function | undefined) {
  let loadingInstance: ElLoadingComponent
  // 请求之前先显示 loading
  if (showLoadingFunc) {
    loadingInstance = showLoadingFunc()
    increaseLoadingCount()
  }
  return requestPromise().then((res: any) => {
    if (res.status === 200) {
      return res.json().then(processDataByCode)
    } else {
      return Promise.reject(new Error(res.statusText))
    }
  }).then((res: any) => {
    // 显示成功消息, 成功消息提示要放到这里, 不能判断 status === 200 之后就提示, 因为 code 可能为 -1, 未登录, 这种情况也是要当作错误处理的
    showSuccessMsgFunc && showSuccessMsgFunc()
    return res
  }).catch((e: Error) => {
    // 显示失败消息
    showErrorMsgFunc && showErrorMsgFunc(e)
    throw e
  }).finally(() => {
    decreaseLoadingCount()
    if (LOADING_COUNT === 0) {
      loadingInstance && loadingInstance.close() // 无论请求成功还是失败都隐藏 loading
    }
  })
}

/**
 * 通用请求，会自动显示和隐藏 loading，显示成功或者失败的提示
 @param requestDetail { RequestDetail } 请求详情
 */
function request (requestDetail: RequestDetail) {
  if (!requestDetail.url.startsWith('http')) {
    requestDetail.url = `${ORIGIN}/${requestDetail.url}`
  }
  requestDetail.options = requestDetail.options || {}
  requestDetail.timeout = requestDetail.timeout || TIMEOUT
  if (typeof requestDetail.showSuccessMsg === 'undefined') requestDetail.showSuccessMsg = true // requestDetail.showSuccessMsg = requestDetail.showSuccessMsg ?? true
  if (typeof requestDetail.showErrorMsg === 'undefined') requestDetail.showErrorMsg = true // requestDetail.showErrorMsg = requestDetail.showErrorMsg ?? true

  // 合并通用选项
  requestDetail.options = Object.assign({}, COMMON_OPTIONS, requestDetail.options)
  let abortedRequest = new RequestFactory(new Request(addTokenToURL(requestDetail.url), requestDetail.options), requestDetail.timeout)
  let originRequest = abortedRequest.start.bind(abortedRequest)
  abortedRequest.start = () => {
    let showLoadingFunc, showSuccessMsgFunc, showErrorMsgFunc
    if (requestDetail.loadingTarget) {
      showLoadingFunc = showLoading.bind(null, requestDetail.loadingTarget)
    }
    if (requestDetail.showSuccessMsg && requestDetail.successMsg) {
      // can write like this
      // requestDetail.showSuccessMsg && requestDetail.messages?.success
      showSuccessMsgFunc = showNotification.bind(null, 'success', requestDetail.successMsg)
    }
    if (requestDetail.showErrorMsg && requestDetail.errorMsg) {
      // can write like this
      // requestDetail.showErrorMsg && requestDetail.messages?.error
      showErrorMsgFunc = (e: Error) => {
        if (!loginConfirmDialogShowed && e.name !== 'AbortError') {
          showNotification('error', requestDetail.errorMsg, e.message)
        }
      }
    }
    return requestWithLoadingAndMessage(originRequest, showLoadingFunc, showSuccessMsgFunc, showErrorMsgFunc).catch((e: Error) => {
      // 没有登录或者登录过期之后弹出对话框, 询问是否跳转到登录页面
      if (e.name === 'NotLoginError') {
        if (!loginConfirmDialogShowed) {
          MessageBox.confirm('没有登录或者登录已过期, 是否跳转到登录页面？', '登录确认', { type: 'warning' })
            .then(() => {
              return gotoLogin()
            })
            .finally(() => {
              loginConfirmDialogShowed = false
            })
          loginConfirmDialogShowed = true
        }
      }
      throw e
    })
  }
  return abortedRequest
}

export { request, ORIGIN, showLoading, increaseLoadingCount, decreaseLoadingCount, LoadingZero }
