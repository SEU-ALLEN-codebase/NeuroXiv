<template>
  <VerticalLineSplitList :data="themes" v-model="theme" @item-change="themeChangeHandler($event.value)" />
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { setTheme } from "@/theme"
import { Theme } from "@/types/Theme"
import VerticalLineSplitList from "@/components/common/VerticalLineSplitList.vue"

@Component({
  components: { VerticalLineSplitList }
})
export default class ThemeSwitcher extends Vue {
  private theme: Theme = 'auto'
  private darkModeMediaQuery: MediaQueryList

  constructor () {
    super()
    this.darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    this.theme = <"light" | "dark" | "auto">this.$store.state.stores.themeStore.get() || 'light'
  }

  private get themes () {
    return ['light', 'dark', 'auto'].map(t => ({
      label: this.$t(`theme.${t}`),
      value: t
    }))
  }

  /**
   * 主题切换事件处理程序
   */
  private colorThemeChangeHandler () {
    if (this.theme !== 'auto') return
    this.themeChangeHandler('auto')
  }

  /**
   * 切换主题
   * @param theme selected theme
   */
  private themeChangeHandler (theme: Theme) {
    // if (theme === this.theme) return
    this.$store.state.stores.themeStore.set(theme)
    this.theme = theme
    if (theme === 'auto') theme = this.darkModeMediaQuery.matches ? 'dark' : 'light'
    setTheme(theme)
  }

  private mounted () {
    // 这里的兼容性判断不能使用 `MediaQueryList.prototype.addEventListener` 判断, 因为 Safari 没有 MediaQueryList 这个变量！
    if (this.darkModeMediaQuery.addEventListener) {
      this.darkModeMediaQuery.addEventListener('change', this.colorThemeChangeHandler)
    } else {
      this.darkModeMediaQuery.addListener(this.colorThemeChangeHandler)
    }
    this.themeChangeHandler(this.theme)
  }

  private destroyed () {
    // 此处this.darkModeMediaQuery.addEventListener会一直为真
    this.darkModeMediaQuery.removeEventListener('change', this.colorThemeChangeHandler)
    // if (this.darkModeMediaQuery.addEventListener) {
    //   this.darkModeMediaQuery.removeEventListener('change', this.colorThemeChangeHandler)
    // } else {
    //   this.darkModeMediaQuery.removeListener(this.colorThemeChangeHandler)
    // }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">

</style>
