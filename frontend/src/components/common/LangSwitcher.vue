<template>
  <VerticalLineSplitList :data="availableLanguages" v-model="lang" @item-change="langChangeHandler($event.value)" />
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator'
import { AVAILABLE_LOCALES } from "@/i18n/common"
import VerticalLineSplitList from "@/components/common/VerticalLineSplitList.vue"

@Component({
  components: {
    VerticalLineSplitList
  }
})
export default class LangSwitcher extends Vue {
  protected lang: string = ''
  protected get availableLanguages () {
    return AVAILABLE_LOCALES.map(l => ({
      label: this.$t(l),
      value: l
    }))
  }

  /**
   * 切换语言
   * @param lang { string } selected language
   */
  protected langChangeHandler (lang: string) {
    // 切换语言的时候, 需要保证除了语言变化之后, 其他所有路径都保持不变
    // 但是如果路由设置有别名的时候, 以下的方式会有问题, 例如原来 URL 上使用路由别名的, 下面的方式会把别名换掉
    // 所以还是要改为正则替换的方式
    // this.$router.push({
    //   name: this.$route.name,
    //   params: { ...this.$route.params, lang },
    //   query: this.$route.query
    // })
    // if (lang === this.lang) return
    const currentLang = this.$route.params.lang
    // 如果有 redirect 参数也要替换
    const newLangRoute = this.$route.fullPath.replace(`/${currentLang}`, `/${lang}`).replace(`%2F${currentLang}`, `%2F${lang}`)
    this.$router.push(newLangRoute)
    this.$store.state.stores.langSettingStore.set(lang)
    this.$store.commit('updateLang', lang)
    this.lang = lang
    this.$emit('switch', new CustomEvent('switch', {
      detail: lang
    }))
  }

  @Watch('$route.params.lang', { immediate: true })
  onLangChanged(val: string) {
    if (!val) return
    this.lang = val
    this.$store.commit('updateLang', val)
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">

</style>
