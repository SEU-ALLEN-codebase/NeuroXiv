<template>
  <div class="neuron-histogram-container">
    <div
      v-for="(item, i) in histogramData"
      ref="histogramItem"
      :key="i"
      class="histogram-item"
    />
  </div>
</template>

<script lang="ts">
import { Component, Vue, Ref, Prop } from 'vue-property-decorator'
import * as echarts from 'echarts'

@Component
export default class NeuronFeatureHistogramBars extends Vue {
  @Ref('histogramItem') histogramItem!: HTMLDivElement[]
  @Prop({ required: true }) histogramData!: any[]

  /**
   * 渲染图表
   */
  public renderChart () {
    this.histogramData.forEach((item: any, i: number) => {
      const chart = echarts.getInstanceByDom(this.histogramItem[i]) || echarts.init(this.histogramItem[i])
      chart.setOption(NeuronFeatureHistogramBars.getOptions(item))
    })
  }

  /**
   * 获取图表选项
   * @param histogramDataItem 图表数据
   * @private
   */
  private static getOptions (histogramDataItem: any) {
    return {
      title: {
        text: histogramDataItem.metric,
        left: 'center'
      },
      xAxis: {
        type: 'category',
        data: histogramDataItem.center
      },
      yAxis: {
        type: 'value'
      },
      grid: {
        left: 10,
        right: 10,
        top: 50,
        bottom: 10,
        containLabel: true
      },
      series: [{
        data: histogramDataItem.height,
        type: 'bar'
      }]
    }
  }

  async mounted () {
    await this.$nextTick()
    // this.renderChart()
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.neuron-histogram-container {
  display: flex;
  flex-flow: row wrap;
  justify-content: space-between;
  margin: 20px;
  .histogram-item {
    width: 450px;
    height: 300px;
    margin-bottom: 30px;
  }
}
</style>
