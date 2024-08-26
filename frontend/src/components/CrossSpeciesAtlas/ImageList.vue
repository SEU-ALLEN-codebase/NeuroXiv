<template>
  <div class="image-list-container">
    <ul class="image-items">
      <li
        v-for="(item, i) in currentPageData"
        :key="i"
        class="image-item"
      >
        <img
          :id="'image_'+item.zslice"
          :src="'http://10.192.23.213:8080/data/'+item.src"
          alt="image slice"
          class="image-slice"
          :class="item.selected?'image-slice-bigger':'image-slice-normal'"
          @click="selectSlice"
        >
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
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator'

@Component
export default class ImageList extends Vue {
  private imageData: any = null
  private data: any[] = []
  private currentPageData: any[] = []
  private pageSize: number = 8
  private currentPage: number = 1
  private currentZSilce: number = -1

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
    console.log('currentPageData ', this.currentPageData)
    this.currentPage = currentPage
  }

  /**
   * 设置缩略图列表数据，用于初始化
   * @param data 缩略图数据，详见api
   */
  public setData (data: any) {
    this.imageData = data
    this.data = data.thumbnail
    this.data.forEach((item: any) => {
      this.$set(item, 'selected', false)
    })
    console.log(this.data)
    this.currentZSilce = Math.floor(this.data.length / 2)
    // console.log('zslice: ', zslice)
    this.data[this.currentZSilce].selected = true
    this.gotoPage(Math.ceil(this.currentZSilce / this.pageSize))
  }

  /**
   * 清空缩略图列表
   */
  public clearData () {
    this.imageData = null
    this.data = []
    this.currentPageData = []
  }

  /**
   * 获取当前的 z slice
   */
  public getCurrentZSlice () {
    return this.currentZSilce
  }

  public setZSlice (zSlice: number) {
    if (this.currentZSilce !== -1) {
      this.data[this.currentZSilce].selected = false
    }
    this.currentZSilce = zSlice
    this.data[this.currentZSilce].selected = true
    this.gotoPage(Math.ceil(this.currentZSilce / this.pageSize))
  }

  /**
   * 点击某张z slice的回调函数，用于切换z slice
   * @param event 回调事件
   */
  public selectSlice (event: any) {
    if (this.currentZSilce !== -1) {
      this.data[this.currentZSilce].selected = false
    }
    const currentId = event.target.getAttribute('id')
    this.currentZSilce = parseInt(currentId.split('_')[1]) - 1
    this.data[this.currentZSilce].selected = true
    console.log('data', this.data)
    console.log('currentData', this.currentPageData)
    let selectedInfo = {
      'speciesId': null,
      'atlasId': null,
      'imageType': null,
      'zslice': this.getCurrentZSlice(),
      'changeValue': 'zslice'
    }
    console.log('selected info', selectedInfo)
    this.$emit('selectCrossAtlas', selectedInfo)
  }
}
</script>

<style scoped lang="less">
.image-list-container {
  width: 280px;
  height: 100%;
  padding: 20px;
  display: flex;
  overflow: auto;
  flex-flow: column nowrap;
  border-left: 1px solid gray;
  .image-item {
    border-bottom: 1px solid gray;
    padding: 15px 0;
    white-space: nowrap;
    width: 100%;
    .image-slice {
      display: block;
      width: 170px;
      height: 110px;
      margin: 0 auto;
    }
    .image-slice-normal {
      width: 170px;
      height: 110px;
    }
    .image-slice-bigger {
      width: 220px;
      height: 148px;
    }
  }
}
</style>
