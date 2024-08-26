<template>
  <div class="s-captcha-container">
    <el-input v-model="captchaInput" class="captcha-input" placeholder="输入验证码" @input.native="checkCaptcha">
      <i slot="suffix" class="captcha-status el-icon-circle-check" v-if="captchaIsCorrect"></i>
    </el-input>
    <img :src="noCacheCaptchaImageUrl" alt="captcha" class="captcha-img" title="点击图片更新验证码" @click="updateCaptchaImg" />
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator'
import SequentCaller from '@/utils/SequentCaller'

@Component
export default class CaptchaInput extends Vue {
  @Prop({ required: true }) captchaImageUrl!: string
  @Prop() value!: string
  @Prop({ required: true }) captchaChecker!: Function // 接收验证码参数, 返回 promise

  public captchaIsCorrect: boolean = false

  private noCacheCaptchaImageUrl: string = ''

  private sequentChecker!: SequentCaller

  get captchaInput () {
    return this.value
  }

  set captchaInput (value: string) {
    this.$emit('input', value)
  }

  /**
   * 更新验证码图片
   */
  private updateCaptchaImg () {
    this.noCacheCaptchaImageUrl = `${this.captchaImageUrl}?nocache=${Date.now()}`
    this.captchaIsCorrect = false
  }

  /**
   * 检查验证码是否正确
   */
  private async checkCaptcha () {
    await this.$nextTick() // Firefox 要加上这个, 否则获取的结果是上一次输入的, chrome safari 正常
    await this.sequentChecker.start(null, this.value)
  }

  mounted () {
    this.updateCaptchaImg()
    this.sequentChecker = new SequentCaller(this.captchaChecker, (result: boolean) => {
      this.captchaIsCorrect = result
    })
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.s-captcha-container {
  height: 40px;
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  .captcha-input {
    margin-right: 10px;
    /deep/ .el-input__suffix {
      line-height: 40px;
    }
    .captcha-status {
      margin-right: 8px;
      color: green;
    }
  }
  .captcha-img {
    border-radius: 3px;
    cursor: pointer;
    height: 100%;
  }
}
</style>
