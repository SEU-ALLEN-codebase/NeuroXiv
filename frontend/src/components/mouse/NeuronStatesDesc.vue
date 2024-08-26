<template>
  <section class="feature-desc">
    <el-collapse
      v-model="activeSection"
    >
      <el-collapse-item
        title="AIPOM data report"
        name="dataSummary"
      >
        <div class="summary-container">
          <p><strong>Overview:</strong></p>
          <ul class="no-bullets">
            <li class="no-bullets">
              {{ basicInfoSummary }}
            </li>
          </ul>
          <p><strong>Morphology Features:</strong></p>
          <ul class="no-bullets">
            <li class="no-bullets">
              {{ morphologySummaries }}
              <!--              v-for="(summary, index) in morphologySummaries"-->
              <!--              :key="index"-->
            </li>
          </ul>
          <p><strong>Projection Patterns:</strong></p>
          <ul class="no-bullets">
            <li class="no-bullets">
              {{ projectionInfoSummary }}
            </li>
          </ul>
        </div>
      </el-collapse-item>
      <el-collapse-item
        title="basic information"
        name="basicInfo"
      >
        <el-table
          :data="basicInfo"
          stripe
          style="width: 100%"
        >
          <el-table-column
            prop="name"
            label=""
          />
          <el-table-column
            prop="num"
            label="number of neurons"
          />
        </el-table>
      </el-collapse-item>
      <el-collapse-item
        title="morphology features"
        name="morphologyFeatures"
      >
        <MorphologyFeaturesTable :morpho-info="morphoInfo" />
      </el-collapse-item>
      <el-collapse-item
        title="anatomy/projection info"
        name="projectionInfo"
      >
        <ProjectionInfoTable :proj-info="projInfo" />
      </el-collapse-item>
    </el-collapse>
  </section>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch, Ref } from 'vue-property-decorator'
import MorphologyFeaturesTable from '@/components/mouse/MorphologyFeaturesTable.vue'
import ProjectionInfoTable from '@/components/mouse/ProjectionInfoTable.vue'

@Component({
  components: {
    MorphologyFeaturesTable,
    ProjectionInfoTable
  }
})
export default class NeuronStatesDesc extends Vue {
  @Prop({ required: true }) basicInfo!: any
  @Prop({ required: true }) morphoInfo!: any
  @Prop({ required: true }) projInfo!: any
  @Prop({ required: true }) readonly neuronsList!: any[]
  private activeSection: string[] = ['basicInfo']

