<template>
  <div class="atlas-detail-container">
    <div class="left-side">
      <el-tabs
        v-model="selectedTab"
        :stretch="true"
        class="full-height"
      >
        <el-tab-pane
          label="menu"
          name="menu"
        >
          <div class="select-container">
            <p class="select-label">
              Species
            </p>
            <el-select
              v-model="selectedSpecies"
              class="select"
              @change="speciesChangeCallback"
            >
              <el-option
                v-for="item in species"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </div>
          <div class="select-container">
            <p class="select-label">
              Template
            </p>
            <el-select
              v-model="selectedImageType"
              class="select"
              @change="imageTypeChangeCallback"
            >
              <el-option
                v-for="item in imageTypes"
                :key="item.image_type"
                :label="item.image_type"
                :value="item.image_type"
              />
            </el-select>
          </div>
          <div class="atlas-container">
            <el-input
              v-model="brainRegionFilterText"
              class="brain-region-filter-input"
              placeholder="Filter keyword"
              size="mini"
            />
            <el-tree
              ref="atlasTree"
              :data="atlasTreeData"
              :render-after-expand="false"
              node-key="id"
              :props="{ label: 'acronym' }"
              :check-strictly="true"
              highlight-current
              :filter-node-method="filterAllConditions"
              @node-click="clickAtlasTreeNodeCallback"
            >
              <template
                slot-scope="{ node, data }"
              >
                <el-tooltip
                  effect="dark"
                  :content="data.name"
                  placement="right"
                >
                  <span>{{ node.label === 'nan' ? data.name : node.label }}</span>
                </el-tooltip>
              </template>
            </el-tree>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    <div class="separator" />
    <div class="right-side">
      <AtlasViewer
        ref="atlasViewer"
        @mouseover.native="handleMouseOver"
        @click.native="handleMouseClick"
        @mousedown.native="handleMouseDown"
        @mouseup.native="handleMouseUp"
      >
        <BrainRegionInfoCard
          ref="brainRegionInfoCardOne"
          :brain-region-info-style="brainRegionInfoOneStyle"
          :brain-region-info-visible="brainRegionInfoOneVisible"
          :brain-region-info="currentBrainRegionInfo"
          :get-adjacent-brain-region-info="GetAdjacentBrainRegionInfo"
          :get-related-brain-region-info="GetRelatedBrainRegionInfo"
          :select-adjacent-brain-region="SelectAdjacentBrainRegion"
          :select-related-brain-region="SelectRelatedBrainRegion"
          :leave-brain-region="leaveBrainRegionCallbackThrottle"
        />
        <BrainRegionInfoCard
          :brain-region-info-visible="brainRegionInfoTwoVisible"
          :brain-region-info-style="brainRegionInfoTwoStyle"
          :brain-region-info="otherBrainRegionInfo"
          :get-adjacent-brain-region-info="GetAdjacentBrainRegionInfo"
          :get-related-brain-region-info="GetRelatedBrainRegionInfo"
          :select-adjacent-brain-region="SelectAdjacentBrainRegion"
          :select-related-brain-region="SelectRelatedBrainRegion"
          :leave-brain-region="leaveBrainRegionCallback"
        />
      </AtlasViewer>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Ref, Vue, Watch } from 'vue-property-decorator'
import AtlasViewer from '@/components/CrossSpeciesAtlas/AtlasViewer.vue'
import BrainRegionInfoCard from '@/components/CrossSpeciesAtlas/BrainRegionInfoCard.vue'
import { debounce, throttle } from 'lodash'

import neuronViewerBaseData from '../mouse/surf_tree.json'

@Component({
  components: {
    BrainRegionInfoCard,
    AtlasViewer
  }
})

export default class AtlasDetail extends Vue {
  @Ref('atlasViewer') readonly atlasViewer!: AtlasViewer
  private selectedTab: string = 'menu'
  public atlasTreeData: any = [] // neuronViewerBaseData
  private brainRegionFilterText: string = ''
  private debounceBrainRegionFilter: any = null
  public selectedSpecies: string = ''
  public species: any = null
  // public selectedAtlas: string = ''
  // public atlases: any = null
  public selectedImageType: string = ''
  public imageTypes: any = null
  public currentSpeciesInfo: any = null
  public currentImageInfo: any = null
  public currentSvgInfo: any = null

  public currentBrainRegionInfo: any = null
  private brainRegionInfoOneVisible: boolean = false
  private brainRegionInfoOneStyle: any = {
    '--top': 0,
    '--left': 0
  }

  private otherBrainRegionInfo: any = null
  private brainRegionInfoTwoVisible: boolean = false
  private brainRegionInfoTwoStyle: any = {
    '--top': 0,
    '--left': 0
  }
  private banMouseOver = false

  private leaveBrainRegionCallbackThrottle: any = () => {};

