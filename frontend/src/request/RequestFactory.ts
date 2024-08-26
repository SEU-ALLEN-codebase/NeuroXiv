// 根据 fetch 封装的一层请求
// 支持取消请求(AbortController), 设置超时
// request 需要先构造好(new Request(url, options)) 传给 RequestFactory 的构造函数

class RequestFactory {
    request: Request
    timeout: number
    controller: AbortController
    /**
     * 构造函数
     * @param request {Request} instance of new Request
     * @param timeout {Number} 请求超时, ms, -1 表示不设置超时
     */
    constructor (request: Request, timeout: number = -1) {
      this.request = request
      this.timeout = timeout
      // 用于取消请求的
      this.controller = new AbortController()
    }

    /**
     * 开始发送请求
     */
    start (): Promise<Response | any> {
      // 用于取消请求的
      this.controller = new AbortController()
      return new Promise(async (resolve, reject) => {
        if (this.timeout && this.timeout !== -1) {
          // 即使超时之前成功或者失败都不用清除定时器，因为 promise 的状态只能设置一次
          setTimeout(reject, this.timeout, new Error('timeout'))
        }
        try {
          const response = await fetch(this.request, {
            signal: this.controller.signal
          })
          return resolve(response)
        } catch (error) {
          if (error.name === 'AbortError') {
            console.log('user cancel')
            // return
          }
          reject(error)
        }
      })
    }

    /**
     * 取消发送请求
     */
    cancel () {
      this.controller.abort()
    }
}

export default RequestFactory
