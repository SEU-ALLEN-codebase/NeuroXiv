<template>
  <div class="neuron-info-container">
    <div class="left-side">
      <el-tabs
        v-model="selectedTab"
        :stretch="true"
        class="full-height"
      >
        <el-tab-pane
          label="info"
          name="info"
        >
          <section class="feature-desc">
            <el-collapse v-model="activeNames1">
              <el-collapse-item
                title="neuron information"
                name="basicInfo"
              >
                <p>{{ neuronInfoData.id }}</p>
                <p>brain region: {{ neuronInfoData.celltype }}</p>
                <p>registration atlas: {{ neuronInfoData.brain_atlas }}</p>
                <p v-show="neuronInfoData.layer">
                  layer: {{ neuronInfoData.layer }}
                </p>
                <p v-show="neuronInfoData.hemisphere">
                  hemisphere: {{ neuronInfoData.hemisphere }}
                </p>
              </el-collapse-item>
              <el-collapse-item
                title="similar neurons"
                name="similarInfo"
              >
                <ul class="connect-item-list">
                  <li
                    v-for="(item, i) in neuronInfoData.simi_info"
                    :key="i"
                    class="connect-item"
                  >
                    <span class="connect-label">{{ item.type }} similar cells: {{ item.id_list.length }}</span>
                    <el-button
                      type="text"
                      :disabled="!item.id_list || item.id_list.length === 0"
                      @click="$emit('checkConnectedNeurons', item.id_list)"
                    >
                      View
                    </el-button>
                  </li>
                </ul>
              </el-collapse-item>
              <el-collapse-item
                title="nearby neurons"
                name="connectInfo"
              >
                <ul class="connect-item-list">
                  <li
                    v-for="(item, i) in neuronInfoData.conn_info"
                    :key="i"
                    class="connect-item"
                  >
                    <span class="connect-label">{{ item.type }} neighboring cells: {{ item.id_list.length }}</span>
                    <el-button
                      type="text"
                      :disabled="!item.id_list || item.id_list.length === 0"
                      @click="$emit('checkConnectedNeurons', item.id_list)"
                    >
                      View
                    </el-button>
                  </li>
                </ul>
              </el-collapse-item>
              <el-collapse-item
                title="morphology features"
                name="morphologyFeatures"
              >
                <MorphologyFeaturesTable
                  :morpho-info="neuronInfoData.morpho_info"
                  type="single"
                />
              </el-collapse-item>
              <el-collapse-item
                title="anatomy/projection info"
                name="projectionInfo"
              >
                <ProjectionInfoTable :proj-info="neuronInfoData.proj_info" />
              </el-collapse-item>
            </el-collapse>
          </section>
        </el-tab-pane>
        <el-tab-pane
          label="viewer property"
          name="viewer property"
        >
          <div>
            <el-collapse v-model="activeNames2">
              <el-collapse-item
                v-if="isUploadData"
                title="AIPOM data report"
                name="dataSummary"
              >
                <div class="summary-container">
                  <p><strong>Soma Region:</strong></p>
                  <ul>
                    <li>{{ somaRegion }}</li>
                  </ul>
                  <p><strong>Morphology Features:</strong></p>
                  <ul>
                    <li>
                      {{ morphologyFeature }}
                    </li>
                  </ul>
                  <p><strong>Projection:</strong></p>
                  <ul>
                    <li>{{ projectionInfo }}</li>
                  </ul>
                  <p><strong>Neurons in Same Brain Region:</strong></p>
                  <ul>
                    <li>{{ sameRegionInfo }}</li>
                  </ul>
                </div>
              </el-collapse-item>
              <el-collapse-item
                title="brain"
                name="brain"
              >
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                  <el-input
                    v-model="searchKeyword"
                    placeholder="brain regions"
                    style="width: 80%; margin-right: 10px;"
                    @keyup.enter.native="onSearch"
                  />
                  <el-button
                    type="primary"
                    @click="onSearch"
                  >
                    Search
                  </el-button>
                </div>
                <el-tree
                  ref="brainTree"
                  :data="neuronViewerData"
                  :render-after-expand="false"
                  show-checkbox
                  node-key="id"
                  :props="{ label: 'acronym' }"
                  :check-strictly="true"
                  :render-content="renderTreeNode"
                  @check-change="checkBrainTreeCallback"
                >
                  <template
                    slot-scope="{ node, data }"
                  >
                    <el-tooltip
                      effect="dark"
                      :content="data.name"
                      placement="right"
                    >
                      <span>{{ node.label }}</span>
                    </el-tooltip>
                  </template>
                </el-tree>
              </el-collapse-item>
              <el-collapse-item
                title="reconstruction"
                name="reconstruction"
              >
                <el-tree
                  v-if="neuronViewerReconstructionData.length"
                  ref="reconstructionTree"
                  :data="neuronViewerReconstructionData"
                  :render-after-expand="false"
                  show-checkbox
                  node-key="id"
                  :check-strictly="true"
                  :props="{ label: 'name' }"
                  @check-change="checkReconstructionTreeCallback"
                />
              </el-collapse-item>
              <el-collapse-item
                title="slice"
                name="slice"
              >
                <SliceSection
                  slice-name="Sagittal"
                  :max-value="sagittalMax"
                  :value-step="step"
                  :_switch-change="switchChange"
                  :_slider-change="sliderChange"
                />
                <SliceSection
                  slice-name="Axial"
                  :max-value="AxialMax"
                  :value-step="step"
                  :_switch-change="switchChange"
                  :_slider-change="sliderChange"
                />
                <SliceSection
                  slice-name="Coronal"
                  :max-value="coronalMax"
                  :value-step="step"
                  :_switch-change="switchChange"
                  :_slider-change="sliderChange"
                />
              </el-collapse-item>
              <el-collapse-item
                title="roi"
                name="roi"
              >
                <ROI
                  ref="ROI"
                  :_show-r-o-i="showROI"
                  :_hide-r-o-i="hideROI"
                  :_update-r-o-i-ball="updateROIBall"
                  @searchROINeurons="$emit('searchROINeurons', $event)"
                />
              </el-collapse-item>
              <!--              <el-collapse-item-->
              <!--                title="soma"-->
              <!--                name="soma"-->
              <!--              >-->
              <!--                <Soma-->
              <!--                  ref="Soma"-->
              <!--                  :_show-soma="showSoma"-->
              <!--                  :_hide-soma="hideSoma"-->
              <!--                  :_update-soma-ball="updateSomaBall"-->
              <!--                  @searchROINeurons="$emit('searchROINeurons', $event)"-->
              <!--                />-->
              <!--              </el-collapse-item>-->
            </el-collapse>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    <div class="separator" />
    <div class="right-side">
      <NeuronScene
        ref="neuronScene"
        @dblclick.native="handleDBClick"
        @contextmenu="handleRightClick"
        @neuronView="$emit('neuronView', $event)"
      />
    </div>
    <div class="right-bottom">
      <NeuronScene
        ref="dendriteScene"
      />
    </div>
    <el-button
      class="control-dendrite-scene-button"
      size="mini"
      @click="switchDendriteSceneZIndex"
    >
      {{ controlDendriteScene }}
    </el-button>
    <div class="left-bottom">
      <NeuronScene
        ref="apicalScene"
      />
    </div>
    <el-button
      class="control-apical-scene-button"
      size="mini"
      @click="switchApicalSceneZIndex"
    >
      {{ controlApicalScene }}
    </el-button>
    <div class="right-top">
      <el-button
        size="mini"
        @click="opSoma"
      >
        {{ ifSoma }}
      </el-button>
      <!--      <el-button-->
      <!--        v-show="neuronInfoData.id"-->
      <!--        icon="el-icon-search"-->
      <!--        size="mini"-->
      <!--        @click="searchSimilarNeurons"-->
      <!--      >-->
      <!--        Search similar neurons-->
      <!--      </el-button>-->
      <el-button
        v-show="neuronInfoData.id"
        icon="el-icon-download"
        size="mini"
        :loading="downloading"
        @click="downloadData"
      >
        Download
      </el-button>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Ref, Vue, Watch } from 'vue-property-decorator'
