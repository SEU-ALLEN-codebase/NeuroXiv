<template>
  <div class="neuron-states-container">
    <NeuronStatesDesc
      :basic-info="neuronStatesData.basic_info"
      :morpho-info="neuronStatesData.morpho_info"
      :proj-info="neuronStatesData.proj_info"
      :neurons-list="neuronsList"
    />
    <div class="separator" />
    <section
      ref="featurePlots"
      class="feature-plots"
    >
      <div class="feature-plot-container">
        <NeuronFeaturePlots
          ref="featurePlot"
          :plot-data="neuronStatesData.plot.proj_plot"
          class="feature-plot abs-full"
        />
      </div>
      <hr class="plot-separator">
      <NeuronFeatureHistogramBars
        ref="histogramBars"
        :histogram-data="neuronStatesData.plot.hist_plot"
      />
    </section>
    <el-button
      icon="el-icon-download"
      class="downloadList-btn"
      size="mini"
      :loading="downloading"
      @click="downloadNeuronList"
    >
      Download Neuron List
    </el-button>
    <el-button
      icon="el-icon-download"
      class="download-btn"
      size="mini"
      :loading="downloading"
      @click="downloadData"
    >
      Download
    </el-button>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Ref, Prop } from 'vue-property-decorator'
import NeuronStatesDesc from '@/components/mouse/NeuronStatesDesc.vue'
import NeuronFeaturePlots from '@/components/mouse/NeuronFeatureScatter.vue'
import NeuronFeatureHistogramBars from '@/components/mouse/NeuronFeatureHistogramBars.vue'
import html2canvas from 'html2canvas'
import JSZip from 'jszip'
import { downloadLink, getBlobFromCanvas, sleep } from '@/utils/util'
// @ts-ignore
// import { data as plotData } from '@/assets/plot'

@Component({
  components: { NeuronFeatureHistogramBars, NeuronFeaturePlots, NeuronStatesDesc }
})
export default class NeuronStates extends Vue {
  @Ref('histogramBars') readonly histogramBars!: NeuronFeatureHistogramBars
  @Ref('featurePlots') readonly featurePlots!: HTMLElement
  @Ref('featurePlot') readonly featurePlot!: NeuronFeaturePlots
  @Ref('NeuronStatesDesc') readonly neuronStatesDesc!: NeuronStatesDesc
  @Prop({ required: true }) readonly neuronsList!: any[]

  public neuronStatesData: any = {
    basic_info: [],
    morpho_info: [],
    proj_info: [],
    plot: {
      proj_plot: [],
      hist_plot: []
    }
  }

  private downloading: boolean = false

