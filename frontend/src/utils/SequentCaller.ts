/**
 * 顺序执行回调, 确保后续的回调执行结果不会被前面的覆盖
 * 例如验证码检测操作, 会不断发送请求验证, 请求结果什么时候返回是不确定的, 有可能后面发送的请求结果先返回, 这里可以确保后续的结果不会被前面的覆盖
 */

class SubsequentCaller {
  private _formerHandler: Function
  private _afterCallback: Function
  private _currentHandlerSequence: number // 最近一次 formerHandler 执行的 sequence
  private _currentCallbackSequence: number // 最近一次 afterCallback 执行的 sequence

  /**
   * constructor
   * @param formerHandler 回调执行前的异步处理, 返回 promise, 这一步获取到的结果会传给 afterCallback
   * @param afterCallback 异步处理完之后执行的回调
   */
  constructor (formerHandler: Function, afterCallback: Function) {
    this._formerHandler = formerHandler
    this._afterCallback = afterCallback
    this._currentHandlerSequence = 0
    this._currentCallbackSequence = 0
  }

  /**
   * 开始执行, 即使不断执行这个函数, 也可以确保后续操作的结果不会被前面的覆盖
   * @param thisArg this 指向
   * @param args 传给 formerHandler 的其他参数
   */
  async start (thisArg: any, ...args: any) {
    let handlerSequence = ++this._currentHandlerSequence
    const result = await this._formerHandler.apply(thisArg, args)
    if (handlerSequence > this._currentCallbackSequence) {
      this._currentCallbackSequence = handlerSequence
      this._afterCallback.call(thisArg, result)
    }
  }
}

export default SubsequentCaller