import MorphologyFeaturesTable from '@/components/mouse/MorphologyFeaturesTable.vue'
import ProjectionInfoTable from '@/components/mouse/ProjectionInfoTable.vue'
import { downloadLink, sleep } from '@/utils/util'
import JSZip from 'jszip'
import NeuronScene from '@/components/mouse/NeuronScene.vue'
import SliceSection from '@/components/mouse/SliceSection.vue'
import ROI from '@/components/mouse/ROI.vue'
import { showLoading, increaseLoadingCount, decreaseLoadingCount, LoadingZero } from '@/request/RequestWrapper'

import neuronViewerBaseDataFMost from './surf_tree_fmost.json'

// import neuronViewerBaseData from './surf_tree.json'
import neuronViewerBaseData from './surf_tree_ccf-me.json'
import Soma from '@/components/mouse/Soma.vue'
import ColorPicker from '@/components/mouse/ColorPicker.vue'
const rootId = neuronViewerBaseData[0].id
const rootIdFMost = neuronViewerBaseDataFMost[0].id

@Component<NeuronInfo>({
  mounted () {
    console.log('neuron info mounted')
    // if (this.$store.state.atlas === 'CCFv3') {
    //   this.neuronViewerData = neuronViewerBaseData
    //   this.rootId = rootId
    // } else {
    //   this.neuronViewerData = neuronViewerBaseDataFMost
    //   this.rootId = rootIdFMost
    // }
    // this.$nextTick()
    this.loadRootComponent()
    this.dendriteScene.ThreeViewer = false
    this.dendriteScene.switchZIndex()
    this.apicalScene.ThreeViewer = false
    this.apicalScene.switchZIndex()
    // this.showSoma(100)
  },
  components: {
    Soma,
    MorphologyFeaturesTable,
    ProjectionInfoTable,
    NeuronScene,
    SliceSection,
    ROI
  }
})
export default class NeuronInfo extends Vue {
  @Ref('neuronScene') neuronScene!: NeuronScene
  @Ref('dendriteScene') dendriteScene!: NeuronScene
  @Ref('apicalScene') apicalScene!: NeuronScene
  @Ref('ROI') ROI!: ROI
  @Ref('Soma') Soma!: Soma
  @Ref('brainTree') brainTree!: any
  public neuronViewerReconstructionData: any = []
  public neuronViewerData: any = this.$store.state.atlas === 'CCFv3' ? neuronViewerBaseData : neuronViewerBaseDataFMost // neuronViewerBaseData
  private rootId: number = this.$store.state.atlas === 'CCFv3' ? rootId : rootIdFMost // rootId
  private activeNames2: any = ['brain', 'dataSummary']
  private sagittalMax: number = 11375 // 18.20
  private AxialMax: number = 7975 // 12.76
  private coronalMax: number = 13175 // 21.08
  private step: number = 25
  public neuronInfoData: any = {}
  private activeNames1: any = ['basicInfo']
  private downloading: boolean = false
  public selectedTab: string = 'viewer property'
  private controlDendriteScene = 'show basal viewer'
  private controlApicalScene = 'show apical viewer'
  private lastSomaPosition:[number, number, number] = [0, 0, 0]
  public roiShown:boolean = false
  public somaShown:boolean = false
  private ifSoma: string = 'Hide Soma Area'
  private somaX: number = 100
  private somaY: number = 100
  private somaZ: number = 100
  private somaR: number = 100
  public sliceAtlas:string = this.$store.state.atlas
  public isUploadData:boolean = false
  private somaRegion: string = ''
  private morphologyFeature: string = ''
  private projectionInfo: string = ''
  private sameRegionInfo:string = ''
  public searchKeyword: string = ''
  public filteredData: any = this.neuronViewerData
  public checkedNodes: [] = [] // 用于保存已选中的节点