  private async downloadNeuronList () {
    this.downloading = true

    try {
      // 移除 neuronsList 中的 img_src 和 selected 字段
      const cleanedNeuronsList = this.neuronsList.map(neuron => {
        // eslint-disable-next-line camelcase
        const { img_src, selected, ...rest } = neuron
        return rest
      })

      // 准备 JSON 数据
      const neuronStatesData = {
        neuronsList: cleanedNeuronsList
      }

      // 创建 Blob 并生成 URL
      const jsonBlob = new Blob([JSON.stringify(neuronStatesData)], { type: 'application/json' })
      const url = URL.createObjectURL(jsonBlob)

      // 下载 JSON 文件
      await downloadLink(url, 'neuronStatesData.json')
      URL.revokeObjectURL(url)
    } catch (e) {
      console.warn(e)
    }
    this.downloading = false
  }
  /**
   * 下载 neuron info json, 散点图, 柱状图
   * @private
   */
  private async downloadData () {
    this.downloading = true
    const zip = new JSZip()
    const folder = zip.folder('neuron_stats')
    const swcFolder = zip.folder('swc_files') // 创建swc文件夹

    try {
      // 左侧的信息 json

      // arbor distribution scatter
      const canvas = await html2canvas(this.featurePlot.$el as HTMLElement)
      // @ts-ignore
      folder.file('arbor_distribution.png', await getBlobFromCanvas(canvas))

      // 柱状图
      for (let i = 0; i < this.neuronStatesData.plot.hist_plot.length; i++) {
        let plotItem = this.neuronStatesData.plot.hist_plot[i]
        let plotItemCanvas = this.histogramBars.histogramItem[i].querySelector('canvas')
        // @ts-ignore
        folder.file(`${plotItem.metric}.png`, await getBlobFromCanvas(plotItemCanvas))
      }

      // 下载swc文件
      const swcPromises = this.neuronsList.map(async neuron => {
        try {
          // 解析 img_src，生成 .swc 文件路径
          let imgSrc = neuron.img_src.replace(/\\/g, '/')
          let directoryPath = imgSrc.substring(0, imgSrc.lastIndexOf('/'))
          let directoryName = directoryPath.split('/').pop()
          let swcSrc = `${directoryPath}/${directoryName}.swc`

          let response = await fetch(swcSrc)
          if (response.ok) {
            let swcBlob = await response.blob()
            // @ts-ignore
            swcFolder.file(`${directoryName}.swc`, swcBlob)
          } else {
            console.warn(`Failed to fetch SWC file for neuron: ${swcSrc}`)
          }
        } catch (error) {
          console.warn(`Error fetching SWC file for neuron: ${neuron.img_src}`, error)
        }
      })

      // 等待所有异步操作完成
      await Promise.all([...swcPromises])

      // 移除 neuronsList 中的 img_src 和 selected 字段
      const cleanedNeuronsList = this.neuronsList.map(neuron => {
        // eslint-disable-next-line camelcase
        const { img_src, selected, ...rest } = neuron
        return rest
      })

      // 左侧的信息 json
      // @ts-ignore
      folder.file('neuronStatesData.json', JSON.stringify({
        neuronsList: cleanedNeuronsList,
        basic_info: this.neuronStatesData.basic_info,
        morpho_info: this.neuronStatesData.morpho_info,
        proj_info: this.neuronStatesData.proj_info
      }))

      const zipBlob = await zip.generateAsync({ type: 'blob' })
      const url = URL.createObjectURL(zipBlob)
      await downloadLink(url, 'neuron_stats.zip')
      URL.revokeObjectURL(url)
    } catch (e) {
      console.warn(e)
    }
    this.downloading = false
  }
  // private async downloadData () {
  //   this.downloading = true
  //   await sleep(100) // 先让 loading 动起来
  //   const zip = new JSZip()
  //   const folder = zip.folder('neuron_stats')
  //   const swcFolder = zip.folder('swc_files')
  //   try {
  //     // 左侧的信息 json
  //     // @ts-ignore
  //     folder.file('neuronStatesData.json', JSON.stringify({
  //       neuronsList: this.neuronsList,
  //       basic_info: this.neuronStatesData.basic_info,
  //       morpho_info: this.neuronStatesData.morpho_info,
  //       proj_info: this.neuronStatesData.proj_info
  //     }))
  //     // arbor distribution scatter
  //     const canvas = await html2canvas(this.featurePlot.$el as HTMLElement)
  //     // @ts-ignore
  //     folder.file('arbor_distribution.png', await getBlobFromCanvas(canvas))
  //     // 柱状图
  //     for (let i = 0; i < this.neuronStatesData.plot.hist_plot.length; i++) {
  //       let plotItem = this.neuronStatesData.plot.hist_plot[i]
  //       let plotItemCanvas = this.histogramBars.histogramItem[i].querySelector('canvas')
  //       // @ts-ignore
  //       folder.file(`${plotItem.metric}.png`, await getBlobFromCanvas(plotItemCanvas))
  //     }
  //     const swcPromises = this.neuronsList.map(async neuron => {
  //       try {
  //         // 解析 img_src，生成 .swc 文件路径
  //         let imgSrc = neuron.img_src.replace(/\\/g, '/')
  //         let directoryPath = imgSrc.substring(0, imgSrc.lastIndexOf('/'))
  //         let directoryName = directoryPath.split('/').pop()
  //         let swcSrc = `${directoryPath}/${directoryName}.swc`
  //
  //         let response = await fetch(swcSrc)
  //         if (response.ok) {
  //           let swcBlob = await response.blob()
  //           // @ts-ignore
  //           swcFolder.file(`${directoryName}.swc`, swcBlob)
  //         } else {
  //           console.warn(`Failed to fetch SWC file for neuron: ${swcSrc}`)
  //         }
  //       } catch (error) {
  //         console.warn(`Error fetching SWC file for neuron: ${neuron.img_src}`, error)
  //       }
  //     })
  //
  //     // 等待所有异步操作完成
  //     await Promise.all([...swcPromises])
  //     const zipBlob = await zip.generateAsync({ type: 'blob' })
  //     const url = URL.createObjectURL(zipBlob)
  //     await downloadLink(url, 'neuron_stats.zip')
  //     URL.revokeObjectURL(url)
  //   } catch (e) {
  //     console.warn(e)
  //   }
  //   this.downloading = false
  // }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.neuron-states-container {
  color: black;
  display: flex;
  flex-flow: row nowrap;
  border-radius: 5px;
  height: 100%;
  position: relative;
  .feature-desc, .feature-plots {
    height: 100%;
    overflow: auto;
    padding: 10px;
  }
  .feature-desc {
    width: 360px;
    flex: 0 0 auto;
  }
  .separator {
    width: 1px;
    height: 100%;
    background-color: grey;
  }
  .feature-plots {
    flex: 1 1 auto;
    overflow: auto;
    > * {
      min-width: 950px;
    }
    .feature-plot-container {
      position: relative;
      &:before {
        content: '';
        display: block;
        padding-top: 62%;
      }
      .feature-plot {
        width: 100%;
        height: 100%;
      }
    }
  }
  .plot-separator {
    border: 1px dashed grey;
    margin: 2em 0;
  }
  .download-btn {
    position: absolute;
    top: 0;
    right: 20px;
  }
  .downloadList-btn {
    position: absolute;
    top: 0;
    right:130px;
  }
}
</style>
