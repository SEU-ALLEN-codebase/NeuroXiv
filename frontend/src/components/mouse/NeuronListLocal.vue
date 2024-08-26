<template>
  <div class="neuron-list-container">
    <div class="batch-actions">
      <el-checkbox
        v-model="checkAll"
        label="Select All"
        :indeterminate="isIndeterminate"
        @change="batchSelectHandler"
      />
      <el-button
        type="primary"
        size="small"
        class="analysis-button"
        @click="neuronAnalysisHandler"
      >
        Analysis
      </el-button>
      <el-button
        type="primary"
        size="small"
        class="analysis-button"
        @click="viewNeuronsHandler"
      >
        View
      </el-button>
    </div>
    <ul class="neuron-items">
      <li
        v-for="(item, i) in currentPageData"
        :key="i"
        class="neuron-item"
      >
        <el-checkbox
          v-model="item.selected"
          @change="checkNeuronCallback(item)"
        />
        <img
          :src="item.img_src"
          :title="item.id"
          alt="neuron thumb"
          class="neuron-thumb"
        >
        <div class="neuron-tags">
          <el-tag
            class="neuron-tag-item-cell-type"
            :color="getTagColor(item.celltype)"
            effect="dark"
            size="mini"
            @click="jumpAtlasWeb(item)"
          >
            {{ item.celltype }}
          </el-tag>
          <el-tag
            class="neuron-tag-item"
            :color="getTagColor('hemisphere')"
            effect="dark"
            size="mini"
          >
            {{ item.hemisphere }}
          </el-tag>
          <el-tag
            class="neuron-tag-item"
            :color="getTagColor(item.brain_atlas)"
            effect="dark"
            size="mini"
          >
            {{ item.brain_atlas }}
          </el-tag>
          <el-tag
            v-for="(prop, j) in ['soma']"
            :key="j"
            class="neuron-tag-item"
            :class="{ disabled: !item[`has_${prop}`] }"
            :color="getTagColor(prop)"
            effect="dark"
            size="mini"
          >
            {{ prop }}
          </el-tag>
<!--          <el-tag-->
<!--            v-for="(prop, k) in ['local']"-->
<!--            :key="k"-->
<!--            class="neuron-tag-item"-->
<!--            :class="{ disabled: prop === 'full' }"-->
<!--            :color="getTagColor(prop)"-->
<!--            effect="dark"-->
<!--            size="mini"-->
<!--          >-->
<!--            {{ prop }}-->
<!--          </el-tag>-->
        </div>
        <el-button
          type="primary"
          size="small"
          @click="neuronViewHandler(item)"
        >
          Info
        </el-button>
      </li>
    </ul>
    <el-pagination
      class="pager"
      background
      small
      layout="prev, pager, next"
      :total="data.length"
      :page-size="pageSize"
      :current-page.sync="currentPage"
      :pager-count="7"
      @current-change="gotoPage"
    />
    <el-row
      class="pager"
      type="flex"
      justify="center">
      <el-col :span="8">
        <el-input v-model="targetPage" placeholder="跳转到页码"></el-input>
      </el-col>
      <el-col :span="8">
        <el-button type="primary" @click="goToTargetPage">go to page</el-button>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator'

@Component
export default class NeuronListLocal extends Vue {
  // 搜索结果的所有数据
  private data: any[] = []
  // 当前分页的数据
  private currentPageData: any[] = []
  private pageSize: number = 10
  private currentPage: number = 1
  private targetPage : number= 1
  private checkAll: boolean = false
  private isIndeterminate: boolean = false

  // 当前这一页选中的 item
  get currentPageSelectedItem () {
    return this.currentPageData.filter((item: any) => item.selected === true)
  }

  /**
   * 获取列表第一个数据
   */
  public getFirstItem () {
    return this.data.length ? this.data[0] : null
  }

  /**
   * 获取列表中勾选的数据
   */
  public getSelectedItems () {
    console.log(this.data.filter((item: any) => item.selected))
    return this.data.filter((item: any) => item.selected)
  }

  /**
   * 设置列表的数据
   * @param listData 列表数据
   */
  public setListData (listData: any[]) {
    listData.forEach((item: any) => {
      item.selected = false
    })
    this.data = listData
    this.gotoPage(1)
    this.checkAll = false
  }

  /**
   * 批量选择
   * @param val 选择或者取消选择
   */
  private batchSelectHandler (val: boolean) {
    this.currentPageData.forEach((item: any) => {
      item.selected = val
      this.$emit('checkNeuronLists', item)
    })
    this.isIndeterminate = false
  }

