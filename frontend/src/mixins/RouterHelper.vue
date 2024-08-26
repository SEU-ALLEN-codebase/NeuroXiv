<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { Location, RawLocation } from 'vue-router'

@Component
export default class RouterHelper extends Vue {
  /**
   * 根据路由对象补全路由参数, 例如添加语言参数
   */
  protected getCompleteRouteByPathObject ({ name, params, query }: Location): Location {
    return {
      name,
      params: { ...(params || {}), lang: this.$route.params.lang },
      query
    }
  }

  /**
   * 根据路由字符串补全路由参数, 例如添加语言参数
   * @param path 路由路径字符串
   */
  protected getCompleteRouteByPathString (path: RawLocation): RawLocation {
    return `/${this.$route.params.lang}/${path}`
  }
}
</script>
