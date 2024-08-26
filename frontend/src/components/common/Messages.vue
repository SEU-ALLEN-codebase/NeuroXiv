<template>
  <el-dropdown
    trigger="click"
    placement="bottom"
    @visible-change="updateMessageStatus"
    class="message-dropdown">
    <el-badge :value="unreadMessages.length" :max="99" :hidden="unreadMessages.length === 0" class="message-badge">
      <i class="el-icon-message-solid"></i>
    </el-badge>
    <el-dropdown-menu slot="dropdown" class="message-dropdown-menu">
      <el-dropdown-item v-if="!messageList.length">
        <span>no messages</span>
      </el-dropdown-item>
      <el-dropdown-item v-else v-for="(m, i) in messageList" :key="i">
        <div class="message-item" :class="`${m.type} ${m.status}`">
          <span class="message-content">{{ m.content }}</span>
          <el-button type="primary" size="mini" v-if="m.type === 'success'" class="action message-check-link" @click="checkMessageDetail(m)">check</el-button>
        </div>
      </el-dropdown-item>
    </el-dropdown-menu>
  </el-dropdown>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'
import { initSocket, destroySocket, getSocket } from '@/socket.io'
import { MessageDetail } from '@/types/Message'

@Component
export default class Messages extends Vue {
  @Prop({ required: true }) getMessageFunc!: Function
  @Prop({ default: '/' }) socketUrl!: string
  private messageList: MessageDetail[] = []

  private get unreadMessages () {
    return this.messageList.filter(m => m.status === 'unread')
  }

  /**
   * 查看消息详情
   * @param msgDetail 消息详情
   */
  private checkMessageDetail (msgDetail: MessageDetail) {
    this.$emit('checkMessageDetail', msgDetail)
  }

  /**
   * 点击通知按钮关闭菜单的时候把消息标记为已读
   * @param isExpanded 是否展开菜单
   */
  private async updateMessageStatus (isExpanded: boolean) {
    if (isExpanded || this.unreadMessages.length === 0) return
    this.$emit('updateMessageStatus', this.unreadMessages)
  }

  /**
   * 监听 websocket 消息, 更新未读消息
   */
  private addMessageListener () {
    const socket = getSocket()
    if (!socket) return
    socket.on('msg_resp', (data: MessageDetail) => {
      if (this.messageList.find(m => m.id === data.id)) return
      this.messageList.unshift(data)
    })
  }

  /**
   * 获取消息列表
   * @private
   */
  private async getMessages () {
    try {
      this.messageList = await this.getMessageFunc()
    } catch (e) {
      console.warn(e)
    }
  }

  private async mounted () {
    await this.getMessages()
    // 判断之前先来一次接口请求, 这样就可以更新登录状态了
    // await getUserInfo(null).start()
    if (this.$store.state.isLogin) {
      initSocket(this.socketUrl)
    }
    this.addMessageListener()
  }

  private destroyed () {
    destroySocket()
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.message-dropdown {
  color: inherit;
  .message-badge {
    cursor: pointer;
    .el-icon-message-solid {
      font-size: 23px;
    }
  }
}
</style>
<style lang="less">
.message-dropdown-menu {
  .el-dropdown-menu__item {
    font-size: 13px;
    line-height: 1.5;
  }
  .message-item {
    padding: 5px 0;
    &::before, .message-content, .action {
      vertical-align: middle;
    }
    &::before {
      content: '●';
      color: rgb(216, 216, 216);
      margin-right: 5px;
    }
    &.read::before {
      opacity: 0;
    }
    &.success::before {
      color: var(--success-color);
    }
    &.error::before {
      color: var(--error-color);
    }
    .message-content {
      display: inline-block;
      width: 325px;
      margin-right: 15px;
    }
    .action {
      cursor: pointer;
    }
  }
}
</style>