  onSearch () {
    const keyword = this.searchKeyword.toLowerCase()
    this.checkedNodes = this.brainTree.getCheckedNodes() // 保存当前选中的节点

    if (keyword) {
      // 遍历节点以匹配关键字并展开相应节点
      this.expandToMatch(this.neuronViewerData, keyword)
    } else {
      // 如果关键字为空，不做处理
      this.collapseAllNodes() // 清空检索条件时，收起所有节点
    }

    this.$nextTick(() => {
      this.restoreCheckedNodes(this.checkedNodes) // 恢复选中状态
      this.selectRootNode() // 确保根节点始终选中
    })
  }

  collapseAllNodes () {
    const nodes = this.brainTree.getNodes()
    nodes.forEach((node: { id: any }) => {
      const treeNode = this.brainTree.getNode(node.id)
      if (treeNode) {
        treeNode.expanded = false
      }
    })
  }

  expandToMatch (nodes: any[], keyword: string) {
    nodes.forEach(node => {
      const treeNode = this.brainTree.getNode(node.id)
      if (treeNode) {
        if (node.acronym.toLowerCase().includes(keyword) || node.name.toLowerCase().includes(keyword)) {
          treeNode.expanded = false // 展开到匹配的节点，但不展开其子节点
          this.expandParentNodes(node.id) // 展开父节点
        } else {
          treeNode.expanded = false // 收起不匹配的节点
        }
      }
      if (!treeNode.expanded && node.children) {
        this.expandToMatch(node.children, keyword) // 继续递归匹配
      }
    })
  }

