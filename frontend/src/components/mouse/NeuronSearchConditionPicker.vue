<template>
  <el-dialog
    :title="`Select ${conditionName}`"
    :visible.sync="show"
    width="fit-content"
    :append-to-body="true"
    @close="$emit('close')"
    :close-on-click-modal = "false"
  >
    <el-transfer
      v-model="value"
      filterable
      filter-placeholder = "Enter search content"
      :data="data"
      :titles="['Candidates', 'Selected']"
    />
    <span
      slot="footer"
      class="dialog-footer"
    >
      <el-button @click="show = false">Cancel</el-button>
      <el-button
        type="primary"
        :disabled="value.length === 0"
        @click="confirmHandler"
      >Confirm</el-button>
    </span>
  </el-dialog>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class NeuronSearchConditionPicker extends Vue {
  public show: boolean = false
  public conditionName: string = '' // 当前的搜索条件, 显示在 dialog title 上面

  private data: any[] = []
  private value: any[] = [] // value 只包含 data 里面的 key

  /**
   * 点击确认按钮
   */
  private confirmHandler () {
    this.$emit('confirm', this.value) // 这个要写在前面, 先接收 confirm 事件
    this.show = false
  }

  /**
   * 设置穿梭框数据
   * @param data 所有可选择的数据
   * @param value 已选中的数据
   */
  public setData (data: any[], value: any[]) {
    this.data = data.map((item: string) => ({ key: item, label: item }))
    this.value = [...value]
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">

</style>
