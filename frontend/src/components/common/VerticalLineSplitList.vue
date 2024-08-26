<template>
  <div class="items-container">
    <template v-for="(item, i) in data">
      <span class="data-item" :class="{ active: item.value === value }" :key="item.value" @click="itemChangeHandler(item)">{{ item.label }}</span>
      <span class="item-separator" v-if="i < data.length - 1">|</span>
    </template>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator'

type LabelValueItem = {
  label: string
  value: number | string
}

@Component
export default class VerticalLineSplitList extends Vue {
  @Prop({ default: '' }) value!: string
  @Prop({ required: true }) data!: LabelValueItem[]

  /**
   * 切换选项
   * @param item selected item
   */
  private itemChangeHandler (item: LabelValueItem) {
    if (item.value === this.value) return
    this.$emit('input', item.value)
    this.$emit('item-change', item)
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.items-container {
  color: white;
  .data-item {
    &.active {
      font-weight: bold;
    }
    &:not(.active) {
      cursor: pointer;
    }
  }
  .item-separator {
    margin: 0 5px;
  }
}
</style>
