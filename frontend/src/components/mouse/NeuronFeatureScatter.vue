<template>
  <div
    ref="neuronPlotContainer"
    class="neuron-plot-container"
  >
    <div
      ref="neuronScatterPlot"
      class="neuron-scatter-plot"
    />
    <div class="legends">
      <div class="legend-item legend-arbor-length">
        <span>Arbor length: </span>
        <ul class="length-list">
          <li
            v-for="(item, i) in lengthMap"
            :key="i"
            class="list-item length-item"
          >
            <span
              class="sub-item length-size"
              :style="{ width: `${item.size}px`, height: `${item.size}px` }"
            />
            <span class="sub-item length-label">{{ item.len }}</span>
          </li>
        </ul>
      </div>
      <div class="legend-item legend-distal-arbor-ratio">
        <span>Distal arbor ratio: </span>
        <ul class="ratio-list">
          <li
            v-for="(item, i) in colorMap"
            :key="i"
            class="list-item ratio-item"
          >
            <span
              class="sub-item ratio-color"
              :style="{ backgroundColor: `rgb(${item.color})` }"
            />
            <span class="sub-item ratio-label">{{ item.distalArborRatio }}</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Ref, Prop } from 'vue-property-decorator'
import { findColorBetween } from '@/utils/util'
import * as echarts from 'echarts'

// const yTicks = [ 'ACAd', 'AId', 'CLA', 'MOp', 'MOs', 'ORBl', 'RSPv', 'SSp-bfd', 'SSp-ll', 'SSp-m', 'SSp-n', 'SSp-ul', 'SSp-un', 'SSs', 'VISl', 'VISp', 'CL', 'LD', 'LGd', 'LP', 'MD', 'MG', 'PO', 'RT', 'SMT', 'VAL', 'VM', 'VPL', 'VPLpc', 'VPM', 'CP', 'OT', 'CA1', 'DG', 'POST', 'PRE', 'ProS', 'SUB', 'LHA', 'ZI' ] // 40
// const xTicks = [ 'ACAd', 'AId', 'AUDd', 'AUDp', 'AUDv', 'CLA', 'MOp', 'MOs', 'ORBl', 'ORBvl', 'RSPagl', 'RSPd', 'RSPv', 'SSp-bfd', 'SSp-ll', 'SSp-m', 'SSp-n', 'SSp-tr', 'SSp-ul', 'SSp-un', 'SSs', 'VISC', 'VISa', 'VISal', 'VISl', 'VISp', 'VISpm', 'VISrl', 'AV', 'CL', 'LD', 'LGd', 'LP', 'MD', 'MG', 'PO', 'RT', 'SMT', 'VAL', 'VM', 'VPL', 'VPLpc', 'VPM', 'AAA', 'ACB', 'CP', 'GPe', 'LSr', 'OT', 'SI', 'CA1', 'CA3', 'DG', 'ENTl', 'ENTm', 'POST', 'PRE', 'ProS', 'SUB', 'LHA', 'MM', 'ZI', 'MRN', 'PAG', 'SNr' ] // 65

