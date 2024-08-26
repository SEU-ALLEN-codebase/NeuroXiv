<template>
  <div class="neuron-detail-tabs">
    <el-tabs
      v-model="selectedTab"
      type="border-card"
      :stretch="true"
      class="full-height"
      @tab-click="tabClickHandler"
    >
      <!--      <el-tab-pane-->
      <!--        label="Neurons Map"-->
      <!--        name="neuronFeatureMap"-->
      <!--        :lazy="true"-->
      <!--      >-->
      <!--        <NeuronFeatureMap ref="neuronFeatureMap" />-->
      <!--      </el-tab-pane>-->
      <el-tab-pane
        label="Neurons viewer"
        name="multiNeuronsViewer"
        :lazy="true"
      >
        <MultiNeuronsViewer
          ref="multiNeuronsViewer"
          @searchROINeurons="$emit('searchROINeurons', $event)"
          @neuronView="$emit('neuronView', $event)"
          @setVisualizedAxon="$emit('setVisualizedAxon')"
          @setVisualizedBasal="$emit('setVisualizedBasal')"
          @setVisualizedApical="$emit('setVisualizedApical')"
          @setVisualizedSoma="$emit('setVisualizedSoma')"
        />
      </el-tab-pane>
      <el-tab-pane
        label="Neurons analysis"
        name="neuronStates"
      >
        <NeuronStates
          ref="neuronStates"
          :neurons-list="neuronsList"
        />
      </el-tab-pane>
      <el-tab-pane
        label="Single neuron info"
        name="neuronInfo"
        :lazy="true"
      >
        <NeuronInfo
          ref="neuronInfo"
          @checkConnectedNeurons="$emit('checkConnectedNeurons', $event)"
          @searchSimilarNeurons="$emit('searchSimilarNeurons', $event)"
          @searchROINeurons="$emit('searchROINeurons', $event)"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Ref, Prop } from 'vue-property-decorator'
import NeuronStates from '@/components/mouse/NeuronStates.vue'
import NeuronInfo from '@/components/mouse/NeuronInfo.vue'
import MultiNeuronsViewer from '@/components/mouse/MultiNeuronsViewer.vue'
import { ElTabPane } from 'element-ui/types/tab-pane'
import NeuronFeatureMap from '@/components/mouse/NeuronFeatureMap.vue'

@Component({
  components: { NeuronFeatureMap, NeuronInfo, NeuronStates, MultiNeuronsViewer }
})
export default class NeuronDetail extends Vue {
  @Ref('neuronFeatureMap') readonly neuronFeatureMap!: NeuronFeatureMap
  @Ref('neuronStates') readonly neuronStates!: NeuronStates
  @Ref('neuronInfo') readonly neuronInfo!: NeuronInfo
  @Ref('multiNeuronsViewer') readonly multiNeuronsViewer!: MultiNeuronsViewer
  @Prop({ required: true }) loadFirstNeuron!: any
  @Prop({ required: true }) readonly neuronsList!: any[]

  // 此处如果初始值不为neuronInfo,neuronInfo的scene不会被渲染
  public selectedTab: string = 'multiNeuronsViewer'

  /**
   * 点击切换 tab (通过改变变量的方式不会触发)
   * @param tab 当前选中的 tab
   * @private
   */
  private async tabClickHandler (tab: ElTabPane) {
    // 切换到 neuronInfo tab 的时候,如果没有神经元则加载神经元列表第一个神经元
    // 切换到 multiNeuronsViewer tab的时候，则将神经元列表勾选的神经元进行展示
    if (tab.name === 'neuronInfo') {
      await this.$nextTick()
      if (!this.neuronInfo.neuronInfoData.id) {
        this.loadFirstNeuron()
      }
    } else if (tab.name === 'multiNeuronsViewer') {
      this.$emit('viewNeurons')
    }
    // else if (tab.name === 'neuronStates') {
    //   this.$emit('checkConnectedNeurons')
    // }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.neuron-detail-tabs {
  height: 100%;
  .el-tabs {
    height: 100%;
  }
}
</style>
