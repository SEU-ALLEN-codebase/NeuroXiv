// 包含本地存储的各种设置, 例如 token storage
// 统一在这里设置有两个好处:
// 1、可以很方便地修改存储的方式, 例如原来是 cookie 存储的, 要改为 session 存储的话, 统一在这里修改就行了, 否则在每个调用的地方都要改一下
// 2、方便统一指定 key 的 name, 例如 `Cookies.set(name, value)`, 要修改这个 name 的话统一在这里修改就行了, 并且其他使用的地方都不用再指定 name 了

import Cookies from 'js-cookie'

// cookie 存储
class CookieStorage {
  private readonly name: string
  private readonly path: string
  private readonly expires: number | Date

  /**
   * constructor
   * @param name { string } cookie name
   * @param path { string } cookie path
   * @param expires { number | Date } 过期时间, number 表示天数
   */
  constructor (name: string, path: string = '', expires: number | Date = 365) {
    this.name = name
    this.path = path
    this.expires = expires
  }

  /**
   * 获取相应的 cookie
   */
  public get () {
    return Cookies.get(this.name)
  }

  /**
   * 设置 cookie
   * @param value { string } cookie value
   */
  public set (value: string) {
    Cookies.set(this.name, value, { path: this.path, expires: this.expires })
  }

  /**
   * remove cookie
   */
  public remove () {
    Cookies.remove(this.name, { path: this.path })
  }
}

// local storage 存储
class LocalStore {
  private readonly name: string

  /**
   * constructor
   * @param name { string } local storage item name
   */
  constructor (name: string) {
    this.name = name
  }

  /**
   * 获取相应的 local item
   */
  public get () {
    return localStorage.getItem(this.name)
  }

  /**
   * 设置 local item
   * @param value { string } local item value
   */
  public set (value: string) {
    localStorage.setItem(this.name, value)
  }

  /**
   * remove local item
   */
  public remove () {
    localStorage.removeItem(this.name)
  }
}

export { CookieStorage, LocalStore }
