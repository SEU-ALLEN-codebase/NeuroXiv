<template>
  <div>
    <el-button type="primary" @click="showLoginWindow()">QQ login</el-button>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component
export default class QQLogin extends Vue {
  @Prop() private appId!: string
  @Prop() private redirectUri!: string

  get QQLoginUrl () {
    const BASE_URL = 'https://graph.qq.com/oauth2.0/authorize'
    return `${BASE_URL}?client_id=${this.appId}&response_type=token&scope=get_user_info&redirect_uri=${encodeURIComponent(this.redirectUri)}`
  }

  /**
   * 开始 QQ 登录, 弹出 QQ 登录窗口
   */
  public showLoginWindow (): void {
    let qqLoginUrl = this.QQLoginUrl
    let popupParams = 'scrollbars=no,resizable=no,status=no,location=no,toolbar=no,menubar=no,width=500,height=600,left=100,top=100'
    window.open(qqLoginUrl, 'qq_login', popupParams)
  }

  private mounted (): void {
    // 监听 QQ 登录回调页面发送过来的消息
    let handler = (e: MessageEvent) => {
      // 只监听 QQ login proxy 发送过来的消息, 这里注意 source 要为 'login-proxy'
      if (e.origin !== location.origin || e.source === window || e.data.source !== 'login-proxy') return
      if (e.data.code === 0) {
        this.$emit('success', new CustomEvent('success', {
          detail: e.data.data
        }))
      } else {
        this.$emit('error', new CustomEvent('error', {
          detail: e.data.msg
        }))
      }
      window.removeEventListener('message', handler)
    }
    window.addEventListener('message', handler)
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">

</style>