  /**
   * 筛选所有的搜索条件
   * @param value 输入的关键字
   * @param data 搜索条目信息
   * @param node 节点
   * @private
   */
  private filterAllConditions (value: string, data: any, node: any) {
    if (!value) return true
    return this.findSearchKey(node, value.toLowerCase())
  }

  /**
   * 递归往上查找 node.label 是否包含 key
   * @param node 节点
   * @param key 要查找的 key
   */
  private findSearchKey (node:any, key: string): boolean {
    if (!node.label) {
      return false
    }
    if (node.label.toLowerCase().indexOf(key) !== -1 || node.data.name.toLowerCase().indexOf(key) !== -1) {
      return true
    }
    if (!node.parent) {
      return false
    }
    return this.findSearchKey(node.parent, key)
  }

  /**
   * species下拉框选项值改变的回调函数
   * @param currentSpecies 当前species
   */
  public speciesChangeCallback (currentSpecies: string) {
    console.log(currentSpecies)
    let selectedInfo = {
      'speciesId': currentSpecies,
      'atlasId': null,
      'imageType': null,
      'zslice': null,
      'changeValue': 'species'
    }
    this.$emit('selectCrossAtlas', selectedInfo)
  }

  // public atlasChangeCallback (currentAtlas: string) {
  //   // console.log(currentSpecies)
  //   let selectedInfo = {
  //     'species': this.selectedSpecies,
  //     'atlas': currentAtlas,
  //     'imageType': null,
  //     'zslice': null,
  //     'changeValue': 'atlas'
  //   }
  //   this.$emit('selectCrossAtlas', selectedInfo)
  // }

