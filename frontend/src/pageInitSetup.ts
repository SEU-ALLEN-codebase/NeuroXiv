// 每个页面的初始化设置
import { isAppleDevice } from '@/utils/util'

// 非苹果设备添加滚动条样式
if (!isAppleDevice()) {
  document.documentElement.classList.add('tiny-scrollbar')
}
