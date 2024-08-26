<template>
  <div class="home">
    <SmallScreenAlert />
    <el-container class="app-container">
      <el-header height="auto">
        <header-bar
          ref="headBar"
          @clickSearchButton="searchDialogVisible = true"
          @clickSearchByIDButton="searchByIDHandler"
          @clickSearchByLLMButton="LLMDialogVisible = true"
          @clickUploadNeuron="uploadNeuronHandler"
          @switchAtlas="switchAtlas($event)"
        />
      </el-header>
      <el-container>
        <el-main>
          <div class="main-content">
            <NeuronDetail
              v-if="reFresh"
              ref="neuronDetail"
              :load-first-neuron="loadFirstNeuron"
              :neurons-list="neuronsList"
              @checkConnectedNeurons="updateNeuronAnalysis($event, true)"
              @searchSimilarNeurons="searchSimilarNeurons($event)"
              @searchROINeurons="searchROINeurons($event)"
              @neuronView="updateCurrentNeuronInfo"
              @viewNeurons="viewNeurons"
              @showNeuronMap="showNeuronMap"
              @setVisualizedAxon="setVisualizedAxon"
              @setVisualizedBasal="setVisualizedBasal"
              @setVisualizedApical="setVisualizedApical"
              @setVisualizedSoma="setVisualizedSoma"
            />
          </div>
        </el-main>
        <el-aside width="auto">
          <NeuronList
            ref="neuronList"
            @neuronView="updateCurrentNeuronInfo"
            @neuronAnalysis="updateNeuronAnalysis"
            @checkNeuron="checkNeuron"
            @viewNeurons="viewNeurons"
          />
        </el-aside>
      </el-container>
    </el-container>
    <!-- 神经元搜索对话框 -->
    <el-dialog
      title="Neuron Search"
      :visible.sync="searchDialogVisible"
      width="90%"
      top="10vh"
      :close-on-click-modal="false"
    >
      <NeuronSearch
        ref="neuronSearch"
        @neuronAnalysis="updateNeuronAnalysis"
      />
      <span
        slot="footer"
        class="dialog-footer"
      >
        <el-button @click="searchDialogVisible = false">Cancel</el-button>
        <el-button
          type="primary"
          @click="Reset"
        >Reset</el-button>
        <el-button
          type="primary"
          @click="searchNeurons()"
        >Confirm</el-button>
      </span>
    </el-dialog>
    <!-- AI搜索对话框 -->
    <el-dialog
      title="AIPOM"
      custom-class="AIWindow"
      :visible.sync="LLMDialogVisible"
      width="50%"
      top="7vh"
      :close-on-click-modal="false"
    >
      <AISearchWindow
        ref="aiSearchWindow"
        @AISearch="AISearch"
        @executeCode="executeCode"
      />
      <span
        slot="footer"
        class="dialog-footer"
      >
        <el-button @click="LLMDialogVisible = false">
          Cancel
        </el-button>
        <el-button
          type="primary"
          @click="ClearMessage()"
        >Clear</el-button>
        <el-button
          type="primary"
          @click="AISearch()"
        >Confirm</el-button>
      </span>
    </el-dialog>>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Ref } from 'vue-property-decorator'
import HeaderBar from '@/components/mouse/HeaderBar.vue'
import NeuronList from '@/components/mouse/NeuronList.vue'
import NeuronDetail from '@/components/mouse/NeuronDetail.vue'
import NeuronSearch from '@/components/mouse/NeuronSearch.vue'
import {
  getNeuronInfo,
  searchNeurons,
  searchSimilarNeuron,
  uploadNeuron,
  searchROINeuron,
  AIChat,
  getSearchIntent,
  ArticleSearch,
  CodeGenerator,
  executeCode,
  AI_RAG,
  getSearchCondition
} from '@/request/apis/mouse/Neuron'
import SmallScreenAlert from '@/components/common/SmallScreenAlert.vue'
import NeuronLLM from '@/components/mouse/NeuronLLM.vue'
import AISearchWindow from '@/components/mouse/AISearchWindow.vue'
import { getCachedData, setCachedData, deleteCachedData } from '@/utils/indexedDB'
import { result } from 'lodash'
import NeuronLists from '@/components/mouse/NeuronLists.vue'

@Component({
  components: {
    NeuronLLM,
    SmallScreenAlert,
    NeuronSearch,
    NeuronDetail,
    NeuronList,
    HeaderBar,
    AISearchWindow
  }
})

export default class Container extends Vue {
  @Ref('neuronDetail') readonly neuronDetail!: NeuronDetail
  @Ref('neuronSearch') readonly neuronSearch!: NeuronSearch
  @Ref('neuronList') readonly neuronList!: NeuronList
  // @Ref('neuronLists') readonly neuronLists!: NeuronLists
  @Ref('neuronLLM') readonly neuronLLM!: NeuronLLM
  @Ref('headBar') readonly headBar!: HeaderBar
  @Ref('aiSearchWindow') readonly aiSearchWindow!: AISearchWindow
  private searchDialogVisible: boolean = false
  private LLMDialogVisible: boolean = false
  private reFresh: boolean = true
  private fullMorphNeurons:any[] = []
  private localMorphNeurons:any[] = []
  public neuronsList:any[] = []

