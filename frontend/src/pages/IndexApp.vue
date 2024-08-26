<template>
  <div id="app">
    <SmallScreenAlert />
    <header-bar>
      <router-link :to="getCompleteRouteByPathString('about')">
        <el-button
          type="primary"
          plain
        >
          About
        </el-button>
      </router-link>
    </header-bar>
    <transition name="slide-fade">
      <router-view />
    </transition>
    <ThemeSwitcher v-show="false" />
    <footer>
      Ver 1.0. Copyright 2021.
      <a
        href="https://beian.miit.gov.cn"
        target="_blank"
      >
        【备案号：粤B2-20090059】
      </a>
    </footer>
  </div>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import HeaderBar from '@/components/mouse/HeaderBar.vue'
import RouterHelper from '@/mixins/RouterHelper.vue'
import ThemeSwitcher from '@/components/common/ThemeSwitcher.vue'
import LangSwitcher from '@/components/common/LangSwitcher.vue'
import SmallScreenAlert from '@/components/common/SmallScreenAlert.vue'

@Component({
  components: {
    SmallScreenAlert,
    LangSwitcher,
    ThemeSwitcher,
    HeaderBar
  }
})
export default class IndexApp extends RouterHelper {}
</script>

<style lang="less" scoped>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100%;
  background-color: var(--page-background-color);
  position: relative;
  min-width: 1300px;
  footer {
    position: absolute;
    color: grey;
    font-size: 0.8em;
    bottom: 30px;
    width: 100%;
    text-align: center;
  }
}
</style>
<style lang="less">
body {
  overflow: auto;
}
</style>
