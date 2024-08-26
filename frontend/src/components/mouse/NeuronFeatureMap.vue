<template>
  <div class="multi-neurons-viewer-container">
    <div class="right-side">
      <NeuronScene
        ref="neuronScene"
        @neuronView="$emit('neuronView', $event)"
      />
    </div>
    <div class="right-top">
      <el-button
        icon="el-icon-download"
        size="mini"
        @click="loadOBJFile"
      >
        Download
      </el-button>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Ref, Vue } from 'vue-property-decorator'
import NeuronScene from '@/components/mouse/NeuronScene.vue'
import SliceSection from '@/components/mouse/SliceSection.vue'
import ROI from '@/components/mouse/ROI.vue'

import neuronViewerBaseData from './surf_tree_ccf-me.json'
import neuronViewerBaseDataFMost from './surf_tree_fmost.json'
const rootId = neuronViewerBaseData[0].id
const rootIdFMost = neuronViewerBaseDataFMost[0].id

@Component<NeuronFeatureMap>({
  mounted () {
  },
  components: {
    NeuronScene,
    SliceSection,
    ROI
  }
})
export default class NeuronFeatureMap extends Vue {
    @Ref('neuronScene') neuronScene!: NeuronScene
    // mounted () {
    // // 调用 loadOBJFile 方法加载 OBJ 文件
    //   this.loadOBJFile('./soma_density.obj')
    // }

    // 方法：使用 NeuronScene 的 loadobj 方法加载 OBJ 文件
    public async loadOBJFile (objFilePath: string) {
      console.log('load obj')
      await this.neuronScene.loadPointObj('./test.obj')
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
