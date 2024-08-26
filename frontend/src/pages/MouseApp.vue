<template>
  <div id="app">
    <transition name="slide-fade">
      <router-view />
    </transition>
    <ThemeSwitcher v-show="false" />
    <BrowserUpdatePrompt />
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import BrowserUpdatePrompt from '@/components/common/BrowserUpdatePrompt.vue'
import ThemeSwitcher from '@/components/common/ThemeSwitcher.vue'

@Component({
  components: {
    ThemeSwitcher,
    BrowserUpdatePrompt
  }
})
export default class MouseApp extends Vue {}
</script>

<style lang="less" scoped>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100%;
  background-color: var(--page-background-color);
  transition: background-color .3s;
  position: relative;
  overflow: hidden;
}
.home, .login {
  position: absolute;
  width: 100%;
  height: 100%;
  left: 0;
  top: 0;
}
</style>
