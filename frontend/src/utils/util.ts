/**
 * 等待一段时间
 * @param ms { number } 等待时长(毫秒)
 */
function sleep (ms: number) {
  return new Promise(resolve => {
    setTimeout(resolve, ms)
  })
}

/**
 * 根据对象生成 URL 中的以 "&" 连接的字符串
 * @param paramsObj { object } json 对象
 */
function queryStringBuilder (paramsObj: any) {
  let searParams = new URLSearchParams()
  for (let prop in paramsObj) {
    if (!paramsObj.hasOwnProperty(prop)) continue
    if (typeof paramsObj[prop] === 'undefined') continue
    searParams.append(prop, paramsObj[prop])
  }
  return searParams.toString()
}

/**
 * 获取系统语言设置
 */
function getSystemLang () {
  let lang = navigator.language.split('-')[0]
  if (lang.toLowerCase() === 'zh') lang = 'cn'
  return lang
}

/**
 * 等待 ⌛️ func resolve, 每隔一段时间判断一下, 直到 resolve 或者 reject 或者超过最大次数
 * @param func { Function } 要等待 resolve 的方法
 * @param delay { number } 时间间隔 ms
 * @param tryCount { number } 最多尝试次数
 */
function wait (func: Function, delay: number, tryCount: number) {
  return new Promise((resolve, reject) => {
    let count = 0
    const fn = async () => {
      try {
        let result = await func()
        count++
        if (result) {
          resolve(result)
        } else {
          if (count >= tryCount) {
            reject(new Error('max count'))
          } else {
            setTimeout(fn, delay)
          }
        }
      } catch (e) {
        reject(e)
      }
    }
    fn().then()
  })
}

/**
 * 添加千分位分隔符
 * @param value 原始数字
 */
function addThousandDelimiter (value: number) {
  let strVal = String(value)
  let [ integerPart, floatPart ] = strVal.split('.')
  let integerSlices = []
  let reversedInteger = integerPart.split('').reverse().join('')
  for (let i = 0; i < reversedInteger.length; i += 3) {
    integerSlices.push(reversedInteger.slice(i, i + 3))
  }
  let thousandSplicedInteger = integerSlices.join(',').split('').reverse().join('')
  if (floatPart) return `${thousandSplicedInteger}.${floatPart}`
  return thousandSplicedInteger
}

/**
 * 截断文本并添加省略号
 * @param text 要添加省略号的文本
 * @param truncateLength 要截断的长度
 */
function addEllipsisToText (text: string, truncateLength: number) {
  if (text.length <= truncateLength) return text
  return text.substr(0, truncateLength).replace(/\.+$/g, '') + '...'
}

/**
 * 判断是否为苹果设备, Mac iPad iPhone
 */
function isAppleDevice () {
  let ua = navigator.userAgent
  return ua.includes('Macintosh') || ua.includes('iPad') || ua.includes('iPhone')
}

/**
 * 线性插值的方式获取两个颜色之间的某个颜色
 * @param left 左侧的颜色, [r, g, b] | [r, g, b, a]
 * @param right 右侧的颜色, [r, g, b] | [r, g, b, a]
 * @param percent 要获取颜色的位置, 例如 0.5
 * @return 最后生成的颜色, [r, g, b] | [r, g, b, a]
 */
function findColorBetween (left: number[], right: number[], percent: number): number[] {
  let newColor: number[] = []
  for (let i = 0; i < left.length; i++) {
    let colorComponent = Math.round(left[i] + (right[i] - left[i]) * percent)
    newColor.push(colorComponent)
  }
  return newColor
}

/**
 * 下载
 * @param url 要下载的链接
 * @param fileName 下载文件名
 */
async function downloadLink (url: string, fileName: string) {
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', fileName)
  link.style.position = 'absolute'
  link.style.width = '0'
  link.style.height = '0'
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  await sleep(1) // Safari 不添加延时下载不了
  link.click()
  document.body.removeChild(link)
}

/**
 * 把 canvas 转换为 blob
 * @param canvas
 */
function getBlobFromCanvas (canvas: HTMLCanvasElement) {
  return new Promise(resolve => {
    canvas.toBlob(resolve)
  })
}

export {
  sleep,
  queryStringBuilder,
  getSystemLang,
  wait,
  addThousandDelimiter,
  addEllipsisToText,
  isAppleDevice,
  findColorBetween,
  downloadLink,
  getBlobFromCanvas
}
