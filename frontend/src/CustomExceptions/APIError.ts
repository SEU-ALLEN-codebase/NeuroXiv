// 请求接口 response code !== 0
export default class APIError extends Error {
  constructor (...params: string[]) {
    // Pass remaining arguments (including vendor specific ones) to parent constructor
    super(...params)

    // Maintains proper stack trace for where our error was thrown (only available on V8)
    // @ts-ignore
    if (Error.captureStackTrace) {
      // @ts-ignore
      Error.captureStackTrace(this, APIError)
    }

    this.name = 'APIError'
  }
}
