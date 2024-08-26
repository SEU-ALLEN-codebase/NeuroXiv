<template>
  <div>
    <el-button
      class="el-button-op-roi"
      @click="opROI"
    >
      {{ ifROI }}
    </el-button>
    <div v-if="ifROI === 'Hide ROI'">
      <div class="roi-parameter">
        <p class="roi-text">
          r (μm)
        </p>
        <el-input-number
          v-model="roiR"
          class="roi-parameter-input"
          size="mini"
          :step="25"
          step-strictly
        />
      </div>
      <div class="roi-parameter">
        <p
          class="roi-text"
          style="color: red"
        >
          x (μm)
        </p>
        <el-input-number
          v-model="roiX"
          class="roi-parameter-input"
          size="mini"
          step-strictly
        />
      </div>
      <div class="roi-parameter">
        <p
          class="roi-text"
          style="color: mediumspringgreen"
        >
          y (μm)
        </p>
        <el-input-number
          v-model="roiY"
          class="roi-parameter-input"
          size="mini"
          step-strictly
        />
      </div>
      <div class="roi-parameter">
        <p
          class="roi-text"
          style="color: mediumblue"
        >
          z (μm)
        </p>
        <el-input-number
          v-model="roiZ"
          class="roi-parameter-input"
          size="mini"
          step-strictly
        />
      </div>
      <div
        class="div-op-roi"
      >
        <el-button
          type="text"
          size="medium"
          icon="el-icon-refresh"
          @click="updateROI"
        >
          Update
        </el-button>
        <el-button
          type="text"
          size="medium"
          icon="el-icon-search"
          @click="searchROINeurons"
        >
          Search Neurons Inside
        </el-button>
        <p
          class="roi-tip"
        >
          double left-click in 3D view to move ROI
        </p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator'

@Component<ROI>({
  mounted () {}
})

export default class ROI extends Vue {
  @Prop({ required: true }) _showROI!: any
  @Prop({ required: true }) _hideROI!: any
  @Prop({ required: true }) _updateROIBall!: any
  private ifROI: string = 'Show ROI'
  private roiX: number = 0
  private roiY: number = 0
  private roiZ: number = 0
  private roiR: number = 500

  /**
   * 展示或隐藏ROI小球
   * @private
   */
  private opROI () {
    if (this.ifROI === 'Show ROI') {
      this._showROI(this.roiR)
      this.ifROI = 'Hide ROI'
    } else {
      this._hideROI()
      this.ifROI = 'Show ROI'
    }
  }

  /**
   * 更新ROI的位置或者半径
   * @private
   */
  private updateROI () {
    this._updateROIBall(this.roiX, this.roiY, this.roiZ, this.roiR)
  }

  /**
   * 设置ROI的位置
   * @param x ROI在标准脑坐标系下的x坐标
   * @param y ROI在标准脑坐标系下的y坐标
   * @param z ROI在标准脑坐标系下的z坐标
   */
  public setROI (x: number, y: number, z: number) {
    this.roiX = x
    this.roiY = y
    this.roiZ = z
    this.updateROI()
  }

  /**
   * 搜索ROI中的神经元
   * @private
   */
  private searchROINeurons () {
    this.updateROI()
    let roiParameter = this.roiX + '_' + this.roiY + '_' + this.roiZ + '_' + this.roiR
    this.$emit('searchROINeurons', roiParameter)
  }
}
</script>

<style scoped lang="less">
.el-button-op-roi {
  margin-bottom: 20px;
}
.roi-parameter {
  display: flex;
  margin-bottom: 20px;
  .roi-text {
    margin: 0;
    height: 28px;
    line-height: 28px;
  }
  .roi-parameter-input {
    margin-left: 20px;
  }
}
.roi-tip {
  color: gray;
  font-size: smaller;
}
</style>
