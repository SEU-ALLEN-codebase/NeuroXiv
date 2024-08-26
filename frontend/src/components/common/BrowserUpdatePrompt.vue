<template>
  <el-dialog
    :title="$t('browser.browserUpdateTitle')"
    :visible.sync="dialogVisible"
    :show-close="false"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <p>{{ $t('browser.browserUpdateMessage') }}</p>
    <div class="browser-list">
      <el-link
        v-for="browser in browserList"
        :key="browser.name"
        class="browser-item"
        :class="browser.name"
        :href="browser.href"
        target="_blank"
      >
        <i :class="`icomoon-icon-${browser.name}`" />
      </el-link>
    </div>
  </el-dialog>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class BrowserUpdatePrompt extends Vue {
  public dialogVisible: boolean = navigator.userAgent.includes('Trident') // 屏蔽 IE
  private browserList = [
    { name: 'chrome', href: 'https://www.google.cn/chrome/' },
    { name: 'firefox', href: 'https://www.firefox.com.cn' }
  ]
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.browser-list {
  margin-top: 20px;
  .browser-item {
    margin-right: 30px;
    font-size: 3em;
  }
}
</style>