  private messageQueue: any[] = []; // 队列来保存消息
  private isProcessing: boolean = false; // 标志是否正在处理消息
  public hasStartedSSE: boolean = false;
  private eventSource: EventSource | null = null;
  private bs : string = 'The dataset consists of 19,406 neurons obtained from three sources: ION (16,380 neurons), SEU-ALLEN (1,876 neurons), and MouseLight (1,150 neurons). These neurons are distributed across both hemispheres of the brain, with 6,354 in the left and 13,052 in the right. The data spans 327 brain regions, prominently featuring CA1 with 3,691 neurons, DG-sg with 2,630, and SUB with 1,008 neurons. In terms of cortical layer distribution, neurons are mainly found in an unspecified layer (12,026 neurons), L5 (4,179 neurons), L2/3 (1,991 neurons), L6a (817 neurons), L1 (308 neurons), L4 (74 neurons), and L6b (11 neurons). This dataset provides valuable insights into the distribution of neurons across various brain regions and cortical layers.'
  private ms : string = 'The analysis of neuronal morphology data from multiple sources reveals significant insights into the complexity and spatial arrangements of CA1 and DG-sg neurons. CA1 neurons, particularly from the MouseLight source, exhibit extensive axonal networks, with a mean total length surpassing 52,000 μm and an average of over 170 bifurcations, reflecting their intricate connectivity patterns. In contrast, DG-sg neurons display less complexity, with lower mean values for total length and number of bifurcations, though high standard deviations indicate variability within this population. \'Max Path Distance\' highlights the projection range, with CA1 neurons from the ION source showing the highest mean of approximately 8,800 μm. The \'Center Shift\' metric provides insights into the balance of spatial distribution, where CA1 neurons generally exhibit higher values, suggesting broader spatial coverage compared to DG-sg neurons. Overall, the data underscores the importance of \'Total Length\' and \'Number of Bifurcations\' in defining neuronal complexity and reach, while \'Max Path Distance\' and \'Center Shift\' offer additional perspectives on the spatial extension and balance of neuronal structures. These findings collectively enhance our understanding of neuronal morphology and its functional implications.'
  private ps : string = 'The neuronal projection data reveals differential patterns of connectivity for dendrite and axon projections in CA1 and DG-sg neurons across various sources (ION, SEU-ALLEN, MouseLight), emphasizing the structure and connectivity strength within the brain. Dendritic arbor data for CA1 neurons shows high intraregional connectivity, with proportions of arborized lengths in CA1 ranging from 72.1% to 87.7% across different sources. SEU-ALLEN reports the lowest proportion (84.0%) compared to ION (87.7%) and MouseLight (72.1%). DG-sg neurons exhibit similar trends, with over 90% of the dendritic lengths within the DG region (ION: 90.1%, MouseLight: 92.8%). Axonal arbor data for CA1 neurons reveal a broader distribution. ION data indicates significant lengths within CA1 (28.1%), but also other regions like LSr (7.6%) and SUB (5.7%). SEU-ALLEN shows notable projections to DG, CA3, and SUB, with MouseLight highlighting extensive CA1 projections (30.6%) and noteworthy connections to SUB and ProS. For DG-sg neurons, ION data reveals nearly balanced projections to CA3 (44.8%) and DG (44.1%), while MouseLight shows a pronounced focus on DG (50.7%) and substantial CA3 connectivity (42.0%). In summary, dendritic arbor data underscores intraregional dominance within CA1 and DG, critical for local processing. Axonal projections from CA1 neurons suggest extensive interregional communication, while DG-sg neurons reinforce hippocampal circuitry, especially between DG and CA3. These patterns reflect the structural basis of neuronal communication and connectivity strength in these brain regions.'
  private basicInfoSummary: string = this.bs
  private morphologySummaries: string = this.ms
  private projectionInfoSummary: string = this.ps
  // eslint-disable-next-line camelcase
  private id_list : any[] = this.neuronsList
    .filter(neuron => !neuron.id.includes('local'))
    .map(neuron => neuron.id)
  private hasInitialized : boolean = false

  @Watch('basicInfo', { deep: true })
  onDataChange () {
    if (!this.hasInitialized) {
      // 初次加载时跳过执行
      this.hasInitialized = true
      return
    }

    console.log('onDataChange')
    this.id_list = this.neuronsList
      .filter(neuron => !neuron.id.includes('local'))
      .map(neuron => neuron.id)
    this.generateDataSummary()
    this.restartSSE()
  }

  private generateDataSummary () {
    this.basicInfoSummary = ''
    this.morphologySummaries = ''
    this.projectionInfoSummary = ''
  }

  private appendTextGradually (target: 'basicInfoSummary' | 'projectionInfoSummary' | 'morphologySummaries' |string, text: string) {
    this.messageQueue.push({ target, text })
    this.processQueue()
  }

  private processQueue () {
    if (this.isProcessing || this.messageQueue.length === 0) {
      return
    }

    this.isProcessing = true
    const { target, text } = this.messageQueue.shift()!
    let targetArray: string[] | null = null

    let targetCopy = target // 复制target变量

    // if (targetCopy.startsWith('morphologySummaries')) {
    //   const index = parseInt(targetCopy.split('[')[1].split(']')[0], 10)
    //   targetArray = this.morphologySummaries
    //   targetCopy = index.toString()
    // }

    let currentIndex = 0
    const intervalId = setInterval(() => {
      if (currentIndex < text.length) {
        if (targetArray) {
          Vue.set(targetArray, parseInt(targetCopy), (targetArray[parseInt(targetCopy)] || '') + text[currentIndex++])
        } else {
          Vue.set(this, targetCopy, (this as any)[targetCopy] + text[currentIndex++])
        }
      } else {
        clearInterval(intervalId)
        this.isProcessing = false
        this.processQueue() // 处理下一个消息
      }
    }, 5) // 控制字符显示速度，可以调整时间间隔
  }

