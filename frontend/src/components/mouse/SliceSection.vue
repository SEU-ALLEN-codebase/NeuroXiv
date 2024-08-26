<template>
  <div class="slice-section">
    <div class="switch-block">
      <el-switch
        v-model="switchValue"
        :active-text="sliceName"
        @change="switchChange"
      />
      <p
        v-show="switchValue"
        class="section-value"
      >
        {{ sliderValue }} μm
      </p>
    </div>
    <el-slider
      v-show="switchValue"
      v-model="sliderValue"
      :max="maxValue"
      :step="valueStep"
      @change="sliderChange"
    />
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator'

@Component<SliceSection>({
  mounted () {}
})

export default class SliceSection extends Vue {
  @Prop({ required: true }) sliceName!: string
  @Prop({ required: true }) maxValue!: number
  @Prop({ required: true }) valueStep!: number
  @Prop({ required: true }) _switchChange!: any
  @Prop({ required: true }) _sliderChange!: any
  private switchValue: boolean = false
  private sliderValue: number = Math.ceil(this.maxValue / 50) * 25

  /**
   * 改变switch的回调函数，用于决定slice是否显示
   * @param isSwitch 是否显示slice
   */
  public switchChange (isSwitch: boolean) {
    // @ts-ignore
    // this.$parent.switchChange(isSwitch, this.sliceName)
    this._switchChange(isSwitch, this.sliceName)
  }

  /**
   * 改变滑动条的回调函数，用于切换slice的位置
   * @param value slice的位置
   */
  public sliderChange (value: number) {
    // @ts-ignore
    // this.$parent.sliderChange(value, this.sliceName)
    this._sliderChange(value, this.sliceName)
  }
}
</script>

<style scoped lang="less">
.slice-section {
  margin-top: 15px;
  .switch-block {
    display: flex;
    justify-content: space-between;
    padding-top: 5px;
    .section-value {
      margin-top: 0;
    }
  }
}
</style>
