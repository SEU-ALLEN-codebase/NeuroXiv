<template>
  <div
    id="map"
    class="map"
  >
    <slot />
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import 'ol/ol.css'
import { Map as OlMap, View, ImageTile } from 'ol'
import Image from 'ol/layer/Image'
import Projection from 'ol/proj/Projection'
import ImageWMS from 'ol/source/ImageWMS'
import Layer from 'ol/layer/Layer'
import { composeCssTransform } from 'ol/transform'
import TileLayer from 'ol/layer/Tile'
import WMTS from 'ol/source/WMTS.js'
import WMTSTileGrid from 'ol/tilegrid/WMTS.js'

import { getWidth, getTopLeft } from 'ol/extent.js'
import { get as getProjection } from 'ol/proj.js'
import { Tile } from 'ol/layer'
import { debounce } from 'lodash'
import { sleep } from '@/utils/util'

@Component<AtlasViewer>({
  mounted () {
    this.initMap()
    // this.getPathMap()
  }
})

export default class AtlasViewer extends Vue {
  private atlasMap!: OlMap
  private projection!: Projection
  private imageLayer: Tile<any> | any = null
  private svgLayer: Layer<any, any> | any = null
  private pathsDom: any[] = []
  private pathsColor: string[] = []
  private pathMap: Map<number, string[]> = new Map()
  private svgContainer: any = null
  private debounceSvgRender: any = null

  /**
   * 初始化地图
   * @private
   */
  private initMap () {
    console.log('initMap...')
    this.projection = new Projection({
      code: 'EPSG:404000',
      units: 'm'
    })
    // let p900913 = getProjection('EPSG:900913')
    // console.log('EPSG:900913: ', p900913)
    // console.log(p900913.getExtent())
    // console.log(getTopLeft(p900913.getExtent()))

    // let projectionExtent = projection.getExtent()
    // let matrixIds = ['My_404000:0', 'My_404000:1', 'My_404000:2', 'My_404000:3', 'My_404000:4', 'My_404000:5',
    //   'My_404000:6', 'My_404000:7', 'My_404000:8', 'My_404000:9', 'My_404000:10', 'My_404000:11',
    //   'My_404000:12', 'My_404000:13', 'My_404000:14', 'My_404000:15', 'My_404000:16', 'My_404000:17',
    //   'My_404000:18', 'My_404000:19', 'My_404000:20', 'My_404000:21', 'My_404000:22', 'My_404000:23',
    //   'My_404000:24', 'My_404000:25', 'My_404000:26', 'My_404000:27', 'My_404000:28', 'My_404000:29', 'My_404000:30']
    // let resolutions = []
    // resolutions.push(781.25)
    // for (let i = 0; i < 30; ++i) {
    //   resolutions.push(resolutions[i] / 2)
    // }
    // console.log('aaaaaaaa', resolutions)

    // this.imageLayer = new Tile({
    //   source: new WMTS({
    //     url: 'http://9.135.230.212:8080/geoserver/gwc/service/wmts',
    //     layer: 'test:57698_0_template', // 'test:576985993_863', // 'test:576985993_863_colorlabel',
    //     matrixSet: 'My_404000',
    //     format: 'image/jpeg',
    //     projection: this.projection,
    //     tileGrid: new WMTSTileGrid({
    //       origin: [-100000, 100000], // getTopLeft(projectionExtent),
    //       extent: [-100000, -100000, 100000, 100000],
    //       resolutions: resolutions,
    //       matrixIds: matrixIds
    //     }),
    //     crossOrigin: 'anonymous',
    //     wrapX: false,
    //     style: ''
    //   }),
    //   opacity: 1
    // })

    this.atlasMap = new OlMap({
      target: 'map',
      layers: [],
      view: new View({
        projection: this.projection,
        center: [5700, 4000],
        zoom: 15,
        minZoom: 15,
        maxZoom: 18
      })
    })
  }

  /**
   * 清除底图层
   */
  public clearImageLayer () {
    if (this.imageLayer) {
      this.atlasMap.removeLayer(this.imageLayer)
      this.imageLayer = null
    }
  }

  /**
   * 更新底图层
   * @param imageInfo 底图的相关信息，详情见api
   */
  public updateImageLayer (imageInfo: any) {
    this.clearImageLayer()
    // console.log(imageInfo)
    this.atlasMap.setView(new View({
      projection: new Projection({
        code: 'EPSG:404000',
        units: 'm'
      }),
      center: [imageInfo.width / 2, imageInfo.height / 2],
      zoom: 6,
      minZoom: 6,
      maxZoom: 18,
      resolutions: imageInfo.source.resolutions,
      // showFullExtent: true
      zoomFactor: 2
    }))
    this.imageLayer = new Tile({
      source: new WMTS({
        url: imageInfo.source.url,
        layer: imageInfo.source.layer,
        matrixSet: imageInfo.source['matrix_set'],
        format: 'image/jpeg',
        projection: this.projection,
        tileGrid: new WMTSTileGrid({
          origin: getTopLeft(imageInfo.source.extent),
          extent: imageInfo.source.extent,
          resolutions: imageInfo.source.resolutions,
          matrixIds: imageInfo.source['matrix_ids']
        }),
        crossOrigin: 'anonymous',
        wrapX: false,
        style: ''
      }),
      opacity: 1
    })
    // console.log(this.imageLayer)
    this.atlasMap.addLayer(this.imageLayer)
    // console.log(this.atlasMap)
    if (this.svgLayer) {
      this.atlasMap.removeLayer(this.svgLayer)
      this.atlasMap.addLayer(this.svgLayer)
    }
  }

