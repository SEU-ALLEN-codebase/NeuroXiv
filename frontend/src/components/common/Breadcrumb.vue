<template>
  <el-breadcrumb separator-class="el-icon-arrow-right">
    <el-breadcrumb-item>
      <router-link to="/">{{ $t('nav.home') }}</router-link>
    </el-breadcrumb-item>
    <el-breadcrumb-item v-for="(item, i) in items" :key="i">
      <router-link :to="item.route" v-if="i < items.length - 1">{{ $t(`nav.${item.name}`) }}</router-link>
      <span v-else>{{ $t(`nav.${item.name}`) }}</span>
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
// @ts-ignore
import RouterHelper from "@/mixins/RouterHelper.vue"

// @ts-ignore
@Component
export default class Breadcrumb extends RouterHelper {
  get items () {
    // @ts-ignore
    const pathItems = this.$route.fullPath.split('/').slice(2) // 去掉语言参数
    return pathItems.map((item: string) => ({
      name: item,
      // @ts-ignore
      route: this.getCompleteRouteByPathObject({ name: item })
    }))
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">

</style>
