<template>
  <div class="tips-container">
    <i class="tips-icon el-icon-circle-check success" v-if="type === 'success'"></i>
    <i class="tips-icon el-icon-circle-close error" v-if="type === 'error'"></i>
    <div class="tips-info">
      <h4 class="tips-title">{{ tipsTitle }}</h4>
      <p class="tips-content">{{ tipsContent }}</p>
    </div>
    <slot name="operations"></slot>
  </div>
</template>

<script lang="ts">
  import { Component, Vue, Prop } from 'vue-property-decorator'

  @Component
  export default class OperationResultTips extends Vue {
    @Prop() tipsTitle!: string
    @Prop() tipsContent!: string
    @Prop() type!: string // 提示类型, success | error
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
  .tips-container {
    width: 420px;
    text-align: center;
    .tips-icon {
      font-size: 6em;
      display: block;
      margin: auto;
      &.success {
        color: var(--success-color);
      }
      &.error {
        color: var(--error-color);
      }
    }
    .tips-info {
      margin: 25px 0;
      .tips-title {
        font-size: 1.5em;
      }
    }
  }
</style>
