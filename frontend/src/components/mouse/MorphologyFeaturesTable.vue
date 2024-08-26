<template>
  <el-tabs :stretch="true">
    <el-tab-pane
      v-for="(item, i) in morphoInfo"
      :key="i"
      :label="item.type"
    >
      <el-table
        :data="item.info"
        stripe
        style="width: 100%"
      >
        <el-table-column
          prop="metric"
          label="metric"
        />
        <el-table-column
          v-if="type === 'multiple'"
          label="value(mean)"
        >
          <template slot-scope="scope">
            {{ scope.row.mean + ' ' + (scope.row.unit || '') }}
          </template>
        </el-table-column>
        <el-table-column
          v-if="type === 'multiple'"
          label="std"
        >
          <template slot-scope="scope">
            {{ scope.row.std + ' ' + (scope.row.unit || '') }}
          </template>
        </el-table-column>
        <el-table-column
          v-if="type === 'single'"
          label="value"
        >
          <template slot-scope="scope">
            {{ scope.row.value + ' ' + (scope.row.unit || '')}}
          </template>
        </el-table-column>
      </el-table>
    </el-tab-pane>
  </el-tabs>
</template>

<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator'

@Component
export default class MorphologyFeaturesTable extends Vue {
  @Prop({ required: true }) morphoInfo!: any
  @Prop({ default: 'multiple' }) type!: string // 统计表格 multiple | 单个神经元表格 single, 表格的字段会不一样
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">

</style>
