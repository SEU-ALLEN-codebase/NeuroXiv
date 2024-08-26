<template>
  <div class="login-options">
    <h2>选择登录方式</h2>
    <ul class="options-list">
      <li class="option-item" @click="selectLoginOption('qq')">
        <img class="option-logo" src="@/assets/login_register/qq.svg" alt="QQ" />
        <span class="option-label">QQ 登录</span>
      </li>
      <li class="option-item" @click="selectLoginOption('email')">
        <img class="option-logo" src="@/assets/login_register/phone_mail.svg" alt="Phone or Mail" />
        <span class="option-label">邮箱登录</span>
      </li>
      <li class="option-item disabled" @click="selectLoginOption('wechat')">
        <img class="option-logo" src="@/assets/login_register/wechat.svg" alt="WeChat" />
        <span class="option-label">微信登录</span>
      </li>
    </ul>
    <p>
      没有账号？
      <router-link :to="{ name: 'register' }">立即注册</router-link>
    </p>
  </div>
</template>

<script lang="ts">
  import { Component, Vue } from 'vue-property-decorator'

  @Component
  export default class LoginOptions extends Vue {
    /**
     * 选择登录方式
     */
    private selectLoginOption (type: string) {
      this.$emit('selectLoginOption', new CustomEvent('selectLoginOption', {
        detail: type
      }))
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
  .login-options {
    text-align: center;
    font-size: .8em;
    .options-list {
      margin: 60px 0;
      .option-item {
        cursor: pointer;
        display: inline-block;
        margin: 0 30px;
        .option-logo {
          display: block;
          margin: 0 auto 10px;
          height: 50px;
        }
      }
    }
  }
</style>