  /**
   * 清除svg层
   */
  public clearSvgLayer () {
    if (this.svgLayer) {
      this.atlasMap.removeLayer(this.svgLayer)
      this.svgLayer = null
      this.pathsDom = []
      this.pathsColor = []
      this.pathMap.clear()
      let svgElement = document.getElementById('svg-content')
      if (svgElement && svgElement.parentNode) {
        svgElement.parentNode.removeChild(svgElement)
      }
    }
  }

  /**
   * 更新svg层，用于脑区交互
   * @param svgInfo svg相关信息，详情见api
   */
  public async updateSvgLayer (svgInfo: any) {
    // await sleep(5000)
    return new Promise(async (resolve, reject) => {
      this.clearSvgLayer()
      // console.log('pathMap clear: ', this.pathMap)
      // const svgContainer = document.createElement('div')
      const svgContainer = document.getElementById('svg-layer') || document.createElement('div')
      const xhr = new XMLHttpRequest()
      xhr.open('GET', svgInfo.src)
      console.log(xhr)
      console.log(svgInfo.src)
      xhr.addEventListener('load', () => {
        console.log(xhr)
        // @ts-ignore
        const svg = xhr.responseXML.documentElement
        svg.id = 'svg-content'
        // @ts-ignore
        svgContainer.ownerDocument.importNode(svg)
        svgContainer.appendChild(svg)
        console.log('append svg')
        this.getPathMap(() => {
          resolve(true)
        })
      })
      xhr.send()
      // console.log(svgContainer)
      const width = svgInfo.width
      const height = svgInfo.height
      const svgResolution = 1
      svgContainer.style.width = width + 'px'
      svgContainer.style.height = height + 'px'
      svgContainer.style.transformOrigin = 'top left'
      // svgContainer.className = 'svg-layer'

      this.svgLayer = new Layer({
        render: (frameState: any) => {
          // console.log('frameState', frameState)
          const scale = svgResolution / frameState.viewState.resolution
          const center = frameState.viewState.center
          const size = frameState.size
          const cssTransform = composeCssTransform(
            size[0] / 2,
            size[1] / 2,
            scale,
            scale,
            frameState.viewState.rotation,
            -center[0],
            center[1] / svgResolution - height
          )
          // console.log('css', cssTransform)
          svgContainer.style.transform = cssTransform
          return svgContainer
        }
      })
      // this.svgContainer = svgContainer
      this.atlasMap.addLayer(
        this.svgLayer
      )
      console.log('add layer')
    })
  }

  /**
   * 判断该脑区是否在当前z slice存在
   * @param structureId 脑区id
   */
  public ifExistBrainRegion (structureId: any) {
    const pathIds = this.pathMap.get(structureId)
    console.log('pathIds', pathIds)
    return this.pathMap.has(structureId)
  }

  /**
   * 高亮脑区
   * @param structureId 脑区id
   */
  public highlightBrainRegion (structureId: any) {
    // console.log('highlightBrainRegion')
    for (let i = 0; i < this.pathsDom.length; i++) {
      // console.log('color', this.pathsColor[i])
      this.pathsDom[i].style.fill = this.pathsColor[i]
      this.pathsDom[i].style.fillOpacity = '0'
      this.pathsDom[i].style.strokeWidth = '8'
    }
    this.pathsDom = []
    this.pathsColor = []

    const pathIds = this.pathMap.get(structureId)
    // console.log('pathIds', pathIds)
    if (pathIds) {
      for (let pathId of pathIds) {
        let pathDom = document.getElementById(pathId) || new HTMLElement()
        // console.log('pathDom', pathDom.style)
        this.pathsDom.push(pathDom)
        this.pathsColor.push(pathDom.style.fill)
        pathDom.style.fill = 'rgb(0,0,255)'
        pathDom.style.fillOpacity = '0.5'
        pathDom.style.strokeWidth = '16'
      }
    }
  }

  /**
   * 鼠标悬浮的回调函数
   * @param event 回调事件
   */
  public handleMouseOver (event: any) {
    if (event.target.hasAttribute('d')) {
      // console.log('path_id: ', event.target.getAttribute('id'))
      // console.log('structure_id: ', event.target.getAttribute('structure_id'))
      const structureId = parseInt(event.target.getAttribute('structure_id'))
      this.highlightBrainRegion(structureId)
    }
  }

  /**
   * 鼠标左键单击的回调事件
   * @param event 回调事件
   */
  public handleMouseClick (event: any) {
    if (event.target.hasAttribute('d')) {
      const structureId = event.target.getAttribute('structure_id')
      return structureId
    } else {
      return null
    }
  }

  /**
   * 获取svg文件中key为脑区id，value为path元素的一个map，并遍历修改path元素的一些属性
   * @private
   */
  private async getPathMap (func: any = () => {}) {
    console.log('get path map start')
    let allPathDom = document.getElementsByTagName('path')
    console.log('length: ', allPathDom.length)
    while (allPathDom.length === 0) {
      await sleep(500)
    }
    console.log('length: ', allPathDom.length)
    for (let path of allPathDom) {
      const structureId = parseInt(path.getAttribute('structure_id') || '')
      const pathId = path.getAttribute('id') || '-1'
      path.style.fillOpacity = '0'
      path.style.strokeWidth = '8'
      if (this.pathMap.has(structureId)) {
        let pathIds: string[] = this.pathMap.get(structureId) || []
        pathIds.push(pathId)
        this.pathMap.set(structureId, pathIds)
      } else {
        this.pathMap.set(structureId, [pathId])
      }
    }
    console.log('get path map end')
    console.log('pathMap: ', this.pathMap)
    func()
  }
}
</script>

<style lang="less" scoped>
.map {
  position: relative;
  width: 100%;
  height: 100%;
}
</style>
