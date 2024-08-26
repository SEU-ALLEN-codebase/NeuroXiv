import { Notification } from 'element-ui'
import io from 'socket.io-client'
import { MessageDetail } from '@/types/Message'

let socket: SocketIOClient.Socket

/**
 * 显示消息提示
 * @param msgDetail 消息详情
 */
function showNotification (msgDetail: MessageDetail) {
  const notify = Notification({
    title: msgDetail.title || '',
    type: msgDetail.type,
    // dangerouslyUseHTMLString: true,
    duration: 5000,
    message: msgDetail.content || '',
    onClick: () => {
      console.log('message click')
      notify.close()
    }
  })
}

/**
 * 建立 websocket 连接
 */
function initSocket (wsUrl: string = '/') {
  socket = io(wsUrl, { transports: ['websocket'] })
  socket.on('msg_resp', function (data: MessageDetail) {
    showNotification(data)
  })
  return socket
}

// 销毁 websocket 连接
function destroySocket () {
  if (!socket) return
  socket.off('msg_resp')
  socket.close()
  // @ts-ignore
  socket.destroy()
  // @ts-ignore
  socket = null
}

// 获取 socket 对象, 因为刚开始没有初始化, 所以后面通过这个方法获取
function getSocket () {
  return socket
}

export { initSocket, destroySocket, getSocket }
