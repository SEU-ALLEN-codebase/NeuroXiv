<template>
  <div class="home">
    <SmallScreenAlert />
    <el-container class="app-container">
      <el-header height="auto">
        <header-bar>
          <div />
        </header-bar>
      </el-header>
      <el-container>
        <el-main>
          <div class="main-content">
            <AtlasDetail
              ref="atlasDetail"
              @selectCrossAtlas="selectCrossAtlas"
              @getBrainRegionInfo="getBrainRegionInfo"
            />
          </div>
          <p
            v-if="!hasSvg"
            class="no-svg-tip"
          >
            No image display for selected atlas
          </p>
        </el-main>
        <el-aside width="auto">
          <ImageList
            ref="imageList"
            @selectCrossAtlas="selectCrossAtlas"
          />
          <p v-if="!hasImage" class="no-image-tip">No image for selected atlas</p>
        </el-aside>
      </el-container>
    </el-container>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Ref } from 'vue-property-decorator'
import HeaderBar from '@/components/mouse/HeaderBar.vue'
import SmallScreenAlert from '@/components/common/SmallScreenAlert.vue'
import AtlasDetail from '@/components/CrossSpeciesAtlas/AtlasDetail.vue'
import { getALLSpecies, getSpeciesInfo, getSpeciesImage, getThumbnailList, getStructuralOntology, getSpeciesAtlas, getBrainRegionInfo } from '@/request/apis/CrossSpeciesAtlas/atlas'
import ImageList from '@/components/CrossSpeciesAtlas/ImageList.vue'
import { decreaseLoadingCount, increaseLoadingCount, LoadingZero, showLoading } from '@/request/RequestWrapper'

@Component({
  components: {
    ImageList,
    AtlasDetail,
    SmallScreenAlert,
    HeaderBar
  }
})
export default class Container extends Vue {
  @Ref('atlasDetail') readonly atlasDetail!: AtlasDetail
  @Ref('imageList') readonly imageList!: ImageList
  private hasImage: boolean = true
  private hasSvg: boolean = true

  /**
   * 获取数据库所有species的id和名称
   * @private
   */
  private async getAllSpecies () {
    try {
      console.log('species: ', this.atlasDetail.species)
      this.atlasDetail.species = await getALLSpecies(document.body).start()
      console.log('species: ', this.atlasDetail.species)
    } catch (e) {
      console.error(e)
    }
  }

  /**
   * 初始化atlas网页的数据
   * @private
   */
  private async initAtlasDetail () {
    await this.getAllSpecies()
    this.atlasDetail.selectedSpecies = this.atlasDetail.species[0].id
    let selectedInfo = {
      'speciesId': this.atlasDetail.selectedSpecies,
      'atlasId': null,
      'imageType': null,
      'zslice': null,
      'changeValue': 'species'
    }
    console.log('init select info', selectedInfo)
    await this.selectCrossAtlas(selectedInfo)
  }

  /**
   * 获取species相关信息
   * @param selectedInfo 当前需要选择的信息
   * @private
   */
  private async getSpeciesInfo (selectedInfo: any) {
    this.atlasDetail.currentSpeciesInfo = await getSpeciesInfo(document.body, selectedInfo.speciesId).start()
    console.log('species info', this.atlasDetail.currentSpeciesInfo)
    this.atlasDetail.imageTypes = this.atlasDetail.currentSpeciesInfo['image_list']
    console.log('image types', this.atlasDetail.imageTypes)
  }

  /**
   * 获取缩略图列表
   * @param selectedInfo 当前需要选择的信息
   * @private
   */
  private async getThumbnailList (selectedInfo: any) {
    const thumbnailInfo = {
      'id': selectedInfo.speciesId,
      'type': selectedInfo.imageType
    }
    let thumbnailData = await getThumbnailList(document.body, thumbnailInfo).start()
    console.log('thumbnail', thumbnailData)
    this.imageList.setData(thumbnailData)
    console.log('-----getThumbnailList-----', selectedInfo)
    if (selectedInfo.zslice !== -1) {
      this.imageList.setZSlice(selectedInfo.zslice)
    }
  }

  /**
   * 获取species的底图信息
   * @param selectedInfo 当前需要选择的信息
   * @private
   */
  private async getSpeciesImage (selectedInfo: any) {
    const imageInfo = {
      'id': selectedInfo.speciesId,
      'type': selectedInfo.imageType,
      'zslice': selectedInfo.zslice
    }
    this.atlasDetail.currentImageInfo = await getSpeciesImage(document.body, imageInfo).start()
    console.log('currentImageInfo ', this.atlasDetail.currentImageInfo)
    this.atlasDetail.atlasViewer.updateImageLayer(this.atlasDetail.currentImageInfo)
  }

  /**
   * 获取脑区树状结构数据
   * @param selectedInfo 当前需要选择的信息
   * @private
   */
  private async getStructuralOntology (selectedInfo: any) {
    this.atlasDetail.atlasTreeData = await getStructuralOntology(document.body, selectedInfo.atlasId).start()
    if (!Array.isArray(this.atlasDetail.atlasTreeData)) {
      this.atlasDetail.atlasTreeData = [this.atlasDetail.atlasTreeData]
    }
    console.log('atlasData', this.atlasDetail.atlasTreeData)
  }

  /**
   * 获取species脑区svg
   * @param selectedInfo 当前需要选择的信息
   * @private
   */
  private async getSpeciesAtlas (selectedInfo: any) {
    const atlasInfo = {
      'ontology_id': selectedInfo.atlasId,
      'zslice': selectedInfo.zslice
    }
    this.atlasDetail.currentSvgInfo = await getSpeciesAtlas(document.body, atlasInfo).start()
    let loadingInstance = showLoading(document.body)
    increaseLoadingCount()
    await this.atlasDetail.atlasViewer.updateSvgLayer(this.atlasDetail.currentSvgInfo)
    decreaseLoadingCount()
    if (LoadingZero()) {
      loadingInstance.close()
    }
  }

