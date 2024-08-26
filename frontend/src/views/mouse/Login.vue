<template>
  <PageWithHeaderFooter header-title="Sange The Master">
    <div class="login-options-container">
      <transition :name="!selectLoginOption ? 'slide-fade-opposite' : 'slide-fade'">
        <div class="login-options-box transition-item abs-full vertical-middle" key="options" v-if="!selectLoginOption">
          <LoginOptions class="centered" @selectLoginOption="loginOptionChangeHandler($event.detail)" />
        </div>
        <div class="mail-login transition-item abs-full vertical-middle" key="email" v-if="selectLoginOption === 'email'">
          <div class="centered">
            <MailLoginForm />
            <p class="back-to-options">
              <span class="back-btn" @click="selectLoginOption = ''"><i class="el-icon-arrow-left"></i>其他登录方式</span>
              <a href="#" class="forget-link">忘记密码?</a>
            </p>
          </div>
        </div>
      </transition>
    </div>
    <QQLogin
      ref="qqLoginBtn"
      v-show="false"
      :app-id="QQLoginAppId"
      :redirect-uri="QQLoginProxy"
      @success="loginSuccessHandler($event.detail)"
      @error="loginErrorHandler($event.detail)"
    />
  </PageWithHeaderFooter>
</template>

<script lang="ts">
import { Component, Vue, Ref } from 'vue-property-decorator'
import { loginByOpenID } from '@/request/apis/mouse/UserRequest'
import QQLogin from '@/components/common/QQLogin.vue'
import { QQUserDetail } from '@/types/QQ'
import APP_CONFIG from '../../../config.json'
import MailLoginForm from '@/components/register_login/MailLoginForm.vue'
import LoginOptions from '@/components/register_login/LoginOptions.vue'
import PageWithHeaderFooter from '@/components/common/PageWithHeaderFooter.vue'

@Component({
  components: { PageWithHeaderFooter, LoginOptions, MailLoginForm, QQLogin }
})
export default class Login extends Vue {
  QQLoginAppId = APP_CONFIG.QQ_LOGIN_APP_ID
  QQLoginProxy = `${location.origin}${APP_CONFIG.QQ_LOGIN_REDIRECT_URL}`

  @Ref('qqLoginBtn') readonly qqLoginBtn!: QQLogin
  private selectLoginOption: string = ''

  /**
   * 切换登录方式
   * @param type 登录方式, qq | wechat | email
   */
  private loginOptionChangeHandler (type: string) {
    // QQ 登录直接弹出窗口
    if (type === 'qq') {
      // @ts-ignore
      this.qqLoginBtn.showLoginWindow()
    } else {
      this.selectLoginOption = type
    }
  }

  /**
   * QQ login success
   * @param userInfo { QQUserDetail } QQ user detail
   */
  protected async loginSuccessHandler (userInfo: QQUserDetail): Promise<void> {
    console.log(userInfo)
    const loginRequest = loginByOpenID(document.body, userInfo.openId)
    try {
      const loginResult = await loginRequest.start()
      // 登录成功之后保存 token, 后续请求都要带上这个 token
      await this.$store.dispatch('updateToken', loginResult.token)
      // 登录成功之后保存用户信息
      await this.$store.dispatch('updateUserInfo', { username: userInfo.nickname, avatar: userInfo.avatar })
      // @ts-ignore
      await this.$router.push({ path: this.$route.query.redirect || `/${this.$route.params.lang}` })
    } catch (e) {
      console.log(e)
    }
  }

  /**
   * QQ login error
   * @param errMsg { string } 错误信息
   */
  protected loginErrorHandler (errMsg: string): void {
    this.$message && this.$message(errMsg)
  }
}
</script>

<style lang="less" scoped>
  .login-options-container {
    position: relative;
    width: 500px;
    height: 500px;
    .transition-item {
      text-align: center;
    }
    .mail-login {
      .back-to-options {
        text-align: left;
        font-size: 0.8em;
        .back-btn {
          cursor: pointer;
        }
        .forget-link {
          float: right;
        }
      }
    }
  }
</style>