const yTicks = ['ACAd', 'ACAv', 'AId', 'AIv', 'FRP', 'ILA', 'MOp', 'MOs', 'ORBl', 'ORBm', 'ORBvl', 'PL', 'RSPv', 'SSp-bfd', 'SSp-ll', 'SSp-m', 'SSp-n', 'SSp-ul', 'SSs', 'VISl', 'VISp', 'CA1', 'CA2', 'CA3', 'DG', 'HATA', 'PAR', 'POST', 'PRE', 'ProS', 'SUB', 'CLA', 'CP', 'OT', 'LD', 'LGd', 'LP', 'MD', 'MG', 'PO', 'RT', 'VAL', 'VM', 'VPL', 'VPLpc', 'VPM', 'LHA', 'ZI'] // 40
const xTicks = ['L1', 'L2/3', 'L4', 'L5', 'L6a', 'L6b', 'ACAd', 'ACAv', 'AId', 'AIv', 'AUDp', 'FRP', 'MOp', 'MOs', 'ORBl', 'ORBm', 'ORBvl', 'PL', 'RSPagl', 'RSPd', 'RSPv', 'SSp-bfd', 'SSp-ll', 'SSp-m', 'SSp-n', 'SSp-ul', 'SSs', 'VISC', 'VISa', 'VISam', 'VISp', 'VISrl', 'CA1', 'CA3', 'DG', 'ENTl', 'ENTm', 'PAR', 'ProS', 'SUB', 'AON', 'COAp', 'PIR', 'TR', 'BLA', 'ACB', 'CP', 'LSr', 'OT', 'SI', 'AM', 'MD', 'VM', 'VPM', 'AHN', 'LHA', 'MM', 'CS', 'PCG', 'PG', 'PRNr', 'MDRN', 'PARN', 'MRN', 'PAG', 'SCm', 'fiber tracts'] // 65
@Component
export default class NeuronFeatureScatter extends Vue {
  @Ref('neuronScatterPlot') neuronScatterPlot!: HTMLDivElement
  @Prop({ required: true }) plotData!: any

  /**
   * 渲染图表
   */
  public renderChart () {
    const scatter = echarts.getInstanceByDom(this.neuronScatterPlot) || echarts.init(this.neuronScatterPlot)
    scatter.setOption(this.getOptions(this.plotData))
  }

  private colorMap: any[] = [
    { distalArborRatio: 0, color: [62, 79, 185] },
    { distalArborRatio: 0.25, color: [147, 176, 248] },
    { distalArborRatio: 0.5, color: [221, 220, 220] },
    { distalArborRatio: 0.75, color: [231, 156, 128] },
    { distalArborRatio: 1, color: [165, 34, 44] }
  ]

  private lengthMap: any[] = [
    { len: 7500, size: 7 },
    { len: 15000, size: 11 },
    { len: 22500, size: 16 },
    { len: 30000, size: 20 }
  ]

  /**
   * 根据神经元 distalArborRatio 获取相应的颜色插值
   * @param distalArborRatio distal arbor ratio
   * @param colorMap distal arbor ratio color stop
   */
  private static getLinearColor (distalArborRatio: number, colorMap: any[]) {
    for (let i = 0; i < colorMap.length - 1; i++) {
      let curRatio = colorMap[i].distalArborRatio
      let nextRatio = colorMap[i + 1].distalArborRatio
      if (distalArborRatio >= curRatio && distalArborRatio <= nextRatio) {
        let percent = (distalArborRatio - curRatio) / (nextRatio - curRatio)
        let curColor = colorMap[i].color
        let nextColor = colorMap[i + 1].color
        return findColorBetween(curColor, nextColor, percent)
      }
    }
  }

