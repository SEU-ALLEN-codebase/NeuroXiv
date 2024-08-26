<template>
  <div class="mail-login-form">
    <h2 class="form-title">
      电子邮箱登录
    </h2>
    <el-form
      ref="form"
      :model="form"
      :rules="rules"
    >
      <el-form-item prop="email">
        <el-input
          v-model="form.email"
          type="email"
          placeholder="请输入电子邮箱地址"
        />
      </el-form-item>
      <el-form-item prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入登录密码"
        />
      </el-form-item>
      <el-form-item
        prop="captcha"
        class="captcha-form-item"
      >
        <CaptchaInput
          ref="captchaInput"
          v-model="form.captcha"
          captcha-image-url="/api/common/captcha"
          :captcha-checker="checkCaptcha"
        />
      </el-form-item>
      <el-form-item class="submit-form-item">
        <el-button
          :loading="loading"
          type="primary"
          class="login-btn"
          @click="loginHandler"
        >
          登录
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Ref } from 'vue-property-decorator'
import { LoginCredentials } from '@/types/Request'
import { login } from '@/request/apis/mouse/UserRequest'
import { checkCaptcha } from '@/request/apis/mouse/Common'
import { ElForm } from 'element-ui/types/form'
import CaptchaInput from '@/components/common/CaptchaInput.vue'

  @Component({
    components: {
      CaptchaInput
    }
  })
export default class MailLoginForm extends Vue {
    @Ref('form') readonly submitForm!: ElForm
    @Ref('captchaInput') readonly captchaInput!: CaptchaInput

    private form: LoginCredentials = {
      username: '',
      email: '',
      password: '',
      captcha: ''
    }
    private loading: boolean = false

    private get rules () {
      const checkCaptcha = (rule: any, value: string, callback: Function) => {
        if (!value) {
          return callback(new Error('验证码不能为空'))
        }
        // @ts-ignore
        if (!this.captchaInput.captchaIsCorrect) {
          return callback(new Error('验证码错误'))
        }
        callback()
      }
      return {
        email: [
          { required: true, message: '电子邮箱不能为空', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '密码不能为空', trigger: 'blur' }
        ],
        captcha: [
          { validator: checkCaptcha, trigger: 'blur' }
        ]
      }
    }

    /**
     * 检查验证码是否正确
     * @param value 输入的验证码
     */
    private checkCaptcha (value: string) {
      return checkCaptcha(null, value, { showSuccessMsg: false, showErrorMsg: false }).start().then(() => {
        return true
      }).catch(() => {
        return false
      })
    }

    /**
     * 登录
     */
    private loginHandler () {
      this.submitForm.validate(async (valid) => {
        if (valid) {
          this.loading = true
          const loginRequest = login(null, this.form)
          try {
            const loginResult = await loginRequest.start()
            // 登录成功之后保存 token, 后续请求都要带上这个 token
            await this.$store.dispatch('updateToken', loginResult.token)
            // 登录成功之后保存用户信息
            await this.$store.dispatch('updateUserInfo', { username: loginResult.username })
            // @ts-ignore
            await this.$router.push({ path: this.$route.query.redirect || `/${this.$route.params.lang}` })
          } catch (e) {
            console.log(e)
          }
          this.loading = false
        } else {
          return false
        }
      })
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
  .mail-login-form {
    width: 330px;
    .form-title {
      margin-bottom: 40px;
    }
    .submit-form-item {
      margin-top: 40px;
      .login-btn {
        width: 100%;
      }
    }
  }
</style>
