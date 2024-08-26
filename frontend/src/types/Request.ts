// 请求相关的各种类型定义

// 请求设置的参数
interface RequestDetail {
  url: string
  loadingTarget: HTMLElement | null // 要显示 loading 的 element
  options: RequestInit // 最后实际发生的 fetch 请求设置的选项
  timeout?: number
  showSuccessMsg?: boolean
  showErrorMsg?: boolean
  successMsg?: string
  errorMsg?: string
}
// 请求设置的选项, 例如是否显示提示信息等
interface RequestOptions {
  showSuccessMsg?: boolean
  showErrorMsg?: boolean
  successMsg?: string
  errorMsg?: string
}
// 请求返回数据的格式
interface ResponseData {
  code: number
  msg?: string
  data?: object
}
// 登录验证信息
interface LoginCredentials {
  username: string
  password: string
  password2?: string
  email: string
  captcha: string
}

export { RequestDetail, RequestOptions, ResponseData, LoginCredentials }