  /**
   * 更新当前显示的 neuron info 信息
   * @param neuronDetail neuron detail
   * @private
   */
  private async updateCurrentNeuronInfo (neuronDetail: any) {
    this.neuronDetail.selectedTab = 'neuronInfo'
    await this.$nextTick()
    this.neuronDetail.neuronInfo.clearReconstruction()
    this.neuronDetail.neuronInfo.hideSoma()
    this.neuronDetail.neuronInfo.isUploadData = false
    await this.$nextTick()
    const needClear = !!this.neuronDetail.neuronInfo.neuronInfoData.id
    const neuronInfo = await getNeuronInfo(document.body, neuronDetail.id, this.$store.state.atlas).start()
    this.neuronDetail.neuronInfo.neuronInfoData = neuronInfo
    if (this.neuronDetail.neuronInfo.roiShown) {
      this.neuronDetail.neuronInfo.ROI.setROI(Math.round(neuronInfo.soma[0]), Math.round(neuronInfo.soma[1]), Math.round(neuronInfo.soma[2]))
    }
    if (this.neuronDetail.neuronInfo.somaShown) {
      this.neuronDetail.neuronInfo.Soma.setSoma(Math.round(neuronInfo.soma[0]), Math.round(neuronInfo.soma[1]), Math.round(neuronInfo.soma[2]))
    }
    // this.neuronDetail.neuronInfo.showSoma(100)
    // console.log('soma loaded')
    // this.neuronDetail.neuronInfo.neuronScene.updateSomaBall(Math.round(neuronInfo.soma[0]), Math.round(neuronInfo.soma[1]), Math.round(neuronInfo.soma[2]), 100)
    this.neuronDetail.neuronInfo.neuronViewerReconstructionData = neuronInfo.viewer_info
    await this.neuronDetail.neuronInfo.updateReconstruction(needClear)
    await this.$nextTick()
    this.neuronDetail.neuronInfo.showSoma(100)
  }
  /**
     * 更新当前显示的 neuron info 信息
     * @param neuronDetail neuron detail
     * @private
     */

  /**
     * 更新AI模型返回答案
     */
  private async getAIAdvice (neuronDetail: any) {
    this.neuronDetail.selectedTab = 'neuronInfo'
    await this.$nextTick()
    // this.neuronDetail.neuronInfo.clearReconstruction()
    // await this.$nextTick()
    // const needClear = !!this.neuronDetail.neuronInfo.neuronInfoData.id
    const AIAdvice = await AIChat(document.body, neuronDetail.question).start()
    // this.neuronDetail.neuronInfo.neuronInfoData = neuronInfo
    // this.neuronDetail.neuronInfo.neuronViewerReconstructionData = neuronInfo.viewer_info
    // await this.neuronDetail.neuronInfo.updateReconstruction(needClear)
  }

