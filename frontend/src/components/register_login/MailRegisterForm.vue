<template>
  <div class="mail-register-form">
    <h2 class="form-title">
      📧 邮箱注册
    </h2>
    <el-form
      ref="form"
      :model="form"
      :rules="rules"
    >
      <el-form-item prop="username">
        <el-input
          v-model="form.username"
          type="text"
          placeholder="请输入名用户"
        />
      </el-form-item>
      <el-form-item prop="email">
        <el-input
          v-model="form.email"
          type="email"
          placeholder="请输入电子邮箱"
        />
      </el-form-item>
      <el-form-item prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
        />
      </el-form-item>
      <el-form-item prop="password2">
        <el-input
          v-model="form.password2"
          type="password"
          placeholder="请再次输入密码"
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
      <el-form-item
        prop="readDisclaimer"
        class="disclaimer-form-item"
      >
        <el-checkbox v-model="readDisclaimer">
          I have read and agree <router-link
            target="_blank"
            :to="getCompleteRouteByPathString('disclaimer')"
          >
            《Disclaimer》
          </router-link>
        </el-checkbox>
      </el-form-item>
      <el-form-item class="submit-form-item">
        <el-button
          :disabled="!readDisclaimer"
          :loading="loading"
          type="primary"
          class="register-btn"
          @click="registerHandler"
        >
          注册
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script lang="ts">
import { Component, Ref } from 'vue-property-decorator'
import { LoginCredentials } from '@/types/Request'
import { checkCaptcha } from '@/request/apis/mouse/Common'
import { ElForm } from 'element-ui/types/form'
// @ts-ignore
import CaptchaInput from '@/components/common/CaptchaInput.vue'
// @ts-ignore
import RouterHelper from '@/mixins/RouterHelper.vue'

  // @ts-ignore
  @Component({
    components: {
      CaptchaInput
    }
  })
export default class MailRegisterForm extends RouterHelper {
    // @ts-ignore
    @Ref('form') readonly submitForm!: ElForm
    // @ts-ignore
    @Ref('captchaInput') readonly captchaInput!: CaptchaInput

    private form: LoginCredentials = {
      username: '',
      email: '',
      password: '',
      password2: '',
      captcha: ''
    }
    private loading: boolean = false
    private readDisclaimer: boolean = false

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
      const checkConfirmPassword = (rule: any, value: string, callback: Function) => {
        if (!(this.form.password === this.form.password2)) {
          return callback(new Error('Passwords do not match'))
        }
        callback()
      }
      return {
        username: [
          { required: true, message: '用户名不能为空', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '电子邮件不能为空', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '密码不能为空', trigger: 'blur' }
        ],
        password2: [
          { required: true, message: '确认密码不能为空', trigger: 'blur' },
          { validator: checkConfirmPassword, trigger: 'blur' }
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
     * 注册
     */
    private registerHandler () {
      this.submitForm.validate(async (valid) => {
        if (valid) {
          this.loading = true
          try {
            // await register(null, {
            //   username: this.form.username,
            //   password: this.form.password,
            //   email: this.form.email
            // }).start()
            // @ts-ignore
            this.$emit('registerSuccess')
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
  .mail-register-form {
    width: 450px;
    .form-title {
      margin-bottom: 40px;
      text-align: center;
    }
    .disclaimer-form-item {
      text-align: center;
    }
    .submit-form-item {
      margin-top: 40px;
      .register-btn {
        width: 100%;
      }
    }
  }
</style>
