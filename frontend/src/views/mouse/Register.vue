<template>
  <PageWithHeaderFooter header-title="Sange The Master">
    <MailRegisterForm
      v-if="!registerSuccess"
      @registerSuccess="registerSuccess = true"
    />
    <OperationResultTips
      v-else
      type="success"
      tips-title="Congrats! Register success!"
      tips-content="An activation link has been sent to your email, please follow the instruction to activate your account."
    >
      <div slot="operations">
        <el-button
          type="primary"
          @click="loginNowHandler"
        >
          login now
        </el-button>
        <el-button
          type="primary"
          @click="$router.push('/')"
        >
          home
        </el-button>
      </div>
    </OperationResultTips>
  </PageWithHeaderFooter>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import PageWithHeaderFooter from '@/components/common/PageWithHeaderFooter.vue'
import MailRegisterForm from '@/components/register_login/MailRegisterForm.vue'
import OperationResultTips from '@/components/common/OperationResultTips.vue'
import RouterHelper from '@/mixins/RouterHelper.vue'

  @Component({
    components: {
      PageWithHeaderFooter,
      MailRegisterForm,
      OperationResultTips
    }
  })
export default class Register extends RouterHelper {
    private registerSuccess: boolean = false

    /**
     * 点击立即登录按钮
     */
    private loginNowHandler () {
      // @ts-ignore
      this.$router.push(this.getCompleteRouteByPathString('login'))
    }
}
</script>

<style lang="less" scoped>

</style>
