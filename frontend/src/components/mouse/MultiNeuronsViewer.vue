<template>
  <div class="multi-neurons-viewer-container">
    <div class="left-side">
      <el-tabs
        v-model="selectedTab"
        :stretch="true"
        class="full-height"
      >
        <el-tab-pane
          label="viewer property"
          name="viewer property"
        >
          <div>
            <el-collapse v-model="activeNames">
              <el-collapse-item
                title="brain"
                name="brain"
              >
                <div style="display: flex; align-items: center; margin-bottom: 8px">
                  <el-input
                    v-model="searchKeyword"
                    placeholder="brain regions"
                    style="width: 100%; margin-right: 3px;padding: 0 6px 0 6px;"
                    @keyup.enter.native="onSearch"
                  />
                  <el-button
                    type="primary"
                    style="font-size: 12px;padding:11px 6px 11px 6px"
                    @click="onSearch"
                  >
                    Search
                  </el-button>
                </div>
                <el-tree
                  ref="brainTree"
                  :data="filteredData"
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
              <el-collapse-item
                title="visualized structures"
                name="visualized structures"
              >
                <el-checkbox
                  v-model="showAllSoma"
                  label="soma"
                  name="soma"
                  @change="setSoma"
                />
                <el-checkbox
                  v-model="showAllAxon"
                  label="axon"
                  name="axon"
                  @change="setAxon"
                />
                <el-checkbox
                  v-model="showAllBasal"
                  label="basal dendrite"
                  name="basal dendrite"
                  @change="setBasal"
                />
                <el-checkbox
                  v-model="showAllApical"
                  label="apical dendrite"
                  name="apical dendrite"
                  @change="setApical"
                />
              </el-collapse-item>
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
        @neuronView="$emit('neuronView', $event)"
      />
    </div>
    <div class="right-top">
      <el-button
        @click="Rotate"
      >
        Animation
      </el-button>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Ref, Vue } from 'vue-property-decorator'
import NeuronScene from '@/components/mouse/NeuronScene.vue'
import SliceSection from '@/components/mouse/SliceSection.vue'
import ROI from '@/components/mouse/ROI.vue'
import { showLoading, increaseLoadingCount, decreaseLoadingCount, LoadingZero } from '@/request/RequestWrapper'

import neuronViewerBaseData from './surf_tree_ccf-me.json'

import neuronViewerBaseDataFMost from './surf_tree_fmost.json'

import ColorPicker from './ColorPicker.vue'
const rootId = neuronViewerBaseData[0].id
const rootIdFMost = neuronViewerBaseDataFMost[0].id
const SliceAtlas = 'CCFv3'
const SliceAtlasfMOST = 'CCF-thin'

@Component<NeuronInfo>({
  mounted () {
    this.loadRootComponent()
    this.neuronScene.multiViewerSoma = new Map()
    this.neuronScene.multiViewerSomaPos = new Map()
  },
  components: {
    NeuronScene,
    SliceSection,
    ROI
  }
})
export default class NeuronInfo extends Vue {
  @Ref('neuronScene') neuronScene!: NeuronScene
  @Ref('ROI') ROI!: ROI
  @Ref('brainTree') brainTree!: any
  public neuronViewerData: any = this.$store.state.atlas === 'CCFv3' ? neuronViewerBaseData : neuronViewerBaseDataFMost // neuronViewerBaseData
  private rootId: number = this.$store.state.atlas === 'CCFv3' ? rootId : rootIdFMost // rootId
  private sliceAtlas: any = this.$store.state.atlas
  private activeNames: any = ['brain']
  private sagittalMax: number = 11375 // 18.20
  private AxialMax: number = 7975 // 12.76
  private coronalMax: number = 13175 // 21.08
  private step: number = 25
  public selectedTab: string = 'viewer property'
  public showAllSoma:boolean = false
  public showAllAxon:boolean = true
  public showAllBasal:boolean = true
  public showAllApical:boolean = true
  public searchKeyword: string = ''
  public filteredData: any = this.neuronViewerData
  public checkedNodes: [] = [] // 用于保存已选中的节点

  private Rotate () {
    this.neuronScene.toggleRotation()
  }

  private setAxon () {
    this.$emit('setVisualizedAxon')
  }
  private setBasal () {
    console.log('showAllBasal')
    this.$emit('setVisualizedBasal')
  }
  private setApical () {
    console.log('showAllApical')
    this.$emit('setVisualizedApical')
  }
  private setSoma () {
    console.log('showAllSoma')
    this.$emit('setVisualizedSoma')
  }
  /**
   * 脑区el-tree节点状态改变的回调函数
   * @param data 节点数据
   * @param checked 节点是否被选中
   * @private
   */
  private async checkBrainTreeCallback (data: any, checked: boolean) {
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
    this.$nextTick(() => {
      // @ts-ignore
      let rootNode = this.$refs.brainTree.getNode(this.rootId)
      rootNode.expanded = true
      // @ts-ignore
      this.$refs.brainTree.setChecked(this.rootId, true)
    })
  }

  /**
   * 鼠标双击的回调函数，用于highlight渲染的组件，并显示出该组件的名字
   * @event 鼠标事件
   */
  private handleDBClick (event: any) {
    event.preventDefault()
    let p = this.neuronScene.handleMouseDoubleClickNeuron(event)
    this.ROI.setROI(Math.round(p[0]), Math.round(p[1]), Math.round(p[2]))
  }

  /**
   * 显示代表ROI的小球
   * @param r ROI的半径
   * @private
   */
  private showROI (r: number) {
    const roiInitialPosition = this.neuronScene.showROIBall(r)
    if (roiInitialPosition) {
      this.ROI.setROI(Math.round(roiInitialPosition[0]), Math.round(roiInitialPosition[1]), Math.round(roiInitialPosition[2]))
    }
  }

  /**
   * 隐藏代表ROI的小球
   * @private
   */
  private hideROI () {
    this.neuronScene.setROIBallVisible(false)
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
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.multi-neurons-viewer-container {
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
}
</style>
