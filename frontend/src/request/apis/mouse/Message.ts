import { RequestOptions } from '@/types/Request'
import { request } from '@/request/RequestWrapper'

const REQUEST_NAME_SPACE = 'message'

/**
 * 获取消息列表
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param requestOptions { RequestOptions } 请求选项
 */
function getMessageList (loadingTarget: HTMLElement | null, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}/list`
  const options: RequestInit = {
    method: 'get'
  }
  requestOptions.successMsg = requestOptions.successMsg || '获取消息列表成功'
  requestOptions.errorMsg = requestOptions.errorMsg || '获取消息列表失败'
  const params = { url, loadingTarget, options, ...requestOptions }
  return request(params)
}

export { getMessageList }
