// not login error
import APIError from '@/CustomExceptions/APIError'
export default class NotLoginError extends APIError {
  constructor (...params: string[]) {
    // Pass remaining arguments (including vendor specific ones) to parent constructor
    super(...params)

    // Maintains proper stack trace for where our error was thrown (only available on V8)
    // @ts-ignore
    if (Error.captureStackTrace) {
      // @ts-ignore
      Error.captureStackTrace(this, NotLoginError)
    }

    this.name = 'NotLoginError'
  }
}