  /**
   * 根据神经元 ID 搜索
   */
  private async searchByIDHandler () {
    try {
      const id = (await this.$prompt('Please input a neuron id', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        closeOnClickModal: false
        // @ts-ignore
      })).value
      await this.updateCurrentNeuronInfo({ id })
    } catch (e) {}
  }

  /**
   * 根据选择的 neuron id 更新统计信息
   * @param neuronIds 选择的 neuron id
   * @param updateNeuronList 是否更新右侧神经元列表
   * @private
   */
  private async updateNeuronAnalysis (neuronIds: string[], updateNeuronList: boolean = false) {
    try {
      console.log('updateNeuronAnalysis')
      console.log(neuronIds)
      // eslint-disable-next-line camelcase
      const { basic_info, morpho_info, plot, proj_info, neurons } = await searchNeurons(document.body, { id_list: neuronIds }).start()
      this.neuronsList = neurons
      this.neuronDetail.selectedTab = 'neuronStates'
      this.neuronDetail.neuronStates.neuronStatesData = { basic_info: basic_info.counts, morpho_info, plot, proj_info }
      await this.$nextTick()
      this.neuronDetail.neuronStates.featurePlot.renderChart()
      this.neuronDetail.neuronStates.histogramBars.renderChart()
      if (updateNeuronList) {
        this.neuronList.setListData(neurons)
        // console.log(neurons)
        // this.neuronLists.neuronList.setListData(this.fullMorphNeurons)
        // this.neuronLists.neuronListLocal.setListData(this.localMorphNeurons)
      }
      this.searchDialogVisible = false
    } catch (e) {
      console.error(e)
    }
  }

  // eslint-disable-next-line camelcase
  // private sendData (basic_info: any, morpho_info: any, proj_info: any) {
  //   const data = {
  //     basic_info: basic_info, // Replace with actual data
  //     morpho_info: morpho_info, // Replace with actual data
  //     proj_info: proj_info // Replace with actual data
  //   }
  //
  //   fetch('http://10.192.40.36:5000/api/stream', {
  //     method: 'POST',
  //     headers: {
  //       'Content-Type': 'application/json'
  //     },
  //     body: JSON.stringify(data)
  //   }).then(response => {
  //     console.log('Data sent successfully')
  //     // this.neuronDetail.neuronStates.neuronStatesDesc.restartSSE() // Start receiving stream data
  //     // this.neuronDetail.neuronStates.neuronStatesDesc.hasStartedSSE = true
  //   }).catch(error => {
  //     console.error('Error sending data:', error)
  //   })
  // }

  /**
   * 搜索神经元
   * @param criteria 搜索条件
   * @param ids 神经元 ID 列表
   * @param func 回调函数
   * @private
   */
  // private async searchNeurons (criteria: any = undefined, ids: string[] | undefined = undefined, func: any = () => {}) {
  //   if (!criteria) {
  //     criteria = this.neuronSearch.getSearchCriteria()
  //   }
  //   criteria['brain_atlas'] = [this.$store.state.atlas]
  //   const condition = ids ? { id_list: ids } : { criteria: criteria }
  //   // console.log(condition)
  //   try {
  //     // eslint-disable-next-line camelcase
  //     const { neurons, basic_info, morpho_info, plot, proj_info } = await searchNeurons(document.body, condition).start()
  //     this.neuronDetail.selectedTab = 'neuronStates'
  //     this.neuronDetail.neuronStates.neuronStatesData = { basic_info: basic_info.counts, morpho_info, plot, proj_info }
  //     await this.$nextTick()
  //     this.neuronDetail.neuronStates.featurePlot.renderChart()
  //     this.neuronDetail.neuronStates.histogramBars.renderChart()
  //     this.searchDialogVisible = false
  //     this.neuronList.setListData(neurons)
  //     this.neuronsList = neurons
  //     // this.neuronLists.neuronListLocal.setListData(this.localMorphNeurons)
  //     func()
  //   } catch (e) {
  //     console.error(e)
  //   }
  //   await this.setVisualizedSoma()
  // }
  private async searchNeurons (criteria: any = undefined, ids: string[] | undefined = undefined, func: any = () => {}) {
    if (!criteria) {
      criteria = this.neuronSearch.getSearchCriteria()
    }
    criteria['brain_atlas'] = [this.$store.state.atlas]
    const condition = ids ? { id_list: ids } : { criteria: criteria }

    const cacheKey = ids ? `neurons_ids_${ids.join('_')}` : `neurons_criteria_${JSON.stringify(criteria)}`

    // 设置缓存有效期为1小时
    const CACHE_DURATION = 604800000

    // 检查缓存
    const cachedData = await getCachedData(cacheKey)
    if (cachedData) {
      console.log('have cache')
      const currentTime = new Date().getTime()
      if (currentTime - cachedData.timestamp < CACHE_DURATION) {
        console.log('use cache')
        // eslint-disable-next-line camelcase
        const { neurons, basic_info, morpho_info, plot, proj_info } = cachedData
        this.neuronsList = neurons
        await this.useNeuronData(neurons, basic_info, morpho_info, plot, proj_info)
        func()
        return
      } else {
        await deleteCachedData(cacheKey) // 缓存过期，移除缓存
      }
    }

    try {
      console.log('no cache')
      const response = await searchNeurons(document.body, condition).start()
      // eslint-disable-next-line camelcase
      const { neurons, basic_info, morpho_info, plot, proj_info } = response as any
      this.neuronsList = neurons
      await this.useNeuronData(neurons, basic_info, morpho_info, plot, proj_info)

      // 缓存数据，附带时间戳
      console.log('make cache')
      const dataToCache = {
        timestamp: new Date().getTime(),
        neurons,
        basic_info,
        morpho_info,
        plot,
        proj_info
      }
      await setCachedData(cacheKey, dataToCache)

      func()
    } catch (e) {
      console.error(e)
    }
    await this.setVisualizedSoma()
  }

  // eslint-disable-next-line camelcase
  private async useNeuronData (neurons: any, basic_info: any, morpho_info: any, plot: any, proj_info: any) {
    this.neuronDetail.selectedTab = 'neuronStates'
    this.neuronDetail.neuronStates.neuronStatesData = { basic_info: basic_info.counts, morpho_info, plot, proj_info }
    await this.$nextTick()
    this.neuronDetail.neuronStates.featurePlot.renderChart()
    this.neuronDetail.neuronStates.histogramBars.renderChart()
    this.searchDialogVisible = false
    this.neuronList.setListData(neurons)
    this.neuronsList = neurons
  }

  private async executeCode (func: any = () => {}) {
    const code = this.aiSearchWindow.code
    console.log('code is: ' + code)
    func()
    try {
      // eslint-disable-next-line camelcase
      const response = await executeCode(document.body).start()
      // let res = JSON.parse(response)
      console.log(response)
      this.aiSearchWindow.addResponseFromAPI(response.response)
      func()
    } catch (e) {
      console.error(e)
    }
  }

  private async AISearch (func: any = () => {}) {
    console.time('startSearchTime')
    this.aiSearchWindow.sendMessage()
    let question = this.aiSearchWindow.lastInput
    console.log('question is: ' + question)
    let searchIntent = 'unknown intent'
    let searchConditions = {}

    // try {
    //   const response = await CodeGenerator(document.body, question).start()
    //   console.log(response)
    //   this.aiSearchWindow.addResponseFromAPI(response.response)
    //   func()
    // } catch (e) {
    //   console.error(e)
    // }

    // 检查用户输入是否为 [Intent]: query 形式并验证意图
    const intentMatch = question.match(/^\[(search|chat|retrieval|article)\]:\s*(.+)/i)
    if (intentMatch) {
      searchIntent = intentMatch[1].trim().toLowerCase()
      question = question.split(':')[1]
      console.log('Extracted intent: ' + searchIntent)
    } else {
      try {
        let response = await getSearchIntent(document.body, question).start()
        searchIntent = response.response.replace(/^'|'$/g, '')
        console.log(searchIntent)
        this.aiSearchWindow.addResponseFromAPI('I guess you want to ' + searchIntent + ', is that right?')
        func()
      } catch (e) {
        console.error(e)
      }
    }
    if (searchIntent === 'article') {
      try {
        const response = await ArticleSearch(document.body, question).start()
        console.log(response)
        this.aiSearchWindow.addResponseFromAPI(response.response.articles)
        func()
      } catch (e) {
        console.error(e)
      }
    }

    if (searchIntent === 'search') {
      // let result = this.aiSearchWindow.GetIntent(question)
      // console.log(result)
      const response = await getSearchCondition(document.body, question).start()
      let result = response.response
      result = JSON.parse(result.replace(/'/g, '"'))
      const condition = { criteria: result }
      searchConditions = condition
      console.log(condition)
      try {
        // eslint-disable-next-line camelcase
        const { neurons, basic_info, morpho_info, plot, proj_info } = await searchNeurons(document.body, searchConditions).start()
        this.neuronList.setListData(neurons)
        this.neuronDetail.selectedTab = 'neuronStates'
        this.neuronDetail.neuronStates.neuronStatesData = { basic_info: basic_info.counts, morpho_info, plot, proj_info }
        await this.$nextTick()
        this.neuronDetail.neuronStates.featurePlot.renderChart()
        this.neuronDetail.neuronStates.histogramBars.renderChart()
        this.LLMDialogVisible = false
        this.aiSearchWindow.addResponseFromAPI('I have found ' + neurons.length + ' neurons')
        this.aiSearchWindow.addResponseFromAPI('Are these the results you are looking for? If not please tell me more information')
        func()
      } catch (e) {
        console.error(e)
      }
    }

    if (searchIntent === 'chat') {
      try {
        const response = await AIChat(document.body, question).start()
        console.log(response)
        const formattedResponse = response.response.replace(/\n/g, '<br>')
        this.aiSearchWindow.addResponseFromAPI(formattedResponse)
        this.aiSearchWindow.addResponseFromAPI('Did you get the results you wanted? If not please enrich your question!')
        func()
      } catch (e) {
        console.error(e)
      }
    }

    if (searchIntent === 'retrieval') {
      try {
        const response = await AI_RAG(document.body, question).start()
        console.log(response)
        const formattedResponse = response.response.replace(/\n/g, '<br>')
        this.aiSearchWindow.addResponseFromAPI(formattedResponse)
        this.aiSearchWindow.addResponseFromAPI('Did you get the results you wanted? If not please enrich your question!')
        func()
      } catch (e) {
        console.error(e)
      }
    }
    console.timeEnd('startSearchTime')
  }

  // private async AISearch (func: any = () => {}) {
  //   this.aiSearchWindow.sendMessage()
  //   const question = this.aiSearchWindow.lastInput
  //   console.log('question is: ' + question)
  //   let searchIntent = 'unknown intent'
  //   let searchConditions = {}
  //   try {
  //     let response = await getSearchIntent(document.body, question).start()
  //     searchIntent = response.response.replace(/^'|'$/g, '')
  //     console.log(searchIntent)
  //     this.aiSearchWindow.addResponseFromAPI('I guess you want to ' + searchIntent + ', is that right?')
  //     func()
  //     if (searchIntent === 'search articles') {
  //       try {
  //         const response = await ArticleSearch(document.body, question).start()
  //         // let res = JSON.parse(response)
  //         console.log(response)
  //         this.aiSearchWindow.addResponseFromAPI(response.response.articles)
  //         // this.aiSearchWindow.addResponseFromAPI('Did you get the results you wanted? If not please enrich your question!')
  //         func()
  //       } catch (e) {
  //         console.error(e)
  //       }
  //     }
  //     if (searchIntent === 'search neuron data') {
  //       let result = this.aiSearchWindow.GetIntent(question)
  //       const condition = { criteria: result }
  //       searchConditions = condition
  //       console.log(condition)
  //       try {
  //         // eslint-disable-next-line camelcase
  //         const { neurons, basic_info, morpho_info, plot, proj_info } = await searchNeurons(document.body, searchConditions).start()
  //         this.neuronList.setListData(neurons)
  //         this.neuronDetail.selectedTab = 'neuronStates'
  //         this.neuronDetail.neuronStates.neuronStatesData = { basic_info: basic_info.counts, morpho_info, plot, proj_info }
  //         await this.$nextTick()
  //         this.neuronDetail.neuronStates.featurePlot.renderChart()
  //         this.neuronDetail.neuronStates.histogramBars.renderChart()
  //         this.LLMDialogVisible = false
  //         this.aiSearchWindow.addResponseFromAPI('I have found ' + neurons.length + ' neurons')
  //         this.aiSearchWindow.addResponseFromAPI('Are these the results you are looking for? If not please tell me more information')
  //         func()
  //       } catch (e) {
  //         console.error(e)
  //       }
  //     }
  //     if (searchIntent === 'chat with neuroxiv website') {
  //       try {
  //         // eslint-disable-next-line camelcase
  //         const response = await AIChat(document.body, question).start()
  //         // let res = JSON.parse(response)
  //         console.log(response)
  //         const formattedResponse = response.response.replace(/\n/g, '<br>')
  //         this.aiSearchWindow.addResponseFromAPI(formattedResponse)
  //         // this.aiSearchWindow.addResponseFromAPI(response.response)
  //         this.aiSearchWindow.addResponseFromAPI('Did you get the results you wanted? If not please enrich your question!')
  //         func()
  //       } catch (e) {
  //         console.error(e)
  //       }
  //     }
  //     if (searchIntent === 'summary') {
  //       try {
  //         // eslint-disable-next-line camelcase
  //         const response = await AIChat(document.body, question).start()
  //         // let res = JSON.parse(response)
  //         console.log(response)
  //         const formattedResponse = response.response.replace(/\n/g, '<br>')
  //         this.aiSearchWindow.addResponseFromAPI(formattedResponse)
  //         // this.aiSearchWindow.addResponseFromAPI(response.response)
  //         this.aiSearchWindow.addResponseFromAPI('Did you get the results you wanted? If not please enrich your question!')
  //         func()
  //       } catch (e) {
  //         console.error(e)
  //       }
  //       this.aiSearchWindow.addResponseFromAPI('NeuAgent didn\'t understand what you meant, can you ask it differently?')
  //     }
  //   } catch (e) {
  //     console.error(e)
  //   }
  // }

  private async ClearMessage (func: any = () => {}) {
    this.aiSearchWindow.messages = []
  }

  /**
   * 上传神经元并计算神经元特征
   * @param param 通过该参数获得要上传的文件
   */
  // private async uploadNeuronHandler (param: any) {
  //   try {
  //     this.neuronDetail.selectedTab = 'neuronInfo'
  //     await this.$nextTick()
  //     const needClear = !!this.neuronDetail.neuronInfo.neuronInfoData.id
  //     const form = new FormData()
  //     form.append('file', param.file)
  //     const neuronInfo = await uploadNeuron(document.body, form).start()
  //     this.neuronDetail.neuronInfo.clearReconstruction()
  //     await this.$nextTick()
  //     this.neuronDetail.neuronInfo.neuronInfoData = neuronInfo
  //     this.neuronDetail.neuronInfo.neuronViewerReconstructionData = neuronInfo.viewer_info
  //     await this.neuronDetail.neuronInfo.updateReconstruction(needClear)
  //   } catch (e) {
  //     console.error(e)
  //   }
  // }

  private async uploadNeuronHandler (param: any) {
    try {
      this.neuronDetail.selectedTab = 'neuronInfo'
      await this.$nextTick()
      const needClear = !!this.neuronDetail.neuronInfo.neuronInfoData.id
      const form = new FormData()
      form.append('file', param.file)

      // 调用实际的上传函数
      const loadingTarget = document.body
      const requestInstance = uploadNeuron(loadingTarget, form)

      // 处理请求结果
      requestInstance.start().then((neuronInfo) => {
        this.neuronDetail.neuronInfo.clearReconstruction()
        this.neuronDetail.neuronInfo.hideSoma()
        this.neuronDetail.neuronInfo.isUploadData = false
        this.$nextTick().then(() => {
          this.neuronDetail.neuronInfo.isUploadData = true
          this.neuronDetail.neuronInfo.neuronInfoData = neuronInfo
          this.neuronDetail.neuronInfo.showSoma(100)
          this.neuronDetail.neuronInfo.neuronViewerReconstructionData = neuronInfo.viewer_info
          this.neuronDetail.neuronInfo.updateReconstruction(needClear)

          // 调用成功回调
          param.onSuccess?.(neuronInfo)
        })
      }).catch((error) => {
        console.error(error)
        param.onError?.(new ErrorEvent('error', { message: '上传神经元失败' }))
      })
    } catch (e) {
      console.error(e)
      param.onError?.(new ErrorEvent('error', { message: '上传神经元失败' }))
    }
  }

  /**
   * 清空搜索条件
   * @constructor
   * @private
   */
  private Reset () {
    this.neuronSearch.selectedConditions = []
  }

  /**
   * 搜索相似神经元，返回搜索条件
   * @param neuronInfo 神经元的信息
   * @private
   */
  private async searchSimilarNeurons (neuronInfo: any) {
    try {
      this.searchDialogVisible = true
      await this.$nextTick()
      neuronInfo['brain_atlas'] = this.$store.state.atlas
      this.neuronSearch.selectedConditions = await searchSimilarNeuron(document.body, neuronInfo).start()
      console.log(this.neuronSearch.selectedConditions)
    } catch (e) {
      console.error(e)
    }
    await this.setVisualizedSoma()
  }

  /**
   * 搜索ROI神经元
   * @param roiParameter ROI的位置与半径，用字符串表示，x_y_z_r
   * @private
   */
  private async searchROINeurons (roiParameter: string) {
    try {
      // eslint-disable-next-line camelcase
      const { neurons, basic_info, morpho_info, plot, proj_info } = await searchROINeuron(document.body, roiParameter, this.$store.state.atlas).start()
      // this.fullMorphNeurons = []
      // this.localMorphNeurons = []
      // neurons.forEach((neuron: { id: string | string[] }) => {
      //   if (neuron.id.includes('full')) {
      //     this.fullMorphNeurons.push(neuron)
      //   } else if (neuron.id.includes('local')) {
      //     this.localMorphNeurons.push(neuron)
      //   }
      // })
      this.neuronList.setListData(neurons)
      // this.neuronLists.neuronListLocal.setListData(this.localMorphNeurons)
      // this.neuronLists.neuronList.setListData(neurons)
      this.neuronDetail.selectedTab = 'neuronStates'
      this.neuronDetail.neuronStates.neuronStatesData = { basic_info: basic_info.counts, morpho_info, plot, proj_info }
      await this.$nextTick()
      this.neuronDetail.neuronStates.featurePlot.renderChart()
      this.neuronDetail.neuronStates.histogramBars.renderChart()
    } catch (e) {
      console.log(e)
    }
    await this.setVisualizedSoma()
  }

  /**
   * 选中或取消右方神经元列表中的神经元的神经元的回调函数，用于在3D viewer里展示
   * @param neuronDetail 神经元的具体信息，包括是否有dendrite、axon，id以及是否选中
   * @param switchTab 是否要主动切换到3D viewer栏
   */
  // public async checkNeuron (neuronDetail: any, switchTab: boolean = false) {
  //   if (switchTab && this.neuronDetail.selectedTab !== 'multiNeuronsViewer') {
  //     this.neuronDetail.selectedTab = 'multiNeuronsViewer'
  //     await this.$nextTick()
  //   }
  //   await this.$nextTick()
  //   if (this.neuronDetail.selectedTab === 'multiNeuronsViewer') {
  //     let dendriteData = {
  //       id: neuronDetail.id + '_basal',
  //       name: neuronDetail.id + '_basal',
  //       src: '',
  //       // eslint-disable-next-line camelcase
  //       rgb_triplet: [0, 0, 255],
  //       info: {
  //         id: neuronDetail.id,
  //         cellType: neuronDetail.celltype
  //       }
  //     }
  //     let apicalData = {
  //       id: neuronDetail.id + '_apical',
  //       name: neuronDetail.id + '_apical',
  //       src: '',
  //       // eslint-disable-next-line camelcase
  //       rgb_triplet: [255, 0, 255],
  //       info: {
  //         id: neuronDetail.id,
  //         cellType: neuronDetail.celltype
  //       }
  //     }
  //     let axonData = {
  //       id: neuronDetail.id + '_axon',
  //       name: neuronDetail.id + '_axon',
  //       src: '',
  //       // eslint-disable-next-line camelcase
  //       rgb_triplet: [255, 0, 0],
  //       info: {
  //         id: neuronDetail.id,
  //         cellType: neuronDetail.celltype
  //       }
  //     }
  //     let localData = {
  //       id: neuronDetail.id + '_local',
  //       name: neuronDetail.id + '_local',
  //       src: '',
  //       // eslint-disable-next-line camelcase
  //       rgb_triplet: [0, 0, 255],
  //       info: {
  //         id: neuronDetail.id,
  //         cellType: neuronDetail.celltype
  //       }
  //     }
  //     if (this.neuronDetail.multiNeuronsViewer.neuronScene.checkLoadComponent(dendriteData) ||
  //         this.neuronDetail.multiNeuronsViewer.neuronScene.checkLoadComponent(axonData) || this.neuronDetail.multiNeuronsViewer.neuronScene.checkLoadComponent(apicalData) || this.neuronDetail.multiNeuronsViewer.neuronScene.checkLoadComponent(localData) ||
  //         !neuronDetail.selected) {
  //       if (neuronDetail['has_dendrite'] && this.neuronDetail.multiNeuronsViewer.showAllBasal) {
  //         this.neuronDetail.multiNeuronsViewer.neuronScene.setComponentVisible(dendriteData, neuronDetail.selected)
  //       }
  //       if (neuronDetail['has_axon'] && this.neuronDetail.multiNeuronsViewer.showAllAxon) {
  //         this.neuronDetail.multiNeuronsViewer.neuronScene.setComponentVisible(axonData, neuronDetail.selected)
  //       }
  //       if (neuronDetail['has_apical'] && this.neuronDetail.multiNeuronsViewer.showAllApical) {
  //         this.neuronDetail.multiNeuronsViewer.neuronScene.setComponentVisible(apicalData, neuronDetail.selected)
  //       }
  //       if (neuronDetail['has_local'] && this.neuronDetail.multiNeuronsViewer.showAllBasal) {
  //         this.neuronDetail.multiNeuronsViewer.neuronScene.setComponentVisible(localData, neuronDetail.selected)
  //       }
  //     } else {
  //       const neuronInfo = await getNeuronInfo(document.body, neuronDetail.id, this.$store.state.atlas).start()
  //       console.log(neuronInfo)
  //       this.neuronDetail.multiNeuronsViewer.neuronScene.multiViewerSomaPos.set(neuronDetail.id, neuronInfo.soma)
  //       dendriteData.src = neuronInfo.viewer_info[0].children[0].src
  //       console.log(dendriteData.src)
  //       axonData.src = neuronInfo.viewer_info[0].children[1].src
  //       apicalData.src = neuronInfo.viewer_info[0].children[2].src
  //       localData.src = neuronInfo.viewer_info[0].children[3].src
  //       if (neuronDetail['has_dendrite']) {
  //         await this.neuronDetail.multiNeuronsViewer.neuronScene.loadObj(dendriteData)
  //         this.neuronDetail.multiNeuronsViewer.neuronScene.setComponentVisible(dendriteData, this.neuronDetail.multiNeuronsViewer.showAllBasal)
  //       }
  //       if (neuronDetail['has_axon']) {
  //         await this.neuronDetail.multiNeuronsViewer.neuronScene.loadObj(axonData)
  //         this.neuronDetail.multiNeuronsViewer.neuronScene.setComponentVisible(axonData, this.neuronDetail.multiNeuronsViewer.showAllAxon)
  //       }
  //       if (neuronDetail['has_apical']) {
  //         await this.neuronDetail.multiNeuronsViewer.neuronScene.loadObj(apicalData)
  //         this.neuronDetail.multiNeuronsViewer.neuronScene.setComponentVisible(apicalData, this.neuronDetail.multiNeuronsViewer.showAllApical)
  //       }
  //       if (neuronDetail['has_local']) {
  //         await this.neuronDetail.multiNeuronsViewer.neuronScene.loadObj(localData)
  //         this.neuronDetail.multiNeuronsViewer.neuronScene.setComponentVisible(localData, this.neuronDetail.multiNeuronsViewer.showAllBasal)
  //       }
  //     }
  //     await this.setVisualizedSoma()
  //   }
  // }
  public async checkNeuron (neuronDetail: any, switchTab: boolean = false) {
    if (switchTab && this.neuronDetail.selectedTab !== 'multiNeuronsViewer') {
      this.neuronDetail.selectedTab = 'multiNeuronsViewer'
      await this.$nextTick()
    }

    if (this.neuronDetail.selectedTab !== 'multiNeuronsViewer') {
      return
    }

    const baseData = {
      id: neuronDetail.id,
      name: neuronDetail.id,
      src: '',
      info: {
        id: neuronDetail.id,
        cellType: neuronDetail.celltype
      }
    }

    const dendriteData = { ...baseData, id: neuronDetail.id + '_basal', name: neuronDetail.id + '_basal', rgb_triplet: [0, 0, 255] }
    const apicalData = { ...baseData, id: neuronDetail.id + '_apical', name: neuronDetail.id + '_apical', rgb_triplet: [255, 0, 255] }
    const axonData = { ...baseData, id: neuronDetail.id + '_axon', name: neuronDetail.id + '_axon', rgb_triplet: [255, 0, 0] }
    const localData = { ...baseData, id: neuronDetail.id + '_local', name: neuronDetail.id + '_local', rgb_triplet: [0, 0, 255] }

    const neuronScene = this.neuronDetail.multiNeuronsViewer.neuronScene

    const checkLoadComponent = (data:any) => neuronScene.checkLoadComponent(data)

    if ([dendriteData, apicalData, axonData, localData].some(checkLoadComponent) || !neuronDetail.selected) {
      if (neuronDetail['has_dendrite'] && this.neuronDetail.multiNeuronsViewer.showAllBasal) {
        neuronScene.setComponentVisible(dendriteData, neuronDetail.selected)
      }
      if (neuronDetail['has_axon'] && this.neuronDetail.multiNeuronsViewer.showAllAxon) {
        neuronScene.setComponentVisible(axonData, neuronDetail.selected)
      }
      if (neuronDetail['has_apical'] && this.neuronDetail.multiNeuronsViewer.showAllApical) {
        neuronScene.setComponentVisible(apicalData, neuronDetail.selected)
      }
      if (neuronDetail['has_local'] && this.neuronDetail.multiNeuronsViewer.showAllBasal) {
        neuronScene.setComponentVisible(localData, neuronDetail.selected)
      }
    } else {
      const neuronInfo = await getNeuronInfo(document.body, neuronDetail.id, this.$store.state.atlas).start()
      console.log(neuronInfo)

      this.neuronDetail.multiNeuronsViewer.neuronScene.multiViewerSomaPos.set(neuronDetail.id, neuronInfo.soma)

      dendriteData.src = neuronInfo.viewer_info[0].children[0].src
      axonData.src = neuronInfo.viewer_info[0].children[1].src
      apicalData.src = neuronInfo.viewer_info[0].children[2].src
      localData.src = neuronInfo.viewer_info[0].children[3].src

      const loadAndSetVisible = async (data:any, condition: any, visibility: boolean) => {
        if (condition) {
          await neuronScene.loadObj(data)
          neuronScene.setComponentVisible(data, visibility)
        }
      }

      await Promise.all([
        loadAndSetVisible(dendriteData, neuronDetail['has_dendrite'], this.neuronDetail.multiNeuronsViewer.showAllBasal),
        loadAndSetVisible(axonData, neuronDetail['has_axon'], this.neuronDetail.multiNeuronsViewer.showAllAxon),
        loadAndSetVisible(apicalData, neuronDetail['has_apical'], this.neuronDetail.multiNeuronsViewer.showAllApical),
        loadAndSetVisible(localData, neuronDetail['has_local'], this.neuronDetail.multiNeuronsViewer.showAllBasal)
      ])
    }

    await this.setVisualizedSoma()
  }

  /**
   * 将神经元列表中勾选的的神经元进行展示
   */
  public async viewNeurons () {
    let neuronsDetail = this.neuronList.getSelectedItems()
    this.neuronDetail.multiNeuronsViewer.neuronScene.setAllNeuronsVisible(false)
    neuronsDetail.forEach((neuronDetail: any) => {
      this.checkNeuron(neuronDetail, true)
    })
  }

  /**
   * 将神经元列表中勾选的的神经元进行展示
   */
  public async setVisualizedSoma () {
    let neuronsDetail = this.neuronList.getSelectedItems()
    let selectedIds = new Set(neuronsDetail.map(neuronDetail => neuronDetail.id))

    // 显示选中的神经元
    neuronsDetail.forEach((neuronDetail: any) => {
      this.neuronDetail.multiNeuronsViewer.neuronScene.showMultiViewerSomaBall(neuronDetail.id, 100, this.neuronDetail.multiNeuronsViewer.showAllSoma)
    })

    // 清除Map中未被选中的神经元
    this.neuronDetail.multiNeuronsViewer.neuronScene.multiViewerSoma.forEach((value, key) => {
      if (!selectedIds.has(key)) {
        this.neuronDetail.multiNeuronsViewer.neuronScene.unloadMultiViewerSomaBalls(key)
        this.neuronDetail.multiNeuronsViewer.neuronScene.multiViewerSoma.delete(key)
      }
    })
  }
  public async setVisualizedAxon ($event: any) {
    let neuronsDetail = this.neuronList.getSelectedItems()
    neuronsDetail.forEach((neuronDetail: any) => {
      let axonData = {
        id: neuronDetail.id + '_axon',
        name: neuronDetail.id + '_axon',
        src: '',
        // eslint-disable-next-line camelcase
        rgb_triplet: [255, 0, 0],
        info: {
          id: neuronDetail.id,
          cellType: neuronDetail.celltype
        }
      }
      if (this.neuronDetail.multiNeuronsViewer.neuronScene.checkLoadComponent(axonData)) {
        if (neuronDetail['has_axon']) {
          this.neuronDetail.multiNeuronsViewer.neuronScene.setComponentVisible(axonData, this.neuronDetail.multiNeuronsViewer.showAllAxon)
        }
      }
    })
  }
  public async setVisualizedBasal () {
    let neuronsDetail = this.neuronList.getSelectedItems()
    neuronsDetail.forEach((neuronDetail: any) => {
      let dendriteData = {
        id: neuronDetail.id + '_basal',
        name: neuronDetail.id + '_basal',
        src: '',
        // eslint-disable-next-line camelcase
        rgb_triplet: [0, 0, 255],
        info: {
          id: neuronDetail.id,
          cellType: neuronDetail.celltype
        }
      }
      let localData = {
        id: neuronDetail.id + '_local',
        name: neuronDetail.id + '_local',
        src: '',
        // eslint-disable-next-line camelcase
        rgb_triplet: [0, 0, 255],
        info: {
          id: neuronDetail.id,
          cellType: neuronDetail.celltype
        }
      }
      if (this.neuronDetail.multiNeuronsViewer.neuronScene.checkLoadComponent(dendriteData) || this.neuronDetail.multiNeuronsViewer.neuronScene.checkLoadComponent(localData)) {
        if (neuronDetail['has_dendrite']) {
          this.neuronDetail.multiNeuronsViewer.neuronScene.setComponentVisible(dendriteData, this.neuronDetail.multiNeuronsViewer.showAllBasal)
        }
        if (neuronDetail['has_local']) {
          this.neuronDetail.multiNeuronsViewer.neuronScene.setComponentVisible(localData, this.neuronDetail.multiNeuronsViewer.showAllBasal)
        }
      }
    })
  }
  public async setVisualizedApical () {
    let neuronsDetail = this.neuronList.getSelectedItems()
    neuronsDetail.forEach((neuronDetail: any) => {
      let apicalData = {
        id: neuronDetail.id + '_apical',
        name: neuronDetail.id + '_apical',
        src: '',
        // eslint-disable-next-line camelcase
        rgb_triplet: [255, 0, 255],
        info: {
          id: neuronDetail.id,
          cellType: neuronDetail.celltype
        }
      }
      if (this.neuronDetail.multiNeuronsViewer.neuronScene.checkLoadComponent(apicalData)) {
        if (neuronDetail['has_dendrite']) {
          this.neuronDetail.multiNeuronsViewer.neuronScene.setComponentVisible(apicalData, this.neuronDetail.multiNeuronsViewer.showAllApical)
        }
      }
    })
  }
  /**
   * 加载神经元列表第一个神经元
   */
  public async loadFirstNeuron () {
    await this.updateCurrentNeuronInfo(this.neuronList.getFirstItem())
  }

  public async showNeuronMap () {
    this.neuronDetail.multiNeuronsViewer.neuronScene.showMap(10)
  }

  /**
   * 切换当前atlas
   * @param atlas
   */
  public async switchAtlas (atlas: string) {
    // location.reload()
    this.headBar.setAtlas(atlas)
    this.$store.commit('updateAtlas', atlas)
    this.reFresh = false
    this.$nextTick(() => {
      this.reFresh = true
      let criteria = {
        brain_atlas: [this.$store.state.atlas]
      }
      this.searchNeurons(criteria, undefined, () => {
        this.neuronDetail.selectedTab = 'multiNeuronsViewer'
      })
    })
  }
  mounted () {
    setTimeout(() => {
      console.log('----------route----------', this.$route.query)
      if (this.$route.query.hasOwnProperty('brainRegion') && this.$route.query.hasOwnProperty('atlasName')) {
        // @ts-ignore
        // this.switchAtlas(this.$route.query['atlasName'])
        this.headBar.setAtlas(this.$route.query['atlasName'])
        // @ts-ignore
        this.$store.commit('updateAtlas', this.$route.query['atlasName'])
        this.$nextTick(() => {
          let criteria = {
            brain_atlas: [this.$store.state.atlas],
            celltype: [this.$route.query['brainRegion']]
          }
          this.searchNeurons(criteria)
        })
      } else {
        // console.log('mounted atlas', this.$store.state.atlas)
        let criteria = {
          brain_atlas: [this.$store.state.atlas]
        }
        this.searchNeurons(criteria, undefined, () => {
          this.neuronDetail.selectedTab = 'multiNeuronsViewer'
        })
      }
    }, 2000, {})
  }
}
</script>

<style lang="less" scoped>
.home {
  overflow: auto;
  height: 100%;
}
.app-container {
  min-width: 1300px;
  height: 100%;
  .el-header {
    padding: 0;
  }
  .el-main {
    height: 100%;
    .main-content {
      height: 100%;
    }
  }
  .el-aside {
    height: 100%;
    overflow: visible;
    box-shadow: 3px 3px 8px 2px var(--shadow-color);
  }
}
.AIWindow {
  /* 调整对话框宽度，使其适应内容 */
  width: 50%;
  /* 可以调整对话框顶部的位置 */
  top: 20vh;
  /* 如果您想要对话框宽度自适应，可以设置为 auto */
  /* width: auto; */
}

.AIWindow .el-dialog__header {
  /* 对话框头部的样式，如果需要的话 */
  text-align: center;
  padding: 15px 20px;
}

.AIWindow .el-dialog {
  /* 设置对话框的背景颜色为现代的灰色，并略微调整阴影 */
  background: #f5f5f5; /* 调整为您喜欢的颜色 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.AIWindow .el-dialog__body {
  /* 对话框内容的内边距 */
  padding: 20px;
}

.AIWindow .chat-window {
  /* 移除可能影响到布局的最大宽度和阴影 */
  max-width: none;
  box-shadow: none;
  /* 设置聊天窗口的高度，这取决于您的对话框高度 */
  height: 65vh;
  /* 满宽度 */
  width: 100%;
  /* 移除边距 */
  margin: 0;
}

.AIWindow .chat-messages {
  /* 设置消息区域的样式，允许滚动 */
  overflow-y: auto;
  height: 100%; /* 或根据需要设置一个固定高度 */
}

/* 样式调整，以适应聊天窗口内的消息气泡 */
.AIWindow .user-message, .AIWindow .system-message {
  /* 限制气泡宽度，确保消息在对话框中正确显示 */
  max-width: 70%;
  margin-bottom: 10px;
  border-radius: 18px;
  padding: 10px;
}

/* 用户消息的特定样式 */
.AIWindow .user-message {
  /* 靠右浮动，背景色调整 */
  float: right;
  clear: both;
  background-color: #007bff;
  color: white;
  margin-right: 20px; /* 消息与对话框边缘的距离 */
}

/* 系统消息的特定样式 */
.AIWindow .system-message {
  /* 靠左浮动，背景色调整 */
  float: left;
  clear: both;
  background-color: #e1e1e1;
  color: black;
  margin-left: 20px; /* 消息与对话框边缘的距离 */
}

/* 输入框样式调整，以适应对话框 */
.AIWindow .input-box {
  width: calc(100% - 40px); /* 输入框的宽度减去左右边距 */
  margin: 20px; /* 输入框与对话框边缘的距离 */
  padding: 10px 15px;
  border-radius: 22px;
  border: 2px solid #007bff;
  outline: none;
}

/* 对话框底部按钮的样式 */
.AIWindow .dialog-footer {
  text-align: right; /* 按钮靠右对齐 */
  padding: 10px 20px; /* 底部内边距 */
}

/* 确保按钮具有一致的样式 */
.AIWindow .el-button {
  margin-left: 10px; /* 按钮之间的间距 */
}

/* 按钮样式 */
.AIWindow .dialog-footer .el-button {
  border: none; /* 移除边框 */
  box-shadow: none; /* 移除阴影 */
  border-radius: 4px; /* 轻微的圆角 */
  background: #007bff; /* 蓝色背景，可以根据您的品牌颜色调整 */
  color: white; /* 白色文字 */
  margin-left: 8px; /* 按钮之间的间距 */
}

.AIWindow .dialog-footer .el-button:hover {
  background: #0056b3; /* 悬浮时更深的蓝色 */
}

.AIWindow .dialog-footer .el-button:active {
  background: #003a75; /* 按下时的颜色 */
}

/* 第一个按钮使用透明背景，以区分它与其他操作按钮 */
.AIWindow .dialog-footer .el-button:first-child {
  background: transparent;
  color: #007bff;
}

.AIWindow .dialog-footer .el-button:first-child:hover {
  background: rgba(0, 123, 255, 0.1); /* 悬浮时的背景颜色 */
}
</style>