  expandParentNodes (nodeId: any) {
    let currentNode = this.brainTree.getNode(nodeId)
    while (currentNode && currentNode.parent) {
      const parentNode = this.brainTree.getNode(currentNode.parent.data.id)
      if (parentNode) {
        parentNode.expanded = true // 展开父节点
      }
      currentNode = currentNode.parent
    }
  }

  selectRootNode () {
    const rootNode = this.brainTree.getNode(this.neuronViewerData[0].id)
    if (rootNode) {
      this.brainTree.setChecked(rootNode.data.id, true, true) // 确保根节点选中
    }
  }

  restoreCheckedNodes (checkedNodes: any[]) {
    checkedNodes.forEach(node => {
      this.brainTree.setChecked(node.id, true, true) // 恢复选中状态
    })
  }

  renderTreeNode (createElement: any, { node, data }: any) {
    return createElement('span', {
      style: {
        display: 'flex',
        alignItems: 'center'
      },
      on: {
        click: (event: MouseEvent) => {
          event.stopPropagation() // 阻止父容器的点击事件冒泡
        }
      }
    }, [
      // 在节点前面加上颜色选择器，并调整大小和样式
      createElement(ColorPicker, {
        ref: 'colorPicker_' + data.id, // 为每个节点的颜色选择器设置一个唯一的 ref
        style: {
          marginRight: '8px', // 设置与文字的间距
          pointerEvents: 'auto' // 确保颜色选择器可以捕获点击事件
        },
        on: {
          'color-selected': (color: string) => this.neuronScene.updateVtkColor(data.id, this.hexToRgb(color)),
          'mousedown': (event: MouseEvent) => {
            event.stopPropagation() // 阻止 mousedown 事件的冒泡
          },
          'click': (event: MouseEvent) => {
            event.stopPropagation() // 阻止 click 事件的冒泡
          }
        },
        hook: {
          insert: (vnode: { componentInstance: any }) => {
            const colorPicker = vnode.componentInstance as any
            colorPicker.updateSize(25, 25) // 调整大小为 25x25 px
            colorPicker.setColor(this.rgbToHex([data.rgb_triplet[0], data.rgb_triplet[1], data.rgb_triplet[2]]))
          }
        }
      }),
      // 渲染节点的标签
      createElement('span', {
        style: {
          pointerEvents: 'none' // 禁止标签文本部分处理点击事件
        }
      }, node.label)
    ])
  }

  hexToRgb (hex: string): [number, number, number] {
    const bigint = parseInt(hex.slice(1), 16)
    const r = (bigint >> 16) & 255
    const g = (bigint >> 8) & 255
    const b = bigint & 255
    return [r, g, b]
  }

  rgbToHex (rgb: any[]) {
    console.log(`#${rgb.map(x => x.toString(16).padStart(2, '0')).join('')}`)
    return `#${rgb.map(x => x.toString(16).padStart(2, '0')).join('')}`
  }
  private opSoma () {
    if (this.ifSoma === 'Show Soma Area') {
      this.showSoma(this.somaR)
      this.ifSoma = 'Hide Soma Area'
    } else {
      this.hideSoma()
      this.ifSoma = 'Show Soma Area'
    }
  }
  /**
   * 下载 neuron info json, 轮播图片
   * @private
   */
  private async downloadData () {
    this.downloading = true
    await sleep(100) // 先让 loading 动起来
    const zip = new JSZip()
    const folder = zip.folder('neuron_info')
    try {
      // 左侧的信息 json
      // @ts-ignore
      folder.file('neuronInfoData.json', JSON.stringify(this.neuronInfoData))
      // 轮播图片
      let loadImgPromisesList = []
      let imgNames: string[] = []
      for (let i = 0; i < this.neuronInfoData.img_src.length; i++) {
        let imgSlides = this.neuronInfoData.img_src[i]
        for (let j = 0; j < imgSlides.slides.length; j++) {
          let imgItem = imgSlides.slides[j]
          loadImgPromisesList.push(fetch(imgItem.src).then(res => res.blob()))
          imgNames.push(`${imgSlides.title}_${imgItem.view}.png`)
        }
      }
      const imgBlobs = await Promise.all(loadImgPromisesList)
      imgBlobs.forEach((blob: Blob, i: number) => {
        folder!.file(imgNames[i], blob)
      })
      const zipBlob = await zip.generateAsync({ type: 'blob' })
      const url = URL.createObjectURL(zipBlob)
      await downloadLink(url, 'neuron_info.zip')
      URL.revokeObjectURL(url)
    } catch (e) {
      console.warn(e)
    }
    this.downloading = false
  }