  /**
   * template下拉框选项值改变的回调函数
   * @param currentImageType 当前image type
   */
  public imageTypeChangeCallback (currentImageType: string) {
    let selectedInfo = {
      'speciesId': this.selectedSpecies,
      'atlasId': this.currentSpeciesInfo.atlas.id,
      'imageType': currentImageType,
      'zslice': null,
      'changeValue': 'imageType'
    }
    console.log('-----------------------imageTypeChangeCallback----------------------')
    this.$emit('selectCrossAtlas', selectedInfo)
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
   * 将el-tree的某个节点的孩子节点以及自己都设置为收起
   * @param node 节点
   * @private
   */
  private static collapseNode (node: any) {
    node.expanded = false
    // console.log('node: ', node)
    node.childNodes.forEach((cNode: any) => {
      AtlasDetail.collapseNode(cNode)
    })
  }

  /**
   * 鼠标处于down的回调函数
   * @private
   */
  private handleMouseDown () {
    this.banMouseOver = true
  }

  /**
   * 鼠标处于up的回调函数
   * @private
   */
  private handleMouseUp () {
    this.banMouseOver = false
  }

  /**
   * 鼠标悬浮的回调函数，用于高亮脑区
   * @param event 回调事件
   * @private
   */
  private handleMouseOver (event: any) {
    event.preventDefault()
    if (!this.banMouseOver) {
      this.atlasViewer.handleMouseOver(event)
      console.log('mouse enter')
    }
    // this.atlasViewer.handleMouseOver(event)
  }

  /**
   * 鼠标左键单击的回调函数，用于显示脑区信息
   * @param event 回调事件
   * @private
   */
  private async handleMouseClick (event: any) {
    console.log(event)
    this.brainRegionInfoOneVisible = false
    event.preventDefault()
    const structId = this.atlasViewer.handleMouseClick(event)
    if (structId) {
      // @ts-ignore
      AtlasDetail.collapseNode(this.$refs['atlasTree'].root)
      // @ts-ignore
      let node = this.$refs['atlasTree'].getNode(structId)
      AtlasDetail.expandNode(node)
      // @ts-ignore
      this.$refs['atlasTree'].setCurrentKey(structId)
      console.log('event', event)
      this.brainRegionInfoOneStyle['--left'] = event.layerX + 'px'
      this.$emit('getBrainRegionInfo', (brainRegion: any) => {
        this.currentBrainRegionInfo = brainRegion
        this.brainRegionInfoOneVisible = true
        this.$nextTick(() => {
          this.brainRegionInfoOneStyle['--top'] = '0px'
          this.brainRegionInfoOneStyle['--left'] = '0px'
          // // @ts-ignore
          // const brainRegionInfoCardOneHeight = this.$refs.brainRegionInfoCardOne.$el.children[0].offsetHeight
          // // @ts-ignore
          // const brainRegionInfoCardOneWidth = this.$refs.brainRegionInfoCardOne.$el.children[0].offsetWidth
          // console.log('brainRegionInfoCardOneElement', brainRegionInfoCardOneHeight)
          // // @ts-ignore
          // const atlasViewerHeight = this.$refs.atlasViewer.$el.clientHeight
          // // @ts-ignore
          // const atlasViewerWidth = this.$refs.atlasViewer.$el.clientWidth
          // if (event.layerY > atlasViewerHeight / 2) {
          //   this.brainRegionInfoOneStyle['--top'] = (event.layerY - brainRegionInfoCardOneHeight) + 'px'
          // } else {
          //   this.brainRegionInfoOneStyle['--top'] = event.layerY + 'px'
          // }
          // if (event.layerX > atlasViewerWidth / 2) {
          //   this.brainRegionInfoOneStyle['--left'] = (event.layerX - brainRegionInfoCardOneWidth) + 'px'
          // } else {
          //   this.brainRegionInfoOneStyle['--left'] = event.layerX + 'px'
          // }
        })
      }, this.currentSpeciesInfo.atlas.id, structId)
    }
  }

  /**
   * 切换到有该脑区的z slice并高亮其脑区
   * @param brainRegionId 脑区id
   */
  private switchZSliceForHighlightBrainRegion (brainRegionId: number) {
    if (this.currentBrainRegionInfo['zslices'].length > 0) {
      if (this.atlasViewer.ifExistBrainRegion(brainRegionId)) {
        // console.log('exist ', data.id)
        this.atlasViewer.highlightBrainRegion(brainRegionId)
      } else {
        // console.log('not exist ', data.id)
        let selectedInfo = {
          'speciesId': this.selectedSpecies,
          'atlasId': this.currentSpeciesInfo.atlas.id,
          'imageType': this.selectedImageType,
          'zslice': this.currentBrainRegionInfo['zslices'][0],
          'changeValue': 'zslice'
        }
        this.$emit('selectCrossAtlas', selectedInfo, () => {
          this.atlasViewer.highlightBrainRegion(brainRegionId)
        })
      }
    }
  }

  /**
   * 点击脑区树状结构结构的回调函数，用于显示脑区信息
   * @param data 脑区数据
   * @private
   */
  private clickAtlasTreeNodeCallback (data: any) {
    console.log('data id: ', data.id)
    // @ts-ignore
    AtlasDetail.collapseNode(this.$refs['atlasTree'].root)
    // @ts-ignore
    let node = this.$refs['atlasTree'].getNode(data.id)
    AtlasDetail.expandNode(node)
    // @ts-ignore
    this.$refs['atlasTree'].setCurrentKey(data.id)
    this.atlasViewer.highlightBrainRegion(data.id)
    this.$emit('getBrainRegionInfo', (brainRegion: any) => {
      this.currentBrainRegionInfo = brainRegion
      this.brainRegionInfoOneStyle['--top'] = '0'
      this.brainRegionInfoOneStyle['--left'] = '0'
      this.brainRegionInfoOneVisible = true
      console.log('brainRegionInfoOneVisible', this.brainRegionInfoOneVisible)
      console.log('currentBrainRegionInfo', this.currentBrainRegionInfo)
      this.switchZSliceForHighlightBrainRegion(data.id)
    }, this.currentSpeciesInfo.atlas.id, data.id)
  }

  /**
   * 离开脑区信息卡片中脑区链接的回调函数
   * @private
   */
  private leaveBrainRegionCallback () {
    console.log('mouse leave')
    this.brainRegionInfoTwoVisible = false
  }

  /**
   * 点击脑区信息卡片相邻脑区的回调函数
   * @param item 对应脑区相关信息
   * @constructor
   * @private
   */
  private SelectAdjacentBrainRegion (item: any) {
    console.log('SelectAdjacentBrainRegion', item)
    // @ts-ignore
    AtlasDetail.collapseNode(this.$refs['atlasTree'].root)
    // @ts-ignore
    let node = this.$refs['atlasTree'].getNode(item.id)
    AtlasDetail.expandNode(node)
    // @ts-ignore
    this.$refs['atlasTree'].setCurrentKey(item.id)
    // this.brainRegionInfoOneVisible = true
    // this.atlasViewer.highlightBrainRegion(item.id)
    this.$emit('getBrainRegionInfo', (brainRegion: any) => {
      this.currentBrainRegionInfo = brainRegion
      this.brainRegionInfoOneVisible = true
      this.switchZSliceForHighlightBrainRegion(item.id)
    }, this.currentSpeciesInfo.atlas.id, item.id)
  }

  /**
   * 悬浮脑区信息卡片相邻脑区的回调函数
   * @param item 对应脑区相关信息
   * @constructor
   * @private
   */
  private GetAdjacentBrainRegionInfo (item: any) {
    if (this.brainRegionInfoTwoVisible) {
      return
    }
    this.$emit('getBrainRegionInfo', (brainRegion: any) => {
      this.otherBrainRegionInfo = brainRegion
      this.brainRegionInfoTwoVisible = true
      this.$nextTick(() => {
        // @ts-ignore
        const brainRegionInfoCardOneWidth = this.$refs.brainRegionInfoCardOne.$el.children[0].offsetWidth
        console.log('brainRegionInfoCardOneElement', brainRegionInfoCardOneWidth)
        this.brainRegionInfoTwoStyle['--top'] = this.brainRegionInfoOneStyle['--top']
        this.brainRegionInfoTwoStyle['--left'] = (parseInt(this.brainRegionInfoOneStyle['--left'].replace('px', '')) + brainRegionInfoCardOneWidth + 5) + 'px'
        console.log('brainRegionInfoTwoStyle', this.brainRegionInfoTwoStyle)
      })
    }, this.currentSpeciesInfo.atlas.id, item.id)
  }

  /**
   * 点击脑区信息卡片相关脑区的回调函数
   * @param item 对应脑区相关信息
   * @constructor
   * @private
   */
  private SelectRelatedBrainRegion (item: any, bItem: any) {
    console.log(item, bItem)
    this.selectedSpecies = item['species_id']
    this.$emit('getBrainRegionInfo', (brainRegion: any) => {
      this.currentBrainRegionInfo = brainRegion
      this.brainRegionInfoOneVisible = true
      let selectedInfo = {
        'speciesId': item['species_id'],
        'atlasId': null,
        'imageType': null,
        'zslice': null,
        'changeValue': 'species'
      }
      this.$emit('selectCrossAtlas', selectedInfo, () => {
        // @ts-ignore
        AtlasDetail.collapseNode(this.$refs['atlasTree'].root)
        // @ts-ignore
        let node = this.$refs['atlasTree'].getNode(bItem.id)
        AtlasDetail.expandNode(node)
        // @ts-ignore
        this.$refs['atlasTree'].setCurrentKey(bItem.id)
        this.switchZSliceForHighlightBrainRegion(bItem.id)
      })
    }, item.ontology_id, bItem.id)
  }

  /**
   * 悬浮脑区信息卡片相关脑区的回调函数
   * @param item 对应脑区相关信息
   * @constructor
   * @private
   */
  private GetRelatedBrainRegionInfo (item: any, bItem: any) {
    if (this.brainRegionInfoTwoVisible) {
      return
    }
    console.log('GetRelatedBrainRegionInfo', item, bItem)
    this.$emit('getBrainRegionInfo', (brainRegion: any) => {
      this.otherBrainRegionInfo = brainRegion
      this.brainRegionInfoTwoVisible = true
      this.$nextTick(() => {
        // @ts-ignore
        const brainRegionInfoCardOneWidth = this.$refs.brainRegionInfoCardOne.$el.children[0].offsetWidth
        console.log('brainRegionInfoCardOneElement', brainRegionInfoCardOneWidth)
        this.brainRegionInfoTwoStyle['--top'] = this.brainRegionInfoOneStyle['--top']
        this.brainRegionInfoTwoStyle['--left'] = (parseInt(this.brainRegionInfoOneStyle['--left'].replace('px', '')) + brainRegionInfoCardOneWidth + 5) + 'px'
        console.log('brainRegionInfoTwoStyle', this.brainRegionInfoTwoStyle)
      })
    }, item.ontology_id, bItem.id)
  }

  /**
   * 根据小鼠脑区简称高亮该脑区，并显示脑区信息
   * @param brainRegion 脑区简称
   * @param data 脑区节点数据
   */
  public selectMouseBrainRegion (brainRegion: string, data: any) {
    if (data['acronym'] === brainRegion) {
      this.clickAtlasTreeNodeCallback(data)
      return
    }
    if (data.hasOwnProperty('children')) {
      for (let cdata of data['children']) {
        this.selectMouseBrainRegion(brainRegion, cdata)
      }
    }
  }

  mounted () {
    this.leaveBrainRegionCallbackThrottle = throttle(this.leaveBrainRegionCallback, 100)
  }

  @Watch('brainRegionFilterText')
  brainRegionFilterChanged (newVal: string) {
    if (!this.debounceBrainRegionFilter) {
      // @ts-ignore
      this.debounceBrainRegionFilter = debounce(this.$refs['atlasTree'].filter, 500)
    }
    this.debounceBrainRegionFilter(newVal)
  }
}
</script>

<style lang="less" scoped>
.atlas-detail-container {
  height: 100%;
  //color: black;
  background: #ffffff;
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
        .select-container {
          display: flex;
          justify-content: space-between;
          padding-bottom: 20px;
          .select-label {
            margin: 0;
            height: 40px;
            line-height: 40px;
          }
        }
        .brain-region-filter-input {
          margin-bottom: 10px;
        }
      }
    }
  }
  .right-side {
    flex: 1;
  }
}
</style>