  /**
   * 获取图表选项
   * @param plotData
   * @private
   */
  private getOptions (plotData: any) {
    return {
      dataset: [
        {
          dimensions: ['brain_region_id', 'celltype_id', 'arbor_length', 'distal_arbor_ratio', 'neuronCount'],
          source: plotData
        }
      ],
      title: {
        text: 'Arbor Distribution',
        left: 'center'
        // text: 'Arbor Distribution',
        // left: 'center'
      },
      tooltip: {
        trigger: 'item',
        axisPointer: {
          type: 'cross'
        },
        formatter: (params: any) => {
          const dimensions = params.dimensionNames
          const data = params.data
          // console.log(params, data)
          const content = dimensions.map((d: string) => {
            if (d === 'brain_region_id') return `${d}: ${xTicks[data[d]]}`
            if (d === 'celltype_id') return `${d}: ${yTicks[data[d]]}`
            if (d === 'neuronCount') return `number of neurons: ${data.neuron_count || 0} of ${data.celltype_count || 0}`
            return `${d}: ${data[d].toFixed(2)}`
          })
          return content.join('<br />')
        }
      },
      xAxis: {
        type: 'value',
        splitNumber: xTicks.length,
        min: 0, // 确保第一个标签显示
        max: xTicks.length - 1, // 确保最后一个标签显示
        axisLabel: {
          rotate: 90,
          formatter: function (value: number) {
            return xTicks[value]
          }
        }
      },
      yAxis: {
        type: 'value',
        splitNumber: yTicks.length,
        min: -0.1, // 确保第一个标签显示
        max: yTicks.length - 0.9, // 确保最后一个标签显示
        axisLabel: {
          interval: 0,
          formatter: function (value: number) {
            return yTicks[value]
          }
        }
      },
      grid: {
        left: '1%', // 增加左边距，确保y轴标签显示
        right: '1%', // 增加右边距
        bottom: 20, // 增加底部间距，确保x轴标签显示
        top: 50, // 增加顶部间距，确保标题显示
        containLabel: true
      },
      visualMap: [{
        show: false,
        dimension: 2, // 从 0 开始
        min: 0,
        max: this.lengthMap[this.lengthMap.length - 1].len,
        range: [100, this.lengthMap[this.lengthMap.length - 1].len], // 过滤 100 以下的显示
        seriesIndex: [0],
        inRange: {
          symbolSize: [3, this.lengthMap[this.lengthMap.length - 1].size]
        }
      }],
      series: [
        {
          type: 'scatter',
          // encode: {
          //   tooltip: [0, 1, 2, 3]
          // },
          itemStyle: {
            color: (params: any) => {
              let color = NeuronFeatureScatter.getLinearColor(params.data.distal_arbor_ratio, this.colorMap)
              return `rgb(${color})`
            }
          }
        }
      ]
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
.neuron-plot-container {
  width: 100%;
  height: 80vh;
  display: flex;
  flex-flow: column nowrap;
  .neuron-scatter-plot {
    width: 100%;
    flex: 1;
  }
  .legends {
    text-align: center;
    .legend-item {
      display: inline-block;
      + .legend-item {
        margin-left: 30px;
      }
    }
    .length-list, .ratio-list {
      display: inline-block;
      margin-left: 10px;
    }
    .list-item {
      display: inline-block;
      margin-right: 15px;
      .sub-item {
        display: inline-block;
        vertical-align: middle;
      }
      .length-size, .ratio-color {
        border-radius: 50%;
        margin-right: 3px;
      }
    }
    .legend-arbor-length {
      .length-list {
        .length-item {
          .length-size {
            background-color: black;
          }
        }
      }
    }
    .legend-distal-arbor-ratio {
      .ratio-list {
        .ratio-item {
          .ratio-color {
            width: 15px;
            height: 15px;
          }
        }
      }
    }
  }
}
</style>

<!--<template>-->
<!--  <div-->
<!--    ref="neuronPlotContainer"-->
<!--    class="neuron-plot-container"-->
<!--  >-->
<!--    <div-->
<!--      ref="neuronScatterPlot"-->
<!--      class="neuron-scatter-plot"-->
<!--    />-->
<!--    <div class="legends">-->
<!--      <div class="legend-item legend-arbor-length">-->
<!--        <span>Arbor length: </span>-->
<!--        <ul class="length-list">-->
<!--          <li-->
<!--            v-for="(item, i) in lengthMap"-->
<!--            :key="i"-->
<!--            class="list-item length-item"-->
<!--          >-->
<!--            <span-->
<!--              class="sub-item length-size"-->
<!--              :style="{ width: `${item.size}px`, height: `${item.size}px` }"-->
<!--            />-->
<!--            <span class="sub-item length-label">{{ item.len }}</span>-->
<!--          </li>-->
<!--        </ul>-->
<!--      </div>-->
<!--      <div class="legend-item legend-distal-arbor-ratio">-->
<!--        <span>Distal arbor ratio: </span>-->
<!--        <ul class="ratio-list">-->
<!--          <li-->
<!--            v-for="(item, i) in colorMap"-->
<!--            :key="i"-->
<!--            class="list-item ratio-item"-->
<!--          >-->
<!--            <span-->
<!--              class="sub-item ratio-color"-->
<!--              :style="{ backgroundColor: `rgb(${item.color})` }"-->
<!--            />-->
<!--            <span class="sub-item ratio-label">{{ item.distalArborRatio }}</span>-->
<!--          </li>-->
<!--        </ul>-->
<!--      </div>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<script lang="ts">-->
<!--import { Component, Vue, Ref, Prop } from 'vue-property-decorator'-->
<!--import { findColorBetween } from '@/utils/util'-->
<!--import * as echarts from 'echarts'-->

<!--// const yTicks = [ 'ACAd', 'AId', 'CLA', 'MOp', 'MOs', 'ORBl', 'RSPv', 'SSp-bfd', 'SSp-ll', 'SSp-m', 'SSp-n', 'SSp-ul', 'SSp-un', 'SSs', 'VISl', 'VISp', 'CL', 'LD', 'LGd', 'LP', 'MD', 'MG', 'PO', 'RT', 'SMT', 'VAL', 'VM', 'VPL', 'VPLpc', 'VPM', 'CP', 'OT', 'CA1', 'DG', 'POST', 'PRE', 'ProS', 'SUB', 'LHA', 'ZI' ] // 40-->
<!--// const xTicks = [ 'ACAd', 'AId', 'AUDd', 'AUDp', 'AUDv', 'CLA', 'MOp', 'MOs', 'ORBl', 'ORBvl', 'RSPagl', 'RSPd', 'RSPv', 'SSp-bfd', 'SSp-ll', 'SSp-m', 'SSp-n', 'SSp-tr', 'SSp-ul', 'SSp-un', 'SSs', 'VISC', 'VISa', 'VISal', 'VISl', 'VISp', 'VISpm', 'VISrl', 'AV', 'CL', 'LD', 'LGd', 'LP', 'MD', 'MG', 'PO', 'RT', 'SMT', 'VAL', 'VM', 'VPL', 'VPLpc', 'VPM', 'AAA', 'ACB', 'CP', 'GPe', 'LSr', 'OT', 'SI', 'CA1', 'CA3', 'DG', 'ENTl', 'ENTm', 'POST', 'PRE', 'ProS', 'SUB', 'LHA', 'MM', 'ZI', 'MRN', 'PAG', 'SNr' ] // 65-->

<!--const yTicks = ['ACAd', 'ACAv', 'AId', 'AIv', 'FRP', 'ILA', 'MOp', 'MOs', 'ORBl', 'ORBm', 'ORBvl', 'PL', 'RSPv', 'SSp-bfd', 'SSp-ll', 'SSp-m', 'SSp-n', 'SSp-ul', 'SSs', 'VISl', 'VISp', 'CA1', 'CA2', 'CA3', 'DG', 'HATA', 'PAR', 'POST', 'PRE', 'ProS', 'SUB', 'CLA', 'CP', 'OT', 'LD', 'LGd', 'LP', 'MD', 'MG', 'PO', 'RT', 'VAL', 'VM', 'VPL', 'VPLpc', 'VPM', 'LHA', 'ZI'] // 40-->
<!--const xTicks = ['L1', 'L2/3', 'L4', 'L5', 'L6a', 'L6b', 'ACAd', 'ACAv', 'AId', 'AIv', 'AUDp', 'FRP', 'MOp', 'MOs', 'ORBl', 'ORBm', 'ORBvl', 'PL', 'RSPagl', 'RSPd', 'RSPv', 'SSp-bfd', 'SSp-ll', 'SSp-m', 'SSp-n', 'SSp-ul', 'SSs', 'VISC', 'VISa', 'VISam', 'VISp', 'VISrl', 'CA1', 'CA3', 'DG', 'ENTl', 'ENTm', 'PAR', 'ProS', 'SUB', 'AON', 'COAp', 'PIR', 'TR', 'BLA', 'ACB', 'CP', 'LSr', 'OT', 'SI', 'AM', 'MD', 'VM', 'VPM', 'AHN', 'LHA', 'MM', 'CS', 'PCG', 'PG', 'PRNr', 'MDRN', 'PARN', 'MRN', 'PAG', 'SCm', 'fiber tracts'] // 65-->
<!--@Component-->
<!--export default class NeuronFeatureScatter extends Vue {-->
<!--  @Ref('neuronScatterPlot') neuronScatterPlot!: HTMLDivElement-->
<!--  @Prop({ required: true }) plotData!: any-->

<!--  /**-->
<!--   * 渲染图表-->
<!--   */-->
<!--  public renderChart () {-->
<!--    const scatter = echarts.getInstanceByDom(this.neuronScatterPlot) || echarts.init(this.neuronScatterPlot)-->
<!--    scatter.setOption(this.getOptions(this.plotData))-->
<!--  }-->

<!--  private colorMap: any[] = [-->
<!--    { distalArborRatio: 0, color: [62, 79, 185] },-->
<!--    { distalArborRatio: 0.25, color: [147, 176, 248] },-->
<!--    { distalArborRatio: 0.5, color: [221, 220, 220] },-->
<!--    { distalArborRatio: 0.75, color: [231, 156, 128] },-->
<!--    { distalArborRatio: 1, color: [165, 34, 44] }-->
<!--  ]-->

<!--  private lengthMap: any[] = [-->
<!--    { len: 7500, size: 7 },-->
<!--    { len: 15000, size: 11 },-->
<!--    { len: 22500, size: 16 },-->
<!--    { len: 30000, size: 20 }-->
<!--  ]-->

<!--  /**-->
<!--   * 根据神经元 distalArborRatio 获取相应的颜色插值-->
<!--   * @param distalArborRatio distal arbor ratio-->
<!--   * @param colorMap distal arbor ratio color stop-->
<!--   */-->
<!--  private static getLinearColor (distalArborRatio: number, colorMap: any[]) {-->
<!--    for (let i = 0; i < colorMap.length - 1; i++) {-->
<!--      let curRatio = colorMap[i].distalArborRatio-->
<!--      let nextRatio = colorMap[i + 1].distalArborRatio-->
<!--      if (distalArborRatio >= curRatio && distalArborRatio <= nextRatio) {-->
<!--        let percent = (distalArborRatio - curRatio) / (nextRatio - curRatio)-->
<!--        let curColor = colorMap[i].color-->
<!--        let nextColor = colorMap[i + 1].color-->
<!--        return findColorBetween(curColor, nextColor, percent)-->
<!--      }-->
<!--    }-->
<!--  }-->

<!--  /**-->
<!--   * 获取图表选项-->
<!--   * @param plotData-->
<!--   * @private-->
<!--   */-->
<!--  private getOptions (plotData: any) {-->
<!--    return {-->
<!--      dataset: [-->
<!--        {-->
<!--          dimensions: ['brain_region_id', 'celltype_id', 'arbor_length', 'distal_arbor_ratio', 'neuronCount'],-->
<!--          source: plotData-->
<!--        }-->
<!--      ],-->
<!--      title: {-->
<!--        text: 'Arbor Distribution',-->
<!--        left: 'center'-->
<!--        // text: 'Arbor Distribution',-->
<!--        // left: 'center'-->
<!--      },-->
<!--      tooltip: {-->
<!--        trigger: 'item',-->
<!--        axisPointer: {-->
<!--          type: 'cross'-->
<!--        },-->
<!--        formatter: (params: any) => {-->
<!--          const dimensions = params.dimensionNames-->
<!--          const data = params.data-->
<!--          // console.log(params, data)-->
<!--          const content = dimensions.map((d: string) => {-->
<!--            if (d === 'brain_region_id') return `${d}: ${xTicks[data[d]]}`-->
<!--            if (d === 'celltype_id') return `${d}: ${yTicks[data[d]]}`-->
<!--            if (d === 'neuronCount') return `number of neurons: ${data.neuron_count || 0} of ${data.celltype_count || 0}`-->
<!--            return `${d}: ${data[d].toFixed(2)}`-->
<!--          })-->
<!--          return content.join('<br />')-->
<!--        }-->
<!--      },-->
<!--      xAxis: {-->
<!--        type: 'value',-->
<!--        splitNumber: xTicks.length, // tick 的数量为 length, 格子的数量为 length - 1-->
<!--        min: 0,-->
<!--        max: xTicks.length - 1,-->
<!--        axisLabel: {-->
<!--          rotate: 90,-->
<!--          formatter: function (value: number) {-->
<!--            return xTicks[value]-->
<!--          }-->
<!--        }-->
<!--      },-->
<!--      yAxis: {-->
<!--        type: 'value',-->
<!--        splitNumber: yTicks.length,-->
<!--        min: 0,-->
<!--        max: yTicks.length - 1,-->
<!--        axisLabel: {-->
<!--          interval: 0,-->
<!--          formatter: function (value: number) {-->
<!--            return yTicks[value]-->
<!--          }-->
<!--        }-->
<!--      },-->
<!--      grid: {-->
<!--        left: '10px',-->
<!--        right: 20,-->
<!--        bottom: 20,-->
<!--        containLabel: true-->
<!--      },-->
<!--      visualMap: [{-->
<!--        show: false,-->
<!--        dimension: 2, // 从 0 开始-->
<!--        min: 0,-->
<!--        max: this.lengthMap[this.lengthMap.length - 1].len,-->
<!--        range: [100, this.lengthMap[this.lengthMap.length - 1].len], // 过滤 100 以下的显示-->
<!--        seriesIndex: [0],-->
<!--        inRange: {-->
<!--          symbolSize: [3, this.lengthMap[this.lengthMap.length - 1].size]-->
<!--        }-->
<!--      }],-->
<!--      series: [-->
<!--        {-->
<!--          type: 'scatter',-->
<!--          // encode: {-->
<!--          //   tooltip: [0, 1, 2, 3]-->
<!--          // },-->
<!--          itemStyle: {-->
<!--            color: (params: any) => {-->
<!--              let color = NeuronFeatureScatter.getLinearColor(params.data.distal_arbor_ratio, this.colorMap)-->
<!--              return `rgb(${color})`-->
<!--            }-->
<!--          }-->
<!--        }-->
<!--      ]-->
<!--    }-->
<!--  }-->

<!--  async mounted () {-->
<!--    await this.$nextTick()-->
<!--    // this.renderChart()-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--&lt;!&ndash; Add "scoped" attribute to limit CSS to this component only &ndash;&gt;-->
<!--<style scoped lang="less">-->
<!--.neuron-plot-container {-->
<!--  width: 600px;-->
<!--  height: 600px;-->
<!--  display: flex;-->
<!--  flex-flow: column nowrap;-->
<!--  .neuron-scatter-plot {-->
<!--    height: 0;-->
<!--    flex: 1 1 auto;-->
<!--  }-->
<!--  .legends {-->
<!--    text-align: center;-->
<!--    .legend-item {-->
<!--      display: inline-block;-->
<!--      + .legend-item {-->
<!--        margin-left: 30px;-->
<!--      }-->
<!--    }-->
<!--    .length-list, .ratio-list {-->
<!--      display: inline-block;-->
<!--      margin-left: 10px;-->
<!--    }-->
<!--    .list-item {-->
<!--      display: inline-block;-->
<!--      margin-right: 15px;-->
<!--      .sub-item {-->
<!--        display: inline-block;-->
<!--        vertical-align: middle;-->
<!--      }-->
<!--      .length-size, .ratio-color {-->
<!--        border-radius: 50%;-->
<!--        margin-right: 3px;-->
<!--      }-->
<!--    }-->
<!--    .legend-arbor-length {-->
<!--      .length-list {-->
<!--        .length-item {-->
<!--          .length-size {-->
<!--            background-color: black;-->
<!--          }-->
<!--        }-->
<!--      }-->
<!--    }-->
<!--    .legend-distal-arbor-ratio {-->
<!--      .ratio-list {-->
<!--        .ratio-item {-->
<!--          .ratio-color {-->
<!--            width: 15px;-->
<!--            height: 15px;-->
<!--          }-->
<!--        }-->
<!--      }-->
<!--    }-->
<!--  }-->
<!--}-->
<!--</style>-->