  /**
   * 脑区el-tree节点状态改变的回调函数
   * @param data 节点数据
   * @param checked 节点是否被选中
   * @private
   */
  private async checkBrainTreeCallback (data: any, checked: boolean) {
    console.log(data)
    if (data.hasOwnProperty('src')) {
      if (checked) {
        if (this.neuronScene.checkLoadComponent(data)) {
          this.neuronScene.setComponentVisible(data, true)
        } else {
          // @ts-ignore
          let node = this.$refs.brainTree.getNode(data.id)
          node.loading = true
          let loadingInstance = showLoading(document.body)
          increaseLoadingCount()
          await this.neuronScene.loadComponent(data)
          node.loading = false
          decreaseLoadingCount()
          if (LoadingZero()) {
            loadingInstance.close()
          }
        }
      } else {
        this.neuronScene.setComponentVisible(data, false)
      }
    }
  }

  /**
   * reconstruction的el-tree节点状态改变的回调函数，当选中父节点时，不默认把soma region的节点选中
   * @param data 节点数据
   * @param checked 节点是否被选中
   * @private
   */
  private async checkReconstructionTreeCallback (data: any, checked: boolean) {
    console.log(data)
    if (data.hasOwnProperty('src')) {
      if (checked) {
        if (this.neuronScene.checkLoadComponent(data)) {
          this.neuronScene.setComponentVisible(data, true)
        } else {
          // @ts-ignore
          let node = this.$refs.reconstructionTree.getNode(data.id)
          // NeuronInfo.setLoadingForNode(node, true)
          let loadingInstance = showLoading(document.body)
          // increaseLoadingCount()
          await this.neuronScene.loadComponent(data)
          NeuronInfo.setLoadingForNode(node, false)
          // decreaseLoadingCount()
          if (LoadingZero()) {
            loadingInstance.close()
          }
          if (data.id === -1) {
            await this.dendriteScene.loadDendrite(data)
          }
          if (data.id === -4) {
            await this.apicalScene.loadDendrite(data)
          }
        }
      } else {
        this.neuronScene.setComponentVisible(data, false)
      }
    }
    if (data.hasOwnProperty('children')) {
      for (let child of data.children) {
        console.log('checkReconstructionTreeCallback')
        console.log(child)
        if (!child.disabled && (!child.hasOwnProperty('brain_region_id') || !checked)) {
          // @ts-ignore
          this.$refs.reconstructionTree.setChecked(child.id, checked)
        }
      }
    }
    this.checkRegion(data, checked)
  }

  /**
   * 控制某个脑区显示或隐藏
   * @param data 节点数据
   * @param checked 节点是否被选中
   * @private
   */
  private checkRegion (data: any, checked: boolean) {
    if (data.hasOwnProperty('brain_region_id')) {
      const brainRegionId = data.brain_region_id[0]
      // @ts-ignore
      this.$refs.brainTree.setChecked(brainRegionId, checked)
    }
  }

  /**
   * 设置el-tree的某个节点以及其祖先节点是否加载的状态
   * @param node 节点
   * @param isLoading 是否加载中
   * @private
   */
  private static setLoadingForNode (node: any, isLoading: boolean) {
    node.loading = isLoading
    while (node.parent) {
      node.parent.loading = isLoading
      node = node.parent
    }
  }

  /**
   * 将el-tree的某个节点的祖先节点都设置为展开
   * @param node 节点
   * @private
   */
  private static expandNode (node: any) {
    while (node.parent) {
      node.parent.expanded = true
      node = node.parent
    }
  }