  /**
   * 批量选择神经元之后点击统计分析按钮
   */
  private neuronAnalysisHandler () {
    const selectedNeuronIds = this.data.filter((item: any) => item.selected).map((item: any) => item.id)
    if (selectedNeuronIds.length === 0) {
      this.$message.warning('No neuron selected')
      return
    }
    this.$emit('neuronAnalysis', selectedNeuronIds)
  }

  /**
   * 批量选择神经元之后3D可视化
   */
  private viewNeuronsHandler () {
    this.$emit('viewNeuronsHandlerLists')
  }

  /**
   * 点击查看按钮
   * @param neuronDetail 神经元信息
   */
  private neuronViewHandler (neuronDetail: any) {
    this.$emit('neuronViewHandlerLists', neuronDetail)
  }

  /**
   * 选中或取消右方神经元列表中的神经元的神经元的回调函数
   * @param neuronDetail 神经元信息
   */
  private checkNeuronCallback (neuronDetail: any) {
    console.log('Show Local')
    console.log(neuronDetail)
    this.$emit('checkNeuronLists', neuronDetail)
  }

  /**
   * 获取 neuron 属性标签对应的颜色
   * @param prop 属性名称
   * @private
   */
  private getTagColor (prop: string) {
    const colorMap: { [key: string]: string } = {
      axon: 'rgb(247, 206, 205)',
      bouton: 'rgb(253, 242, 208)',
      dendrite: 'rgb(229, 239, 219)',
      apical: 'rgb(255, 0, 255)',
      basal: 'rgb(255, 255, 0)',
      soma: 'rgb(224, 235, 245)',
      CCFv3: 'rgb(214, 253, 254)',
      fMOST: 'rgb(159, 205, 99)',
      local: 'rgb(134,145,234)',
      full: 'rgb(255,50,50)',
      hemisphere: 'rgb(255, 121, 108)'
    }
    return colorMap[prop] || 'white'
  }

  /**
   * 切换分页
   * @param whichPage 要切换的页数
   * @private
   */
  private gotoPage (whichPage: number) {
    let currentPage = whichPage || this.currentPage
    let start = this.pageSize * (currentPage - 1)
    let end = start + this.pageSize
    this.currentPageData = this.data.slice(start, end)
    this.currentPage = currentPage
  }

  private goToTargetPage () {
    let currentPage = this.targetPage
    let start = this.pageSize * (currentPage - 1)
    let end = start + this.pageSize
    this.currentPageData = this.data.slice(start, end)
    this.currentPage = currentPage
  }

  private jumpAtlasWeb (item: any) {
    window.location.href = `/CrossSpeciesAtlas.html#/${this.$route.params.lang}/?atlasName=${this.$store.state.atlas}&brainRegion=${item.celltype}`
  }

  @Watch('currentPageSelectedItem.length')
  currentPageSelectedChanged (newVal: number) {
    this.checkAll = newVal === this.currentPageData.length
    this.isIndeterminate = newVal > 0 && newVal < this.currentPageData.length
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.neuron-list-container {
  width: 380px;
  height: 100%;
  padding: 20px;
  display: flex;
  flex-flow: column nowrap;
  border-left: 1px solid gray;
  .batch-actions {
    border-bottom: 1px solid gray;
    padding: 0 0 20px 0;
    .analysis-button {
      margin-left: 20px;
    }
  }
  .neuron-items {
    height: 0;
    overflow: auto;
    flex: 1 1 auto;
    .neuron-item {
      border-bottom: 1px solid gray;
      padding: 15px 0;
      white-space: nowrap;
      > * {
        display: inline-block;
        vertical-align: middle;
        margin-right: 10px;
      }
      .neuron-thumb {
        width: 70px;
        border: 1px solid gray;
      }
      .neuron-tags {
        width: 160px;
        text-align: center;
        white-space: initial;
        .neuron-tag-item {
          display: inline-block;
          margin: 3px;
          width: 60px;
          text-align: center;
          color: black;
        }
        .neuron-tag-item-cell-type {
          display: inline-block;
          margin: 3px;
          width: 60px;
          text-align: center;
          color: black;
        }
        .neuron-tag-item-cell-type:hover {
          cursor: pointer;
        }
      }
    }
  }
  .pager {
    margin-top: 20px;
  }
}
</style>
