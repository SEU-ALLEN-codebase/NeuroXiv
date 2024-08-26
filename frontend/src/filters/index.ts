/** 全局 filters */

import Vue from 'vue'
import { addEllipsisToText, addThousandDelimiter } from '@/utils/util'

/**
 * 保留 N 位小数
 * @param count 要保留的小数位数
 */
Vue.filter('fixNumber', (value: any, count: number) => {
  if (typeof value === 'undefined') return ''
  if (isNaN(value)) return value
  return parseFloat(value.toFixed(count))
})

/**
 * 转换为百分比显示
 * @param count 要保留的小数位数
 */
Vue.filter('toPercent', (value: any, count: number) => {
  if (typeof value === 'undefined') return ''
  if (isNaN(value)) return value
  return `${(value * 100).toFixed(count)}%`
})

/**
 * 添加千分位分隔符
 */
Vue.filter('addThousandDelimiter', (value: number) => {
  return addThousandDelimiter(value)
})

// 截断文本并添加省略号
Vue.filter('toEllipsisText', (text: string, len: number) => addEllipsisToText(text, len))
