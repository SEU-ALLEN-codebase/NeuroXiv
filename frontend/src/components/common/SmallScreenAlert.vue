<template>
  <el-alert
    class="small-screen-alert"
    title="Please use desktop device and maximise the window to have the best experience !"
    type="warning"
    center
    show-icon
  />
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class SmallScreenAlert extends Vue {}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.small-screen-alert {
  width: 100vw;
  display: none;
}
@media screen and (max-width: 500px) {
  .small-screen-alert {
    display: block;
  }
}
</style>