  public startSSE (): void {
    console.log('startSSE')
    const neuronlists = {
      id_list: this.id_list
    }

    fetch('http://10.192.0.176:5000/api/start_stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Encoding': 'gzip'
      },
      body: JSON.stringify(neuronlists),
      credentials: 'include'
    })
      .then((response) => {
        const reader = response.body?.getReader()
        const decoder = new TextDecoder()
        let stopReading = false // 控制流读取的变量

        const readStream = (): Promise<void> => {
          if (stopReading) {
            console.log('Stream stopped')
            return Promise.resolve()
          }

          return reader?.read().then(({ done, value }) => {
            if (done) {
              console.log('Stream complete')
              return
            }

            const text = decoder.decode(value, { stream: true })
            text.split('\n\n').forEach(eventString => {
              if (eventString.trim() !== '') {
                const event = eventString.replace(/^data: /, '')
                const data = JSON.parse(event)

                if (data.type === 'end') {
                  console.log('Streaming finished')
                  stopReading = true
                  this.messageQueue = []
                } else if (data.type === 'ping') {
                  console.log('keep Streaming')
                } else if (data.type === 'basicInfo') {
                  this.appendTextGradually('basicInfoSummary', data.content)
                } else if (data.type === 'morphologyFeatures') {
                  this.appendTextGradually('morphologySummaries', data.content)
                } else if (data.type === 'projectionInfo') {
                  this.appendTextGradually('projectionInfoSummary', data.content)
                }
              }
            })

            return readStream() // Continue reading the stream
          }) as Promise<void>
        }

        return readStream()
      })
      .catch((error) => {
        console.error('Error in SSE fetch:', error)
      })
  }

  public stopSSE (): void {
    // 检查 eventSource 是否已初始化
    if (this.eventSource) {
      this.eventSource.close() // 确保关闭当前的 SSE 连接
      console.log('SSE connection closed')
    } else {
      console.warn('No SSE connection to close')
    }

    // 通知后端终止任务
    fetch('http://10.192.0.176:5000/api/stop_stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include'
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to stop the stream on the server')
        }
        return response.json()
      })
      .then(data => {
        console.log('Server response:', data)
      })
      .catch(error => {
        console.error('Error stopping SSE:', error)
      })
  }

  public restartSSE () {
    if (this.eventSource) {
      this.eventSource.close()
    }
    this.startSSE()
  }

  mounted () {
    this.$nextTick(() => {
      if (!this.hasStartedSSE) {
        this.hasStartedSSE = false
      }
    })
  }

  beforeDestroy () {
    if (this.eventSource) {
      this.eventSource.close()
    }
    this.hasInitialized = true
  }

  // private handleCollapseChange (val: string[]) {
  //   this.activeSection = val
  //   if (val.includes('dataSummary') && !this.hasStartedSSE) {
  //     this.startSSE()
  //     this.hasStartedSSE = true
  //     this.messageQueue = []
  //   }
  //   // if (!val.includes('dataSummary') && this.hasStartedSSE) {
  //   //   this.stopSSE()
  //   //   this.hasStartedSSE = false
  //   //   this.messageQueue = []
  //   // }
  // }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.summary-container {
  padding: 15px;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.summary-container p {
  margin: 10px 0;
  font-size: 16px;
  color: #333;
}

.summary-container ul {
  padding-left: 20px;
  list-style-type: disc;
}

.summary-container ul li {
  margin: 5px 0;
  font-size: 14px;
  color: #555;
}
.no-bullets {
  list-style-type: none;
  padding-left: 0;
}

</style>