  /**
   * 改变switch的回调函数，用于决定slice是否显示
   * @param isSwitch 是否显示slice
   * @param sliceName SLice的方向名称
   */
  public switchChange (isSwitch: boolean, sliceName: string) {
    if (isSwitch) {
      if (this.neuronScene.checkLoadSlice(sliceName)) {
        this.neuronScene.setSliceVisible(sliceName, true)
      } else {
        this.neuronScene.loadSlice(sliceName, this.sliceAtlas)
      }
    } else {
      this.neuronScene.setSliceVisible(sliceName, false)
    }
  }

  /**
   * 改变滑动条的回调函数，用于切换slice的位置
   * @param value slice的位置
   * @param sliceName SLice的方向名称
   */
  public sliderChange (value: number, sliceName: string) {
    this.neuronScene.updateSlice(sliceName, Math.round(value / 25), this.sliceAtlas)
  }

  /**
   * 加载脑区的root组件
   * @private
   */
  private loadRootComponent () {
    // @ts-ignore
    let rootNode = this.$refs.brainTree.getNode(this.rootId)
    rootNode.expanded = true
    // @ts-ignore
    this.$refs.brainTree.setChecked(this.rootId, true)
  }

  /**
   * 鼠标双击的回调函数，用于highlight渲染的组件，并显示出该组件的名字
   * @event 鼠标事件
   */
  private handleDBClick (event: any) {
    event.preventDefault()
    let p = this.neuronScene.handleMouseDoubleClick(event)
    // let q = this.neuronScene.handleMouseDoubleClickNeuron(event)
    this.ROI.setROI(Math.round(p[0]), Math.round(p[1]), Math.round(p[2]))
  }

  /**
     * 鼠标双击的回调函数，用于highlight渲染的组件，并显示出该组件的名字
     * @event 鼠标事件
     */
  private handleRightClick (event: any) {
    console.log('handleRightClick')
    event.preventDefault()
    this.neuronScene.handleMouseRightClick(event)
  }

  /**
   * 收起或展开渲染dendrite的场景
   * @private
   */
  private switchDendriteSceneZIndex () {
    if (this.controlDendriteScene === 'show basal viewer') {
      this.controlDendriteScene = 'hide basal viewer'
    } else {
      this.controlDendriteScene = 'show basal viewer'
    }
    this.dendriteScene.switchZIndex()
  }

  private switchApicalSceneZIndex () {
    if (this.controlApicalScene === 'show apical viewer') {
      this.controlApicalScene = 'hide apical viewer'
    } else {
      this.controlApicalScene = 'show apical viewer'
    }
    this.apicalScene.switchZIndex()
  }

  /**
   * 将reconstructionTree对应的树形控件全部取消选中
   */
  public clearReconstruction () {
    if (this.neuronViewerReconstructionData.length !== 0) {
      // @ts-ignore
      this.$refs.reconstructionTree.setCheckedKeys([])
    }
  }

  /**
   * 更新神经元的三维可视化，默认加载神经元的dendrite和axon
   * @param needClear 是否需要清除之前的神经元
   */
  public async updateReconstruction (needClear: boolean) {
    if (needClear) {
      this.neuronScene.unloadAllNeuron()
      this.dendriteScene.unloadAllNeuron()
      this.apicalScene.unloadAllNeuron()
    }
    console.log('cleared')
    if (this.activeNames2.indexOf('reconstruction') === -1) {
      this.activeNames2.push('reconstruction')
    }
    await this.$nextTick()
    // @ts-ignore
    let reconstructionRootNode = this.$refs.reconstructionTree.getNode(this.neuronViewerReconstructionData[0].id)
    reconstructionRootNode.expanded = true
    await this.$nextTick()
    // @ts-ignore
    this.$refs.reconstructionTree.setCheckedKeys(this.neuronViewerReconstructionData[0].visible_keys)
  }

