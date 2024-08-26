<template>
  <div>
    <el-button
      class="el-button-op-roi"
      @click="opSoma"
    >
      {{ ifSoma }}
    </el-button>
    <div v-if="ifSoma === 'Hide Soma'" />
    <div
      class="div-op-roi"
    >
      <el-button
        type="text"
        size="medium"
        icon="el-icon-search"
        @click="searchSomaNeurons"
      >
        Search Neurons Around
      </el-button>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator'

@Component<Soma>({
  mounted () {}
})

export default class Soma extends Vue {
    @Prop({ required: true }) _showSoma!: any
    @Prop({ required: true }) _hideSoma!: any
    @Prop({ required: true }) _updateSomaBall!: any
    private ifSoma: string = 'Show Soma'
    private somaX: number = 100
    private somaY: number = 100
    private somaZ: number = 100
    private somaR: number = 100

    /**
     * 展示或隐藏ROI小球
     * @private
     */
    private opSoma () {
      if (this.ifSoma === 'Show Soma') {
        this._showSoma(this.somaR)
        this.ifSoma = 'Hide Soma'
      } else {
        this._hideSoma()
        this.ifSoma = 'Show Soma'
      }
    }

    /**
     * 更新ROI的位置或者半径
     * @private
     */
    private updateSoma () {
      this._updateSomaBall(this.somaX, this.somaY, this.somaZ, this.somaR)
    }

    /**
     * 设置ROI的位置
     * @param x
     * @param y
     * @param z
     */
    public setSoma (x: number, y: number, z: number) {
      this.somaX = x
      this.somaY = y
      this.somaZ = z
      this.updateSoma()
    }

    /**
     * 搜索ROI中的神经元
     * @private
     */
    private searchSomaNeurons () {
      this.updateSoma()
      let somaParameter = this.somaX + '_' + this.somaY + '_' + this.somaZ + '_' + this.somaR
      this.$emit('searchROINeurons', somaParameter)
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
