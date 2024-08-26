type MessageDetail = {
  id: string
  category?: string
  type: 'success' | 'error' | 'info'
  status: 'read' | 'unread'
  title?: string
  content?: string
}

export { MessageDetail }
