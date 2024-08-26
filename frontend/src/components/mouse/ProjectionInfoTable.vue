<template>
  <el-tabs :stretch="true">
    <el-tab-pane
      v-for="(item, i) in projInfo"
      :key="i"
      :label="item.type"
    >
      <el-table
        :data="item.info"
        stripe
        style="width: 100%"
      >
        <el-table-column
          prop="region"
          label="region"
        />
        <el-table-column
          prop="relative"
          label="relative"
        />
        <el-table-column
          prop="abs"
          label="absolute"
        />
      </el-table>
    </el-tab-pane>
  </el-tabs>
</template>

<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator'

@Component
export default class ProjectionInfoTable extends Vue {
  @Prop({ required: true }) projInfo!: any
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">

</style>
