<template>
  <div class="neuron-detail-tabs">
    <el-tabs
      v-model="selectedTab"
      type="border-card"
      :stretch="true"
      class="full-height"
      @tab-click="tabClickHandler"
    >
      <el-tab-pane
        label="Full"
        name="fullMorph"
        :lazy="true"
      >
        <NeuronList
          ref="neuronList"
          @checkNeuronLists="checkNeuronLists"
          @viewNeuronsHandlerLists="viewNeuronsHandlerLists"
          @neuronViewHandlerLists="updateNeuronAnalysis"
          @neuronAnalysisLists="updateNeuronAnalysisLists"
        />
      </el-tab-pane>
      <el-tab-pane
        label="Local"
        name="localMorph"
        :lazy="true"
      >
        <NeuronListLocal
          ref="neuronListLocal"
          @checkNeuronLists="checkNeuronLists"
          @viewNeuronsHandlerLists="viewNeuronsHandlerLists"
          @neuronViewHandlerLists="updateNeuronAnalysis"
          @neuronAnalysisLists="updateNeuronAnalysisLists"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Ref, Prop } from 'vue-property-decorator'
import { ElTabPane } from 'element-ui/types/tab-pane'
import NeuronList from '@/components/mouse/NeuronList.vue'
import NeuronListLocal from '@/components/mouse/NeuronListLocal.vue'

@Component({
  components: { NeuronListLocal, NeuronList }
})
export default class NeuronLists extends Vue {
  @Ref('neuronList') readonly neuronList!: NeuronList
  @Ref('neuronListLocal') readonly neuronListLocal!: NeuronListLocal
  public selectedTab: string = 'fullMorph'
  private async tabClickHandler (tab: ElTabPane) {
    if (tab.name === 'fullMorph') {
      console.log(this.selectedTab)
      this.$emit('switchLocalAndFull', 'fullMorph')
    } else {
      this.$emit('switchLocalAndFull', 'localMorph')
    }
  }

  private checkNeuronLists (neuronDetail: any) {
    console.log('checkNeuronLists')
    this.$emit('checkNeuron', neuronDetail)
  }
  private switchRecDegree () {
    console.log(this.selectedTab)
    this.$emit('switchLocalAndFull', this.selectedTab)
  }

  public setRecDegree (recDegree: string) {
    this.selectedTab = recDegree
  }

  private viewNeuronsHandlerLists () {
    this.$emit('viewNeurons')
  }

  private updateNeuronAnalysis (neuronDetail: any) {
    this.$emit('neuronView', neuronDetail)
  }

  private updateNeuronAnalysisLists (neuronIds: string[]) {
    this.$emit('neuronAnalysis', neuronIds)
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