  /**
   * 显示代表ROI的小球
   * @param r ROI的半径
   * @private
   */
  private showROI (r: number) {
    this.roiShown = true
    const roiInitialPosition = this.neuronScene.showROIBall(r)
    // if (roiInitialPosition) {
    //   this.ROI.setROI(Math.round(roiInitialPosition[0]), Math.round(roiInitialPosition[1]), Math.round(roiInitialPosition[2]))
    // }
    if (roiInitialPosition || (this.lastSomaPosition[0] !== this.neuronInfoData.soma[0] || this.lastSomaPosition[1] !== this.neuronInfoData.soma[1] || this.lastSomaPosition[2] !== this.neuronInfoData.soma[2])) {
      this.lastSomaPosition = this.neuronInfoData.soma
      this.ROI.setROI(Math.round(this.neuronInfoData.soma[0]), Math.round(this.neuronInfoData.soma[1]), Math.round(this.neuronInfoData.soma[2]))
    }
  }

  public showSoma (r: number) {
    const somaInitialPosition = this.neuronScene.showSomaBall(100)
    // if (roiInitialPosition) {
    //   this.ROI.setROI(Math.round(roiInitialPosition[0]), Math.round(roiInitialPosition[1]), Math.round(roiInitialPosition[2]))
    // }
    if (somaInitialPosition || (this.lastSomaPosition[0] !== Number(this.neuronInfoData.soma[0]) || this.lastSomaPosition[1] !== Number(this.neuronInfoData.soma[1]) || this.lastSomaPosition[2] !== Number(this.neuronInfoData.soma[2]))) {
      this.lastSomaPosition = this.neuronInfoData.soma
      this.updateSomaBall(Math.round(this.neuronInfoData.soma[0]), Math.round(this.neuronInfoData.soma[1]), Math.round(this.neuronInfoData.soma[2]), 100)
    }
    console.log('this.neuronInfoData.soma')
    console.log(this.neuronInfoData.soma)
    this.somaShown = true
    this.ifSoma = 'Hide Soma Area'
  }

  /**
   * 隐藏代表ROI的小球
   * @private
   */
  private hideROI () {
    this.roiShown = false
    this.neuronScene.setROIBallVisible(false)
  }

  public hideSoma () {
    this.somaShown = false
    this.ifSoma = 'Show Soma Area'
    this.neuronScene.setSomaBallVisible(false)
  }

  /**
   * 更新代表ROI的小球
   * @param x ROI在标准脑坐标系下的x坐标
   * @param y ROI在标准脑坐标系下的y坐标
   * @param z ROI在标准脑坐标系下的z坐标
   * @param r ROI的半径
   * @private
   */
  private updateROIBall (x: number, y: number, z: number, r: number) {
    this.neuronScene.updateROIBall(x, y, z, r)
  }

  private updateSomaBall (x: number, y: number, z: number, r: number) {
    this.neuronScene.updateSomaBall(x, y, z, r)
  }

  /**
   * 搜索当前神经元相似神经元
   * @private
   */
  private searchSimilarNeurons () {
    let neuronInfo = {
      'morpho_info': this.neuronInfoData.morpho_info,
      'celltype': this.neuronInfoData.celltype,
      'brain_atlas': this.neuronInfoData.brain_atlas
    }
    console.log(neuronInfo)
    this.$emit('searchSimilarNeurons', neuronInfo)
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.neuron-info-container {
  height: 100%;
  color: black;
  display: flex;
  flex-flow: row nowrap;
  border-radius: 5px;
  position: relative;
  .left-side, .right-side {
    height: 100%;
    overflow: auto;
    padding: 10px;
  }
  .separator {
    width: 1px;
    height: 100%;
    background-color: lightgrey;
  }
  .left-side {
    width: 360px;
    .el-tabs {
      height: 100%;
      .el-tab-pane {
        overflow: auto;
        .feature-desc {
          .connect-item-list {
            .connect-item {
              display: flex;
              flex-flow: row nowrap;
              justify-content: space-between;
              align-items: center;
            }
          }
        }
      }
    }
  }
  .right-side {
    flex: 1;
  }
  .right-top {
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 1;
  }
  .right-bottom {
    position: absolute;
    width: 360px;
    height: 360px;
    bottom: 10px;
    right: 10px;
  }
  .left-bottom {
    position: absolute;
    width: 360px;
    height: 360px;
    bottom: 10px;
    left: 370px;
  }
  .control-dendrite-scene-button {
    position: absolute;
    bottom: 370px;
    right: 10px;
    z-index: 2;
  }
  .control-apical-scene-button {
    position: absolute;
    bottom: 370px;
    left: 370px;
    z-index: 2;
  }
}
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
</style>
