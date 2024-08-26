<template>
  <div class="neuron-viewer-container">
    <div class="left-side">
      <el-collapse v-model="activeNames">
        <el-collapse-item
          title="Brain"
          name="brain"
        >
          <el-tree
            ref="brainTree"
            :data="neuronViewerData"
            show-checkbox
            node-key="id"
            :props="{ label: 'acronym' }"
            :check-strictly="true"
            @check-change="checkCallback"
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
          title="Reconstruction"
          name="reconstruction"
        >
          <el-tree
            v-if="neuronViewerReconstructionData.length"
            ref="reconstructionTree"
            :data="neuronViewerReconstructionData"
            show-checkbox
            node-key="id"
            :props="{ label: 'name' }"
            @check-change="checkCallback"
          />
        </el-collapse-item>
        <el-collapse-item
          title="Slice"
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
      </el-collapse>
    </div>
    <div class="separator-vertical" />
    <div class="right-side">
      <NeuronScene
        ref="neuronScene"
        @dblclick.native="handleDBClick"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch, Ref } from 'vue-property-decorator'
import NeuronScene from '@/components/mouse/NeuronScene.vue'
import SliceSection from '@/components/mouse/SliceSection.vue'

import neuronViewerBaseData from './surf_tree_ccf-me.json'
const rootId = neuronViewerBaseData[0].id

@Component<NeuronViewer>({
  mounted () {
    this.loadRootComponent()
  },
  components: {
    NeuronScene,
    SliceSection
  }
})

export default class NeuronViewer extends Vue {
  @Ref('neuronScene') neuronScene!: NeuronScene
  public neuronViewerReconstructionData: any = []
  public neuronViewerData: any = neuronViewerBaseData
  private rootId: number = rootId
  private activeNames: any = ['brain']
  private sagittalMax: number = 18.20
  private AxialMax: number = 12.76
  private coronalMax: number = 21.08
  private step: number = 0.04
  private sliceAtlas: any = this.$store.state.atlas

  /**
   * el-tree节点状态改变的回调函数
   * @param data 节点数据
   * @param checked 节点是否被选中
   * @private
   */
  private async checkCallback (data: any, checked: boolean) {
    if (data.hasOwnProperty('src')) {
      if (checked) {
        if (this.neuronScene.checkLoadComponent(data)) {
          this.neuronScene.setComponentVisible(data, true)
        } else {
          // @ts-ignore
          let node = this.neuronScene.ifNeuron(data) ? this.$refs.reconstructionTree.getNode(data.id) : this.$refs.brainTree.getNode(data.id)
          node.loading = true
          await this.neuronScene.loadComponent(data)
          node.loading = false
        }
      } else {
        this.neuronScene.setComponentVisible(data, false)
      }
    }
    await this.checkRegion(data, checked)
  }

  /**
   * 控制某个脑区显示或隐藏
   * @param data 节点数据
   * @param checked 节点是否被选中
   * @private
   */
  private async checkRegion (data: any, checked: boolean) {
    if (data.hasOwnProperty('brain_region_id')) {
      const brainRegionId = data.brain_region_id[0]
      // @ts-ignore
      let regionNode = this.$refs.brainTree.getNode(brainRegionId)
      NeuronViewer.expandNode(regionNode)
      await this.$nextTick()
      // @ts-ignore
      this.$refs.brainTree.setChecked(brainRegionId, checked)
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
    this.neuronScene.updateSlice(sliceName, Math.round(value * 25), this.sliceAtlas)
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
    this.neuronScene.handleMouseDoubleClick(event)
  }

  @Watch('neuronViewerReconstructionData', {
    deep: true
  })
  public async neuronViewerReconstructionDataChange (newValue: any, oldValue: any) {
    if (oldValue.length !== 0 && oldValue[0].name === newValue[0].name) {
      await this.$nextTick()
      // @ts-ignore
      let reconstructionRootNode = this.$refs.reconstructionTree.getNode(newValue[0].id)
      reconstructionRootNode.expanded = true
      return
    }
    if (oldValue.length !== 0) {
      // @ts-ignore
      this.$refs.reconstructionTree.setCheckedKeys([])
      await this.$nextTick()
      this.neuronScene.unloadAllNeuron()
    }
    if (this.activeNames.indexOf('reconstruction') === -1) {
      this.activeNames.push('reconstruction')
    }
    await this.$nextTick()
    // @ts-ignore
    let reconstructionRootNode = this.$refs.reconstructionTree.getNode(newValue[0].id)
    reconstructionRootNode.expanded = true
    await this.$nextTick()
    // @ts-ignore
    this.$refs.reconstructionTree.setCheckedKeys(newValue[0].visible_keys)
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.neuron-viewer-container {
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
  .separator-horizon {
    width: 100%;
    height: 1px;
    background-color: lightgrey;
  }
  .separator-vertical {
    width: 1px;
    height: 100%;
    background-color: lightgrey;
  }
  .left-side {
    width: 360px;
  }
  .right-side {
    flex: 1;
  }
}
</style>