  /**
   * 获取脑区信息
   * @param func 获取后执行的回调函数
   * @param ontologyId 图谱id
   * @param brainRegionId 脑区id
   * @private
   */
  private async getBrainRegionInfo (func: any, ontologyId: number, brainRegionId: number) {
    console.log('func', arguments)
    const brainRegionInfo = {
      'ontology_id': ontologyId,
      'brain_region_id': brainRegionId
    }
    // this.atlasDetail.currentBrainRegionInfo = await getBrainRegionInfo(document.body, brainRegionInfo).start()
    let brainRegion = await getBrainRegionInfo(document.body, brainRegionInfo).start()
    console.log('getBrainRegionInfo', brainRegion)
    func(brainRegion)
  }

  /**
   * 根据当前选择的信息切换对应脑图谱
   * @param selectedInfo 当前需要选择的信息
   * @param func 回调函数
   * @private
   */
  private async selectCrossAtlas (selectedInfo: any, func: any = () => {}) {
    switch (selectedInfo.changeValue) {
      case 'species':
        await this.getSpeciesInfo(selectedInfo)
        selectedInfo.atlasId = this.atlasDetail.currentSpeciesInfo.atlas.id
        if (this.atlasDetail.imageTypes.length > 0) {
          this.hasImage = true
          this.atlasDetail.selectedImageType = this.atlasDetail.imageTypes[0]['image_type']
          selectedInfo.imageType = this.atlasDetail.selectedImageType
          selectedInfo.changeValue = 'imageType'
          await this.selectCrossAtlas(selectedInfo)
          selectedInfo.zslice = this.imageList.getCurrentZSlice()
          if (selectedInfo.zslice === -1) {
            selectedInfo.zslice = 0
          }
          if (this.atlasDetail.currentSpeciesInfo.hasOwnProperty('has_svg') && this.atlasDetail.currentSpeciesInfo['has_svg']) {
            this.hasSvg = true
            await this.getSpeciesAtlas(selectedInfo)
          } else {
            this.hasSvg = false
          }
        } else {
          this.imageList.clearData()
          this.atlasDetail.atlasViewer.clearImageLayer()
          this.atlasDetail.atlasViewer.clearSvgLayer()
          this.hasImage = false
          this.hasSvg = false
        }
        await this.getStructuralOntology(selectedInfo)
        break
      case 'imageType':
        console.log('------------------before imageType selectedInfo------------------------ ', selectedInfo)
        selectedInfo.zslice = this.imageList.getCurrentZSlice()
        await this.getThumbnailList(selectedInfo)
        selectedInfo.zslice = this.imageList.getCurrentZSlice()
        console.log('------------------imageType selectedInfo------------------------ ', selectedInfo)
        await this.getSpeciesImage(selectedInfo)
        break
      case 'zslice':
        selectedInfo.speciesId = this.atlasDetail.selectedSpecies
        selectedInfo.atlasId = this.atlasDetail.currentSpeciesInfo.atlas.id
        selectedInfo.imageType = this.atlasDetail.selectedImageType
        this.imageList.setZSlice(selectedInfo.zslice)
        await this.getSpeciesImage(selectedInfo)
        await this.getSpeciesAtlas(selectedInfo)
        break
      default:
        break
    }
    func()
  }

  /**
   * 根据小鼠脑区简称高亮该脑区，并显示脑区信息
   * @param atlasName atlas名称 fMOST或者CCFv3
   * @param brainRegion 脑区简称
   * @private
   */
  private async getMouseBrainRegion (atlasName: string, brainRegion: string) {
    await this.getAllSpecies()
    if (atlasName === 'fMOST') {
      this.atlasDetail.selectedSpecies = this.atlasDetail.species[2].id
    } else {
      this.atlasDetail.selectedSpecies = this.atlasDetail.species[0].id
    }
    // this.atlasDetail.selectedSpecies = this.atlasDetail.species[0].id
    let selectedInfo = {
      'speciesId': this.atlasDetail.selectedSpecies,
      'atlasId': null,
      'imageType': null,
      'zslice': null,
      'changeValue': 'species'
    }
    console.log('init select info', selectedInfo)
    await this.selectCrossAtlas(selectedInfo, () => {
      this.atlasDetail.selectMouseBrainRegion(brainRegion, this.atlasDetail.atlasTreeData[0])
    })
  }

  mounted () {
    setTimeout(() => {
      console.log('----------route----------', this.$route.query)
      if (this.$route.query.hasOwnProperty('brainRegion') && this.$route.query.hasOwnProperty('atlasName')) {
        // @ts-ignore
        this.getMouseBrainRegion(this.$route.query['atlasName'], this.$route.query['brainRegion'])
      } else {
        this.initAtlasDetail()
      }
    }, 2000, {})
  }
}
</script>

<style lang="less" scoped>
.home {
  overflow: auto;
  height: 100%;
  .app-container {
    min-width: 1300px;
    height: 100%;
    .el-header {
      padding: 0;
    }
    .el-main {
      height: 100%;
      position: relative;
      .main-content {
        height: 100%;
      }
      .no-svg-tip {
        position: absolute;
        top: 5px;
        right: 20px;
      }
    }
    .el-aside {
      height: 100%;
      overflow: visible;
      box-shadow: 3px 3px 8px 2px var(--shadow-color);
      position: relative;
      .no-image-tip {
        position: absolute;
        top: 50%;
        width: 100%;
        text-align: center;
      }
    }
  }
}
</style>
