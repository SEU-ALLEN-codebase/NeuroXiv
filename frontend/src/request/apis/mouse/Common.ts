import { RequestOptions } from '@/types/Request'
import { request } from '@/request/RequestWrapper'

const REQUEST_NAME_SPACE = 'common'

/**
 * 上传文件
 * @param loadingTarget 要显示 loading 的元素
 * @param path { string } 上传文件的路径
 * @param file { File } 上传的文件
 * @param requestOptions 请求选项
 */
function upload (loadingTarget: HTMLElement | null, { path, file }: any, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}/upload`
  const formData = new FormData()
  formData.append('file', file)
  formData.append('path', path)
  const options: RequestInit = {
    body: formData,
    headers: {}
  }
  requestOptions.successMsg = requestOptions.successMsg || 'Upload success'
  requestOptions.errorMsg = requestOptions.errorMsg || 'Upload error'
  const params = { url, loadingTarget, options, ...requestOptions }
  return request(params)
}

/**
 * 检查验证码是否正确
 * @param loadingTarget 要显示 loading 的元素
 * @param captcha 验证码
 * @param requestOptions 请求选项
 */
function checkCaptcha (loadingTarget: HTMLElement | null, captcha: string, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}/checkCaptcha`
  const options: RequestInit = {
    body: `captcha=${captcha}`
  }
  requestOptions.successMsg = requestOptions.successMsg || 'captcha right'
  requestOptions.errorMsg = requestOptions.errorMsg || 'captcha wrong'
  const params = { url, loadingTarget, options, ...requestOptions }
  return request(params)
}

export { upload, checkCaptcha }
