import { LoginCredentials, RequestOptions } from '@/types/Request'
import { request } from '@/request/RequestWrapper'
import i18n from '@/i18n/mouse'
import RequestFactory from '@/request/RequestFactory'
import { queryStringBuilder, wait } from '@/utils/util'
import { Loading, Notification } from 'element-ui'
import { ElLoadingComponent } from 'element-ui/types/loading'

const REQUEST_NAME_SPACE = 'user'

/**
 * 获取当前登录用户的相关信息
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param requestOptions { RequestOptions } 请求选项
 */
function getUserInfo (loadingTarget: HTMLElement | null, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}/info`
  const options: RequestInit = {
    method: 'get'
  }
  requestOptions.successMsg = requestOptions.successMsg || `${i18n.t('request.getUserInfoSuccess')} 🎉`
  requestOptions.errorMsg = requestOptions.errorMsg || `${i18n.t('request.getUserInfoError')} 😫`
  const params = { url, loadingTarget, options, ...requestOptions }
  return request(params)
  // let r = request(params)
  // let originR = r.start.bind(r)
  // r.start = () => originR().then((data) => {
  //   // 这里可以做数据适配
  //   return data
  // }).catch(e => {
  //   if (e.message.includes('not login')) {
  //     throw new NotLoginError(e.message)
  //   } else {
  //     throw e
  //   }
  // })
  // return r
}

/**
 * 用户登录
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param username { string } username
 * @param password { string } password
 * @param email 电子邮件
 * @param requestOptions { RequestOptions } 请求选项
 */
function login (loadingTarget: HTMLElement | null, { username, password, email }: LoginCredentials, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}/login?${queryStringBuilder(arguments[1])}`
  const options: RequestInit = {
    method: 'get'
  }
  requestOptions.successMsg = requestOptions.successMsg || 'login success 🎉'
  requestOptions.errorMsg = requestOptions.errorMsg || 'login error 😫'
  const params = { url, loadingTarget, options, ...requestOptions }
  return request(params)
}

/**
 * login by open id
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param openId { string } qq open id
 * @param requestOptions { RequestOptions } 请求选项
 */
function loginByOpenID (loadingTarget: HTMLElement | null, openId: string, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}/loginByOpenID?openId=${openId}`
  const options: RequestInit = {
    method: 'get'
  }
  requestOptions.successMsg = requestOptions.successMsg || 'login success 🎉'
  requestOptions.errorMsg = requestOptions.errorMsg || 'login error 😫'
  const params = { url, loadingTarget, options, ...requestOptions }
  return request(params)
}

/**
 * 退出登录
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param requestOptions { RequestOptions } 请求选项
 */
function logout (loadingTarget: HTMLElement | null, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}/logout`
  const options: RequestInit = {
    method: 'get'
  }
  requestOptions.successMsg = requestOptions.successMsg || 'logout success 🎉'
  requestOptions.errorMsg = requestOptions.errorMsg || 'logout error 😫'
  const params = { url, loadingTarget, options, ...requestOptions }
  return request(params)
}
// 下面是合并多个请求的示例

/**
 * 提交一个获取用户列表的任务, 返回一个任务 ID, 后续使用这个 ID 异步轮询获取结果
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param requestOptions { RequestOptions } 请求选项
 */
function _createGetUserListTask (loadingTarget: HTMLElement | null, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}/createGetUserListTask`
  const options: RequestInit = {
    method: 'get'
  }
  requestOptions.successMsg = requestOptions.successMsg || 'create task ok 🎉'
  requestOptions.errorMsg = requestOptions.errorMsg || 'create task error 😫'
  const params = { url, loadingTarget, options, ...requestOptions }
  return request(params)
}

/**
 * 根据 job id 获取用户列表
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param jobId { string } 任务 ID
 * @param requestOptions { RequestOptions } 请求选项
 */
function _getUserListByJobId (loadingTarget: HTMLElement | null, jobId: string, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}/getUserListById?id=${jobId}`
  const options: RequestInit = {
    method: 'get'
  }
  requestOptions.successMsg = requestOptions.successMsg || 'get user list success 🎉'
  requestOptions.errorMsg = requestOptions.errorMsg || 'get user list error 😫'
  const params = { url, loadingTarget, options, ...requestOptions }
  return request(params)
}

/**
 * 异步获取用户列表(合并几个接口调用的例子)
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 */
function getUserListAsync (loadingTarget: HTMLElement | null) {
  const tryCount = 2
  const tryDelay = 1000
  let createTaskRequest: RequestFactory
  let userListRequest: RequestFactory
  let canceled = false
  const check = function () {
    if (canceled) {
      return Promise.reject(new Error('user cancel'))
    }
    return userListRequest.start().then(result => {
      if (result.status === 'complete') {
        return result.users
      } else {
        return false
      }
    })
  }
  return {
    start () {
      canceled = false
      return new Promise(async (resolve, reject) => {
        // show loading
        let loadingInstance: ElLoadingComponent
        if (loadingTarget) {
          loadingInstance = Loading.service({
            target: loadingTarget,
            text: 'loading data...',
            background: 'transparent'
          })
        }
        try {
          createTaskRequest = _createGetUserListTask(null, { showSuccessMsg: false, showErrorMsg: false })
          const id = await createTaskRequest.start()
          userListRequest = _getUserListByJobId(null, id, { showSuccessMsg: false, showErrorMsg: false })
          const result = await wait(check, tryDelay, tryCount)
          // show success
          Notification.success({
            title: 'get user list success',
            message: ''
          })
          resolve(result)
        } catch (e) {
          Notification.error({
            title: 'get user list error',
            message: e.message
          })
          reject(e)
        }
        // @ts-ignore
        loadingInstance && loadingInstance.close()
      })
    },
    cancel () {
      createTaskRequest && createTaskRequest.cancel()
      userListRequest && userListRequest.cancel()
      canceled = true
    }
  }
}

export { getUserInfo, login, logout, loginByOpenID, getUserListAsync }
