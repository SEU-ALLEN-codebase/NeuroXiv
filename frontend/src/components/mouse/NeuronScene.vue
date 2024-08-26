<template>
  <div
    ref="NeuronScene"
    class="neuron-scene"
    :style="pStyle"
  >
    <div class="top-button">
      <ColorPicker @color-selected="setColor" />
      <div
        v-if="ThreeViewer"
        class="right-top"
      >
        <el-button @click="setView('front')">
          <img
            class="view_button"
            src="../../../public/img/front.png"
            alt="Front View"
          >
        </el-button>
        <el-button @click="setView('side')">
          <img
            class="view_button"
            src="../../../public/img/side.png"
            alt="Side View"
          >
        </el-button>
        <el-button @click="setView('top')">
          <img
            class="view_button"
            src="../../../public/img/top.png"
            alt="Top View"
          >
        </el-button>
      </div>
    </div>

    <div
      class="position"
    >
      <p v-if="selectComponent">
        Current Brain Region: {{ selectComponent ? selectComponent.name : '' }}
      </p>
    </div>
    <el-popover
      v-model="neuronTipVisible"
      class="neuron-tip"
      :style="neuronTipStyle"
      trigger="manual"
    >
      <p v-if="selectNeuronInfo">
        id: {{ selectNeuronInfo.id }}
      </p>
      <p v-if="selectNeuronInfo">
        brain region: {{ selectNeuronInfo.cellType }}
      </p>
      <div style="text-align: left; margin: 0">
        <el-button
          type="text"
          @click="neuronViewHandler(selectNeuronInfo)"
        >
          More info
        </el-button>
      </div>
    </el-popover>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import * as THREE from 'three'
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader'
import { VTKLoader } from 'three/examples/jsm/loaders/VTKLoader'
import { TrackballControls } from 'three/examples/jsm/controls/TrackballControls'
import Slice from '@/components/mouse/Slice'
import { debounce } from 'lodash'
import { LineMaterial } from 'three/examples/jsm/lines/LineMaterial'
import { sleep } from '@/utils/util'
import ColorPicker from '@/components/mouse/ColorPicker.vue'

interface neuronSceneComponent {
  id: any,
  name: string,

  src: string,
  // eslint-disable-next-line camelcase
  rgb_triplet: number[],
}

@Component<NeuronScene>({
  components: { ColorPicker },
  mounted () {
    this.init()
  }
})

export default class NeuronScene extends Vue {
  private brainComponentMap!: Map<any, any>
  private neuronDataMap!: Map<any, any>
  private sliceMap!: Map<any, any>
  private centerShift!: THREE.Vector3
  private camera!: THREE.PerspectiveCamera
  private renderer!: THREE.WebGLRenderer
  // private scene!: THREE.Scene
  public scene!: THREE.Scene
  private controls!: TrackballControls
  private debounceOnSceneResize: any = null
  private resizeObserve: any = null
  private neuronData: any = []
  private selectComponent: any = null
  private selectComponentMaterial: any = null
  private pStyle: any = {
    '--zIndex': 1
  }
  private dendrite: any = null
  private roiBall: any = null
  private selectNeuron: any = null
  private selectNeuronMaterial: any = null
  private selectNeuronInfo: any = null
  private neuronTipVisible: boolean = false
  private neuronTipStyle: any = {
    '--bottom': 0,
    '--left': 0
  }
  private neuronInfoMap!: Map<any, any>
  public loadedObj:any = null
  public isRotating: boolean = false
  private somaBall:any = null // soma点的小球
  private selectedColor: string = '#ffffff'
  public ThreeViewer:boolean = true
  public multiViewerSoma!: Map<any, any>
  public multiViewerSomaPos !: Map<any, any>
  public mSomaBall:any = null
  public atlas:string = ''

    VIEW_TRANSFORMATIONS: any = {
      'front': new THREE.Vector3(-1, 0, 0), // Z轴正向朝向观察者
      'side': new THREE.Vector3(0, 0, 1), // X轴正向朝向观察者
      'top': new THREE.Vector3(0, 1, 0) // Y轴正向朝向观察者
    }
    public setView (viewName: string) {
      this.controls.reset()
      const direction = this.VIEW_TRANSFORMATIONS[viewName]
      if (!direction) return

      // 根据视图修改相机的up向量
      if (viewName === 'top') {
        this.camera.up.set(-1, 0, 0) // 重设相机的up向量
        // 同时设置沿y轴旋转180度
      } else {
        this.camera.up.set(0, 1, 0) // 重置为默认up向量
      }

      // 设置相机位置和朝向
      this.camera.position.set(direction.x * 500, direction.y * 500, direction.z * 500)
      this.camera.lookAt(this.scene.position)

      // 如果是顶视图，应用额外的旋转
      if (viewName === 'top') {
        this.camera.rotateOnWorldAxis(new THREE.Vector3(0, 1, 0), Math.PI) // Math.PI为180度
      }

      // 必须调用updateProjectionMatrix，特别是在修改up向量和旋转后
      this.camera.updateProjectionMatrix()

      // 重新渲染场景
      this.renderer.render(this.scene, this.camera)

      // 更新控制器
      this.controls.update()
    }

    // VIEW_TRANSFORMATIONS:any = {
    //   front: new THREE.Euler(-Math.PI / 2, 0, 0, 'XYZ'),
    //   side: new THREE.Euler(0, Math.PI / 2, 0, 'XYZ'),
    //   top: new THREE.Euler(0, 0, 0, 'XYZ')
    // }
    //
    // // 修改init函数，在加载完对象后存储它们的初始状态
    // private storeInitialState (object: THREE.Object3D) {
    //   // 存储当前的位置、旋转和缩放
    //   const initialState = {
    //     position: object.position.clone(),
    //     rotation: object.rotation.clone(),
    //     scale: object.scale.clone()
    //   }
    //   this.initialStates.set(object, initialState)
    // }
    //
    // // 修改setView函数，首先重置到初始状态，然后应用视图转换
    // public setView (viewName: string) {
    //   const transformation = this.VIEW_TRANSFORMATIONS[viewName]
    //   if (!transformation) return
    //
    //   this.scene.traverse((object) => {
    //     if (object instanceof THREE.Mesh && this.initialStates.has(object)) {
    //       const initialState = this.initialStates.get(object)
    //       if (initialState) {
    //         console.log('initialState')
    //         console.log(initialState.position)
    //         console.log(initialState.position)
    //         console.log(initialState.scale)
    //         // 重置到初始状态
    //         object.position.copy(initialState.position)
    //         object.rotation.copy(initialState.rotation)
    //         object.scale.copy(initialState.scale)
    //
    //         // 应用预定义的视角转换
    //         object.rotation.x = transformation.x
    //         object.rotation.y = transformation.y
    //         object.rotation.z = transformation.z
    //         object.rotation.order = transformation.order
    //       }
    //     }
    //   })
    //
    //   // 重新渲染场景
    //   this.renderer.render(this.scene, this.camera)
    // }

    setColor (color: string) {
      this.selectedColor = color
      this.renderer.setClearColor(this.selectedColor, 1)
      this.resetRender()
    }
    /**
   * 检查数据是脑区还是神经元
   * @param data 脑区数据或者神经元数据
   * @return boolean 返回true为神经元，返回false则为脑区
   */
    public ifNeuron (data: neuronSceneComponent) {
      return data.name.indexOf('basal') !== -1 || data.name.indexOf('axon') !== -1 || data.name.indexOf('apical') !== -1 || data.name.indexOf('local') !== -1 || data.name.indexOf('arbor0') !== -1 || data.name.indexOf('arbor1') !== -1 || data.name.indexOf('arbor2') !== -1 || data.name.indexOf('arbor3') !== -1
    }

    /**
   * 利用three.js加载要渲染的脑区或者神经元
   * @param data 脑区数据或者神经元数据
   */
    public async loadComponent (data: neuronSceneComponent) {
      if (data.hasOwnProperty('src')) {
        if (this.checkLoadComponent(data)) {
          return
        }
        if (this.ifNeuron(data)) {
          await this.loadObj(data)
        } else {
          await this.loadVtk(data)
        }
      }
    }

    /**
   * 卸载要渲染的脑区或者神经元
   * @param data 脑区数据或者神经元数据
   */
    public unLoadComponent (data: neuronSceneComponent) {
      if (this.ifNeuron(data)) {
        this.unloadObj(data.id)
      } else {
        this.unloadVtk(data.id)
      }
      this.resetRender()
    }

    /**
   * 检查组件是否被加载过
   * @param data 脑区数据或者神经元数据
   */
    public checkLoadComponent (data: neuronSceneComponent) {
      if (this.ifNeuron(data)) {
        return this.neuronDataMap.has(data.id)
      } else {
        return this.brainComponentMap.has(data.id)
      }
    }

    /**
   * 加载vtk文件
   * @param data 脑区数据
   */
    public async loadVtk (data: neuronSceneComponent) {
      console.log('loadVTK')
      console.log(data.src)
      return new Promise((resolve, reject) => {
        const loader = new VTKLoader()
        loader.load(
          data.src,
          (geometry: any) => {
            let material = new THREE.MeshPhongMaterial()
            // 开启透明属性
            material.transparent = true
            material.opacity = 0.3
            // 使外面的模型不遮挡里面的模型
            material.depthWrite = false
            if (data.hasOwnProperty('rgb_triplet')) {
              material.color = new THREE.Color(`rgb(${data.rgb_triplet[0]}, ${data.rgb_triplet[1]}, ${data.rgb_triplet[2]})`)
            }
            console.log(material.color)
            if (data.name === 'root') {
              material.opacity = 0.15
              geometry.computeBoundingBox()
              geometry.boundingBox.getCenter(this.centerShift).negate()
              geometry.center()

              // 获取 VTK 对象的边界
              const boundingBox = geometry.boundingBox
              const min = boundingBox.min
              const max = boundingBox.max

              // 计算 VTK 对象左上角的位置
              const vtkTopLeft = new THREE.Vector3(min.x + Math.abs(min.x) / 5, max.y + Math.abs(min.y) / 15, max.z + Math.abs(min.z) / 5)

              // 创建并调整箭头
              const arrowLength = 45
              const arrowHeadLength = 10
              const arrowHeadWidth = 5

              const arrowP = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), vtkTopLeft, arrowLength, 0xff0000, arrowHeadLength, arrowHeadWidth) // X轴，红色
              const arrowV = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), vtkTopLeft, arrowLength, 0x00ff00, arrowHeadLength, arrowHeadWidth) // Y轴，绿色
              const arrowR = new THREE.ArrowHelper(new THREE.Vector3(0, 0, 1), vtkTopLeft, arrowLength, 0x0000ff, arrowHeadLength, arrowHeadWidth) // Z轴，蓝色
              arrowV.rotateX(Math.PI)
              arrowR.rotateX(Math.PI)

              this.scene.add(arrowP)
              this.scene.add(arrowV)
              this.scene.add(arrowR)

              // 创建标识文本
              const labels = this.addAxisLabels()
              const offset = 55
              // 设置标识文本的位置
              labels[0].position.set(vtkTopLeft.x + offset, vtkTopLeft.y, vtkTopLeft.z) // P
              labels[1].position.set(vtkTopLeft.x - offset, vtkTopLeft.y, vtkTopLeft.z) // A
              labels[2].position.set(vtkTopLeft.x, vtkTopLeft.y - offset, vtkTopLeft.z) // V
              labels[3].position.set(vtkTopLeft.x, vtkTopLeft.y + offset, vtkTopLeft.z) // D
              labels[4].position.set(vtkTopLeft.x, vtkTopLeft.y, vtkTopLeft.z - offset) // R
              labels[5].position.set(vtkTopLeft.x, vtkTopLeft.y, vtkTopLeft.z + offset) // L

              // 确保箭头和标识文本相对 VTK 对象的左上角位置保持固定
              this.renderer.setAnimationLoop(() => {
                arrowP.position.copy(vtkTopLeft)
                arrowV.position.copy(vtkTopLeft)
                arrowR.position.copy(vtkTopLeft)

                this.renderer.render(this.scene, this.camera)
              })
            } else {
              geometry.translate(this.centerShift.x, this.centerShift.y, this.centerShift.z)
            }
            geometry.computeVertexNormals()
            // 绕x轴翻转180度，使得一开始脑为正方向
            geometry.rotateX(Math.PI)
            let mesh = new THREE.Mesh(geometry, material)
            mesh.name = data.name
            if (this.brainComponentMap.has(data.id)) {
              this.unloadVtk(data.id)
            }
            this.brainComponentMap.set(data.id, mesh)
            this.scene.add(mesh)
            this.resetRender()
            resolve(true)
          },
          () => {},
          (err: any) => { reject(err) }
        )
      })
    }

    // eslint-disable-next-line camelcase
    public updateVtkColor (id: string, rgb_triplet: [number, number, number]) {
      if (this.brainComponentMap.has(id)) {
        const mesh = this.brainComponentMap.get(id)
        if (mesh) {
          const newColor = new THREE.Color(`rgb(${rgb_triplet[0]}, ${rgb_triplet[1]}, ${rgb_triplet[2]})`)
          mesh.material.color = newColor
          mesh.material.needsUpdate = true // Ensure the material updates
          console.log(`Updated color of ${id} to ${newColor.getStyle()}`)
          this.resetRender() // Optional: re-render the scene if needed
        } else {
          console.error(`Mesh not found for ID: ${id}`)
        }
      } else {
        console.error(`No component found with ID: ${id}`)
      }
    }

    // 创建标识文本的函数
    private createLabel (text: string): THREE.Sprite {
      const canvas = document.createElement('canvas')
      canvas.width = 512 // 增加画布大小以提高分辨率
      canvas.height = 256
      const context = canvas.getContext('2d')
      if (context) {
        context.font = 'bold 100px Arial'
        context.fillStyle = 'black'
        context.fillText(text, 100, 150) // 调整位置使文本居中

        const texture = new THREE.CanvasTexture(canvas)
        const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true })
        const sprite = new THREE.Sprite(spriteMaterial)
        sprite.scale.set(20, 10, 1) // 调整大小以适应画布
        return sprite
      }
      throw new Error('Canvas context is null')
    }

    // 添加标识文本
    private addAxisLabels (): THREE.Sprite[] {
      const labels = [
        this.createLabel('P'),
        this.createLabel('A'),
        this.createLabel('V'),
        this.createLabel('D'),
        this.createLabel('R'),
        this.createLabel('L')
      ]
      labels.forEach(label => this.scene.add(label))
      return labels
    }

    // public async loadVtk (data: neuronSceneComponent) {
    //   console.log('loadVTK')
    //   console.log(data.src)
    //   return new Promise((resolve, reject) => {
    //     const loader = new VTKLoader()
    //     loader.load(
    //       data.src,
    //       (geometry: any) => {
    //         let material = new THREE.MeshPhongMaterial()
    //         // 开启透明属性
    //         material.transparent = true
    //         material.opacity = 0.3
    //         // 使外面的模型不遮挡里面的模型
    //         material.depthWrite = false
    //         if (data.hasOwnProperty('rgb_triplet')) {
    //           material.color = new THREE.Color(`rgb(${data.rgb_triplet[0]}, ${data.rgb_triplet[1]}, ${data.rgb_triplet[2]})`)
    //         }
    //         console.log(material.color)
    //         if (data.name === 'root') {
    //           material.opacity = 0.15
    //           geometry.computeBoundingBox()
    //           geometry.boundingBox.getCenter(this.centerShift).negate()
    //           geometry.center()
    //
    //           // 创建并调整坐标轴
    //           let axesHelper = new THREE.AxesHelper(45) // 设置坐标轴大小
    //           axesHelper.rotateY(Math.PI) // Y轴旋转180度，使得X轴指向P，背侧是A
    //           axesHelper.rotateZ(Math.PI)
    //           this.scene.add(axesHelper)
    //
    //           // 将坐标轴移动到左下角
    //           axesHelper.position.set(-this.renderer.domElement.width / 2 + 650, -this.renderer.domElement.height / 2 + 700, this.renderer.domElement.height / 2 - 300)
    //
    //           // 添加标识文本
    //           this.addAxisLabels(axesHelper.position)
    //         } else {
    //           geometry.translate(this.centerShift.x, this.centerShift.y, this.centerShift.z)
    //         }
    //         geometry.computeVertexNormals()
    //         // 绕x轴翻转180度，使得一开始脑为正方向
    //         geometry.rotateX(Math.PI)
    //         let mesh = new THREE.Mesh(geometry, material)
    //         mesh.name = data.name
    //         if (this.brainComponentMap.has(data.id)) {
    //           this.unloadVtk(data.id)
    //         }
    //         this.brainComponentMap.set(data.id, mesh)
    //         this.scene.add(mesh)
    //         this.resetRender()
    //         resolve(true)
    //       },
    //       () => {},
    //       (err: any) => { reject(err) }
    //     )
    //   })
    // }
    //
    // // 创建标识文本的函数
    // private createLabel (text: string, position: THREE.Vector3): THREE.Sprite {
    //   const canvas = document.createElement('canvas')
    //   canvas.width = 512 // 增加画布大小以提高分辨率
    //   canvas.height = 256
    //   const context = canvas.getContext('2d')
    //   if (context) {
    //     context.font = 'bold 100px Arial'
    //     context.fillStyle = 'black'
    //     context.fillText(text, 100, 150) // 调整位置使文本居中
    //
    //     const texture = new THREE.CanvasTexture(canvas)
    //     const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true })
    //     const sprite = new THREE.Sprite(spriteMaterial)
    //     sprite.scale.set(20, 10, 1) // 调整大小以适应画布
    //     sprite.position.copy(position)
    //     return sprite
    //   }
    //   throw new Error('Canvas context is null')
    // }
    //
    // // 添加标识文本
    // private addAxisLabels (axesPosition: THREE.Vector3) {
    //   const offset = 45 // 控制标识与坐标轴的距离，适应缩小后的坐标轴
    //   const labels = [
    //     { text: 'A', position: new THREE.Vector3(axesPosition.x - offset, axesPosition.y, axesPosition.z) }, // x轴正方向
    //     { text: 'P', position: new THREE.Vector3(axesPosition.x + offset, axesPosition.y, axesPosition.z) }, // x轴负方向
    //     { text: 'V', position: new THREE.Vector3(axesPosition.x, axesPosition.y - offset, axesPosition.z) }, // y轴正方向
    //     { text: 'D', position: new THREE.Vector3(axesPosition.x, axesPosition.y + offset, axesPosition.z) }, // y轴负方向
    //     { text: 'L', position: new THREE.Vector3(axesPosition.x, axesPosition.y, axesPosition.z + offset) }, // z轴负方向
    //     { text: 'R', position: new THREE.Vector3(axesPosition.x, axesPosition.y, axesPosition.z - offset) } // z轴正方向
    //   ]
    //
    //   labels.forEach(label => {
    //     const sprite = this.createLabel(label.text, label.position)
    //     this.scene.add(sprite)
    //   })
    // }

    // public async loadVtk (data: neuronSceneComponent) {
    //   console.log('loadVTK')
    //   console.log(data.src)
    //   return new Promise((resolve, reject) => {
    //     const loader = new VTKLoader()
    //     loader.load(
    //       data.src,
    //       (geometry: any) => {
    //         let material = new THREE.MeshPhongMaterial()
    //         // 开启透明属性
    //         material.transparent = true
    //         material.opacity = 0.3
    //         // 使外面的模型不遮挡里面的模型
    //         material.depthWrite = false
    //         if (data.hasOwnProperty('rgb_triplet')) {
    //           material.color = new THREE.Color(`rgb(${data.rgb_triplet[0]}, ${data.rgb_triplet[1]}, ${data.rgb_triplet[2]})`)
    //         }
    //         console.log(material.color)
    //         if (data.name === 'root') {
    //           material.opacity = 0.15
    //           geometry.computeBoundingBox()
    //           // console.log('bounding box', geometry.boundingBox)
    //           geometry.boundingBox.getCenter(this.centerShift).negate()
    //           geometry.center()
    //           let axesHelper = new THREE.AxesHelper(100)
    //           axesHelper.rotateX(Math.PI)
    //           axesHelper.translateOnAxis(new THREE.Vector3().copy(this.centerShift).normalize(), this.centerShift.length())
    //           this.scene.add(axesHelper)
    //         // console.log('center shift: ', this.centerShift)
    //         } else {
    //           geometry.translate(this.centerShift.x, this.centerShift.y, this.centerShift.z)
    //         }
    //         geometry.computeVertexNormals()
    //         // 绕x轴翻转180度，使得一开始脑为正方向
    //         geometry.rotateX(Math.PI)
    //         let mesh = new THREE.Mesh(geometry, material)
    //         mesh.name = data.name
    //         if (this.brainComponentMap.has(data.id)) {
    //           this.unloadVtk(data.id)
    //         }
    //         this.brainComponentMap.set(data.id, mesh)
    //         // this.storeInitialState(mesh)
    //         this.scene.add(mesh)
    //         this.resetRender()
    //         resolve(true)
    //       },
    //       () => {},
    //       (err: any) => { reject(err) }
    //     )
    //   })
    // }

    /**
   * 卸载vtk文件
   * @param dataId 脑区id
   */
    public unloadVtk (dataId: any) {
      if (this.brainComponentMap.has(dataId)) {
        const group = this.brainComponentMap.get(dataId)
        group.traverse(function (obj: any) {
          if (obj.type === 'Mesh' || obj.type === 'LineSegments') {
            obj.geometry.dispose()
            obj.material.dispose()
          }
        })
        this.scene.remove(group)
        this.brainComponentMap.delete(dataId)
      }
    }

    /**
   * 加载obj文件
   * @param data 神经元数据
   */
    public async loadObj (data: any) {
      await this.waitRootLoaded()
      return new Promise((resolve, reject) => {
        const loader = new OBJLoader()
        loader.load(
          data.src,
          (obj: any) => {
            this.neuronData.push(data)
            // obj.children[0].material = new LineMaterial({
            //   linewidth: 100
            // })
            // obj.children[0].material.resolution.set(window.innerWidth, window.innerHeight)
            if (data.hasOwnProperty('rgb_triplet')) {
            // material.color = new THREE.Color(`rgb(${data.rgb_triplet[0]}, ${data.rgb_triplet[1]}, ${data.rgb_triplet[2]})`)
              obj.children[0].material.color = new THREE.Color(`rgb(${data.rgb_triplet[0]}, ${data.rgb_triplet[1]}, ${data.rgb_triplet[2]})`)
              if (data.id > 0) {
                obj.children[0].material.linewidth = 100
                obj.children[0].material.transparent = true
                obj.children[0].material.opacity = 0.3
              }
            }
            obj.children[0].geometry.translate(this.centerShift.x, this.centerShift.y, this.centerShift.z)
            // 绕x轴翻转180度，与脑一致
            obj.children[0].geometry.rotateX(Math.PI)
            if (this.neuronDataMap.has(data.id)) {
              this.unloadObj(data.id)
            }
            if (data.hasOwnProperty('info')) {
              this.neuronInfoMap.set(data.id, data.info)
            }
            obj.children[0].name = data.name
            this.neuronDataMap.set(data.id, obj)
            // this.storeInitialState(obj)
            this.scene.add(obj)
            // console.log(obj)
            this.loadedObj = obj // 保存加载的对象
            this.resetRender()
            resolve(true)
          },
          () => {},
          (err: any) => { reject(err) }
        )
      })
    }

    // eslint-disable-next-line camelcase
    public updateObjColor (id: number, rgb_triplet: [number, number, number]): void {
      if (this.neuronDataMap.has(id)) {
        const obj = this.neuronDataMap.get(id)

        if (obj && obj.children && obj.children[0] && obj.children[0].material) {
          // Update the color of the material
          obj.children[0].material.color = new THREE.Color(`rgb(${rgb_triplet[0]}, ${rgb_triplet[1]}, ${rgb_triplet[2]})`)

          // If the object has transparency settings or other material properties, you can modify them here as well
          // For example, if you want to update opacity or linewidth
          if (obj.children[0].material.transparent) {
            obj.children[0].material.opacity = 0.5 // Or any other value
          }
          obj.children[0].material.needsUpdate = true // Ensure the material is updated in the scene
          this.resetRender() // Re-render the scene if necessary
        } else {
          console.error('Object or material not found for the given ID:', id)
        }
      } else {
        console.error('Object with the given ID not found:', id)
      }
    }

    public async loadPointObj (data: string) {
      console.log(data)
      // await this.waitRootLoaded()
      return new Promise((resolve, reject) => {
        const loader = new OBJLoader()
        loader.load(
          './test.obj',
          (obj: any) => {
            let material = new LineMaterial()
            obj.children[0].material.color.set(0xff0000)
            obj.children[0].geometry.translate(this.centerShift.x, this.centerShift.y, this.centerShift.z)
            // 绕x轴翻转180度，与脑一致
            obj.children[0].geometry.rotateX(Math.PI)
            this.scene.add(obj)
            // console.log(obj)
            // this.resetRender()
            resolve(true)
          },
          () => {},
          (err: any) => { reject(err) }
        )
      })
    }

    /**
   * 卸载obj文件
   * @param dataId 神经元的id
   */
    public unloadObj (dataId: any) {
      if (this.neuronDataMap.has(dataId)) {
        const group = this.neuronDataMap.get(dataId)
        group.traverse(function (obj: any) {
          if (obj.type === 'Mesh' || obj.type === 'LineSegments') {
            obj.geometry.dispose()
            obj.material.dispose()
          }
        })
        this.scene.remove(group)
      }
    }

    /**
   * 卸载当前所有神经元组件
   */
    public unloadAllNeuron () {
      for (let neuronId of this.neuronDataMap.keys()) {
        this.unloadObj(neuronId)
      }
      this.neuronDataMap.clear()
    }

    /**
   * 加载树突
   * @param data 树突数据
   */
    public loadDendrite (data: neuronSceneComponent) {
      this.camera.position.set(0, 0, 25)
      return new Promise((resolve, reject) => {
        const loader = new OBJLoader()
        loader.load(
          data.src,
          (obj: any) => {
            this.neuronData.push(data)
            if (data.name.indexOf('axon') !== -1) {
              obj.children[0].material.color.set(0xff0000)
            } else if (data.name.indexOf('basal') !== -1) {
              obj.children[0].material.color.set(0x0000ff)// 0x0000ff
            } else if (data.name.indexOf('apical') !== -1) {
              obj.children[0].material.color.set(0xff00ff)
            }
            obj.children[0].geometry.center()
            if (this.neuronDataMap.has(data.id)) {
              this.unloadObj(data.id)
            }
            this.neuronDataMap.set(data.id, obj)
            this.scene.add(obj)
            this.resetRender()
            resolve(true)
          },
          () => {},
          (err: any) => { reject(err) }
        )
      })
    }

    public loadDendriteRadius (data: neuronSceneComponent, pointSize: number) {
      this.camera.position.set(0, 0, 25)

      return new Promise((resolve, reject) => {
        const loader = new OBJLoader()
        loader.load(
          data.src,
          (obj: any) => {
            this.neuronData.push(data)

            if (data.name.indexOf('axon') !== -1) {
              const material = new THREE.PointsMaterial({ size: pointSize, color: 0xff0000 })
              obj.children[0].material.dispose() // 清除之前的材质
              obj.children[0].material = material
            } else if (data.name.indexOf('den') !== -1) {
              const material = new THREE.PointsMaterial({ size: pointSize, color: 0xff0000 })
              obj.children[0].material.dispose() // 清除之前的材质
              obj.children[0].material = material
            }

            obj.children[0].geometry.center()

            // 获取BufferGeometry
            const baseGeometry = obj.children[0].geometry
            const positions = baseGeometry.attributes.position.array

            // 获取顶点数
            const numVertices = positions.length / 3

            for (let i = 0; i < numVertices; i++) {
              let vertexSize = pointSize // 基本顶点大小

              // // 如果有自定义顶点大小，请使用它
              // if (customPointSizes.has(i)) {
              //   vertexSize = customPointSizes.get(i)
              // }

              // 修改顶点大小
              obj.children[0].geometry.attributes.size.array[i] = vertexSize
            }

            // 设置更新标志以通知Three.js需要重新渲染材质
            obj.children[0].geometry.attributes.size.needsUpdate = true

            if (this.neuronDataMap.has(data.id)) {
              this.unloadObj(data.id)
            }

            this.neuronDataMap.set(data.id, obj)
            this.scene.add(obj)
            this.resetRender()
            resolve(true)
          },
          () => {},
          (err) => {
            reject(err)
          }
        )
      })
    }

    /**
   * 设置组件是否显示
   * @param component 组件,神经元或者脑区
   * @param flag 是否显示
   */
    public setComponentVisible (component: neuronSceneComponent, flag: boolean) {
      if (this.ifNeuron(component)) {
        if (this.neuronDataMap.has(component.id)) {
          this.neuronDataMap.get(component.id).visible = flag
        }
      } else {
        if (this.brainComponentMap.has(component.id)) {
          this.brainComponentMap.get(component.id).visible = flag
        }
      }
      this.resetRender()
    }

    /**
   * 设置所有神经元是否显示
   * @param flag 是否显示
   */
    public setAllNeuronsVisible (flag: boolean) {
      this.neuronData.forEach((neuron: any) => {
        this.setComponentVisible(neuron, flag)
      })
    }

    /**
   * 等待root脑区加载
   */
    private async waitRootLoaded () {
      while (this.brainComponentMap.size === 0) {
        await sleep(500)
      }
    }

    /**
   * 检查SLice是否被加载过
   * @param sliceName Slice名
   */
    public checkLoadSlice (sliceName: string) {
      return this.sliceMap.has(sliceName)
    }

    /**
     * 加载Slice
     * @param name SLice的方向名称
     * @param atlas
     */
    public loadSlice (name: string, atlas:string) {
      console.log('loadSlice')
      let slice = new Slice(name, atlas, () => {
        this.resetRender()
      })
      slice.mesh.name = name
      this.sliceMap.set(name, slice)
      console.log(this.sliceMap)
      this.scene.add(slice.mesh)
    }

    /**
     * 更新Slice
     * @param name SLice的方向名称
     * @param location Slice的某一层
     * @param atlas
     */
    public updateSlice (name: string, location: number, atlas:string) {
      if (this.sliceMap.has(name)) {
        const slice = this.sliceMap.get(name)
        slice.location = location
        slice.update(location, atlas, () => {
          this.resetRender()
        })
      }
    }

    /**
   * 设置Slice是否显示
   * @param name SLice的方向名称
   * @param flag 是否显示
   */
    public setSliceVisible (name: string, flag: boolean) {
      if (this.sliceMap.has(name)) {
        const slice = this.sliceMap.get(name)
        slice.mesh.visible = flag
        this.resetRender()
      }
    }

    /**
   * NeuronScene初始化
   * @private
   */
    private async init () {
    /* 一、创建场景 */
      this.scene = new THREE.Scene()
      const el = this.$refs.NeuronScene as Element
      /* 二、添加光源 */
      const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5)
      this.scene.add(directionalLight)
      //  环境光
      const ambient = new THREE.AmbientLight(0x444444)
      this.scene.add(ambient)
      /* 三、相机设置 */
      this.camera = new THREE.PerspectiveCamera(75, el.clientWidth / el.clientHeight, 0.1, 100000)
      this.camera.position.set(0, 0, 500)
      this.camera.lookAt(this.scene.position)
      this.camera.zoom = 1.2
      /* 四、渲染设置 */
      this.renderer = new THREE.WebGLRenderer({ antialias: true })
      this.renderer.setSize(el.clientWidth, el.clientHeight)
      // this.renderer.setClearColor(0xeeeeee, 1)
      this.renderer.setClearColor(this.selectedColor, 1)
      el.appendChild(this.renderer.domElement)
      this.resetRender()

      /* 四、控制器设置 */
      this.controls = new TrackballControls(this.camera, this.renderer.domElement)
      this.controls.maxDistance = 10000
      this.controls.staticMoving = true
      this.controls.rotateSpeed = 10
      this.controls.panSpeed = 1
      this.controls.zoomSpeed = 2
      this.controls.addEventListener('change', () => {
        this.resetRender()
      })

      // 初始化数据
      this.brainComponentMap = new Map<any, any>()
      this.neuronDataMap = new Map<any, any>()
      this.neuronInfoMap = new Map<any, any>()
      this.sliceMap = new Map<any, any>()
      this.centerShift = new THREE.Vector3()

      // 监听Neuron scene尺寸变化
      if (!this.resizeObserve) {
      // @ts-ignore
        this.resizeObserve = new ResizeObserver(entries => {
          for (const entry of entries) {
            switch (entry.target) {
              case el:
                if (!this.debounceOnSceneResize) {
                  this.debounceOnSceneResize = debounce(this.onSceneResize, 500)
                }
                this.debounceOnSceneResize()
            }
          }
        })
        this.resizeObserve.observe(el)
      }

      // 调用动画
      this.animate()
    }

    /**
   * 获取鼠标点击射线的物体，并高亮第一个有效的物体，且显示其名字
   * @event 鼠标事件
   * @private
   */
    private highlightObject (event: any) {
      event.preventDefault()
      const el = this.$refs.NeuronScene as Element
      let rayCaster = new THREE.Raycaster()
      let mouse = new THREE.Vector2()
      mouse.x = (event.offsetX / el.clientWidth) * 2 - 1
      mouse.y = -(event.offsetY / el.clientHeight) * 2 + 1

      console.log(this.camera)
      rayCaster.setFromCamera(mouse, this.camera)

      let intersects = rayCaster.intersectObjects(this.scene.children)

      if (this.selectComponent) {
        this.selectComponent.material = this.selectComponentMaterial
        this.selectComponent = null
      }

      if (this.roiBall && this.roiBall.visible) {
        for (let intersect of intersects) {
          if (intersect.object.name !== 'root' && intersect.object.visible) {
            this.updateROIBall((intersect.point.x - this.centerShift.x) * 25, (-intersect.point.y - this.centerShift.y) * 25, (-intersect.point.z - this.centerShift.z) * 25, this.roiBall.geometry.parameters.radius * 25)
            break
          }
        }
      } else {
        for (let intersect of intersects) {
          if (intersect.object.name !== 'root' && intersect.object.visible) {
            this.selectComponent = intersect.object
            this.selectComponentMaterial = this.selectComponent.material.clone()
            this.selectComponent.material = new THREE.MeshPhongMaterial({
              color: 0xffffff * Math.random(),
              transparent: this.selectComponentMaterial.transparent,
              opacity: 0.9
            })
            break
          }
        }
      }
      this.resetRender()
    }

    /**
   * Scene窗口变化的回调函数
   * @private
   */
    private onSceneResize () {
      const el = this.$refs.NeuronScene as Element
      this.camera.aspect = el.clientWidth / el.clientHeight
      this.camera.updateProjectionMatrix()
      this.renderer.setSize(el.clientWidth, el.clientHeight)
      this.resetRender()
    }

    /**
   * 鼠标双击的回调函数，用于highlight渲染的组件，并显示出该组件的名字
   * @event 鼠标事件
   */
    public handleMouseDoubleClick (event: any) {
      event.preventDefault()
      const el = this.$refs.NeuronScene as Element
      console.log('el', el)
      console.log(event)
      this.pStyle['--top'] = event.offsetY + 'px'
      this.pStyle['--right'] = el.clientWidth - event.offsetX + 5 + 'px'
      this.neuronTipStyle['--bottom'] = el.clientHeight - event.offsetY - 5 + 'px'
      this.neuronTipStyle['--left'] = event.offsetX + 10 + 'px'
      // this.highlightObject(event)
      this.highlightNeuron(event)
      return this.roiBall ? [(this.roiBall.position.x - this.centerShift.x) * 25, (-this.roiBall.position.y - this.centerShift.y) * 25, (-this.roiBall.position.z - this.centerShift.z) * 25] : [0, 0, 0]
    }

    /**
   * 获取鼠标点击神经元，并弹出一个弹窗来显示该神经元的信息
   * @event 鼠标事件
   * @private
   */
    private highlightNeuron (event: any) {
      console.log('highlightNeuron')
      event.preventDefault()
      const el = this.$refs.NeuronScene as Element
      let rayCaster = new THREE.Raycaster()
      let mouse = new THREE.Vector2()
      mouse.x = (event.offsetX / el.clientWidth) * 2 - 1
      mouse.y = -(event.offsetY / el.clientHeight) * 2 + 1

      rayCaster.setFromCamera(mouse, this.camera)

      let intersects = rayCaster.intersectObjects(this.scene.children)

      if (this.selectNeuron) {
        this.neuronTipVisible = false
        this.selectNeuron.material = this.selectNeuronMaterial
        this.selectNeuron = null
      }

      if (this.roiBall && this.roiBall.visible) {
        for (let intersect of intersects) {
          if (intersect.object.name !== 'root' && intersect.object.visible) {
            this.updateROIBall((intersect.point.x - this.centerShift.x) * 25, (-intersect.point.y - this.centerShift.y) * 25, (-intersect.point.z - this.centerShift.z) * 25, this.roiBall.geometry.parameters.radius * 25)
            break
          }
        }
      } else {
        for (let intersect of intersects) {
          console.log(intersect.object)
          if (intersect.object.visible && (intersect.object.name.indexOf('den') !== -1 || intersect.object.name.indexOf('axon') !== -1)) {
            this.selectNeuron = intersect.object
            this.selectNeuronMaterial = this.selectNeuron.material.clone()
            this.selectNeuron.material.color = new THREE.Color(0, 255, 0)
            this.selectNeuronInfo = this.neuronInfoMap.get(this.selectNeuron.name)
            this.neuronTipVisible = true
            break
          }
        }
      }
      this.resetRender()
    }

    /**
   * 鼠标双击的回调函数，用于highlight渲染的组件，并显示出该组件的名字
   * @event 鼠标事件
   */
    public handleMouseDoubleClickNeuron (event: any) {
      console.log('handleMouseDoubleClickNeuron')
      event.preventDefault()
      const el = this.$refs.NeuronScene as Element
      this.neuronTipStyle['--bottom'] = el.clientHeight - event.offsetY - 5 + 'px'
      this.neuronTipStyle['--left'] = event.offsetX + 10 + 'px'
      this.highlightNeuron(event)
      return this.roiBall ? [(this.roiBall.position.x - this.centerShift.x) * 25, (-this.roiBall.position.y - this.centerShift.y) * 25, (-this.roiBall.position.z - this.centerShift.z) * 25] : [0, 0, 0]
    }

    public handleMouseRightClick (event: any) {
      console.log('handleMouseRightClick')
      event.preventDefault()
      const el = this.$refs.NeuronScene as Element
      this.neuronTipStyle['--bottom'] = el.clientHeight - event.offsetY - 5 + 'px'
      this.neuronTipStyle['--left'] = event.offsetX + 10 + 'px'
      this.rightClickHighlightNeuron(event)
    }

    private rightClickHighlightNeuron (event: any) {
      console.log('rightClickHighlightNeuron')
      event.preventDefault()
      const el = this.$refs.NeuronScene as Element
      let rayCaster = new THREE.Raycaster()
      let mouse = new THREE.Vector2()
      mouse.x = (event.offsetX / el.clientWidth) * 2 - 1
      mouse.y = -(event.offsetY / el.clientHeight) * 2 + 1

      rayCaster.setFromCamera(mouse, this.camera)

      let intersects = rayCaster.intersectObjects(this.scene.children)

      if (this.selectNeuron) {
        this.neuronTipVisible = false
        this.selectNeuron.material = this.selectNeuronMaterial
        this.selectNeuron = null
      }
      for (let intersect of intersects) {
        console.log(intersect.object)
        if (intersect.object.visible && (intersect.object.name.indexOf('den') !== -1 || intersect.object.name.indexOf('axon') !== -1)) {
          this.selectNeuron = intersect.object
          this.selectNeuronMaterial = this.selectNeuron.material.clone()
          this.selectNeuron.material.color = new THREE.Color(0, 255, 0)
          this.selectNeuronInfo = this.neuronInfoMap.get(this.selectNeuron.name)
          this.neuronTipVisible = true
          break
        }
      }
      this.resetRender()
    }

    /**
   * 点击查看neuron info，跳转到neuron info栏
   * @param selectNeuron 神经元信息
   */
    private neuronViewHandler (selectNeuron: any) {
      this.neuronTipVisible = false
      this.$emit('neuronView', selectNeuron)
    }

    /**
   * three.js绘制函数
   * @private
   */
    private resetRender () {
      this.renderer.render(this.scene, this.camera)
    }

    /**
   * 动画，需要一直更新control，否则它不工作
   * @private
   */
    private animate () {
      requestAnimationFrame(this.animate)
      this.controls.update()
      this.resetRender()
    }

    /**
   * 修改该组件的z平面，进行隐藏或展示的切换
   */
    public switchZIndex () {
      this.pStyle['--zIndex'] = -this.pStyle['--zIndex']
    }

    /**
   * 加载代表ROI的小球
   * @param r ROI的半径
   */
    public loadROIBall (r: number) {
      const geometry = new THREE.SphereGeometry(r / 25, 32, 16)
      const material = new THREE.MeshBasicMaterial({ color: 0xff00ff })
      material.transparent = true
      material.opacity = 0.3
      this.roiBall = new THREE.Mesh(geometry, material)
      this.roiBall.position = new THREE.Vector3()
      this.scene.add(this.roiBall)
    }
    /**
   * 加载代表ROI的小球
   * @param r ROI的半径
   */
    public loadSoma (r: number = 100) {
      const geometry = new THREE.SphereGeometry(r / 25, 32, 16)
      const material = new THREE.MeshBasicMaterial({ color: 0x000000 })
      material.transparent = true
      material.opacity = 0.3
      this.somaBall = new THREE.Mesh(geometry, material)
      this.somaBall.position = new THREE.Vector3()
      this.scene.add(this.somaBall)
    }

    public loadMultiSoma (neuronId:string, x:number, y:number, z:number, r: number = 100) {
      const geometry = new THREE.SphereGeometry(r / 25, 32, 16)
      const material = new THREE.MeshBasicMaterial({ color: 0x000000 })
      material.transparent = true
      material.opacity = 0.3
      const somaBall = new THREE.Mesh(geometry, material)

      // // 计算位置并设置
      // const somaPos = new THREE.Vector3(
      //   Math.round(x) / 25 + this.centerShift.x,
      //   -Math.round(y) / 25 - this.centerShift.y,
      //   -Math.round(z) / 25 - this.centerShift.z
      // )
      // somaBall.position.x = somaPos.x
      // somaBall.position.y = somaPos.y
      // somaBall.position.z = somaPos.z
      somaBall.position.set(0, 0, 0)
      this.scene.add(somaBall)
      return somaBall
    }
    /**
   * 卸载代表ROI的小球
   */
    public unloadROIBall () {
      this.scene.remove(this.roiBall)
      this.roiBall = null
    }

    public unloadSomaBall () {
      this.scene.remove(this.somaBall)
      this.somaBall = null
    }

    /**
   * 设置代表ROI的小球是否显示
   */
    public setROIBallVisible (flag: boolean) {
      if (this.roiBall) {
        this.roiBall.visible = flag
      }
    }

    public setSomaBallVisible (flag: boolean) {
      if (this.somaBall) {
        this.somaBall.visible = flag
      }
    }
    /**
     * 显示map中的小球
     */
    public showMap (r: number) {
      console.log('showmap')
      let points = null
      let lines = null
      const pointGeometry = new THREE.BufferGeometry()
      const lineGeometry = new THREE.BufferGeometry()
      const material = new THREE.LineBasicMaterial({ color: 0xffffff })

      const pointsArray = [
        0, 0, 0,
        1, 1, 1,
        -1, 1, -1,
        2, 2, 2
      ]

      pointGeometry.setAttribute('position', new THREE.Float32BufferAttribute(pointsArray, 3))
      points = new THREE.Points(pointGeometry, material)

      const lineIndices = [
        0, 1,
        1, 2,
        2, 3,
        3, 0
      ]

      lineGeometry.setIndex(lineIndices)
      lines = new THREE.LineSegments(lineGeometry, material)

      // 添加点和线到场景
      this.scene.add(points)
      this.scene.add(lines)

      this.camera.position.z = 5

      // 渲染场景
      const animate = () => {
        requestAnimationFrame(animate)
        this.renderer.render(this.scene, this.camera)
      }

      animate()
    }
    /**
   * 显示代表ROI的小球
   */
    public showROIBall (r: number) {
      if (this.roiBall) {
        this.setROIBallVisible(true)
        return null
      } else {
        this.loadROIBall(r)
        return [-this.centerShift.x * 25, -this.centerShift.y * 25, -this.centerShift.z * 25]
      }
    }

    public showSomaBall (r: number) {
      if (this.somaBall) {
        this.setSomaBallVisible(true)
        return null
      } else {
        this.loadSoma(100)
        return [-this.centerShift.x * 25, -this.centerShift.y * 25, -this.centerShift.z * 25]
      }
    }

    public showMultiViewerSomaBall (neuronId:string, r: number = 100, flag:boolean) {
      console.log(this.multiViewerSoma.get(neuronId))
      if (this.multiViewerSoma.get(neuronId)) {
        this.multiViewerSoma.get(neuronId).visible = flag
        return null
      } else {
        if (this.multiViewerSomaPos.get(neuronId)) {
          const somaPos = this.multiViewerSomaPos.get(neuronId)
          if (somaPos) {
            this.mSomaBall = this.loadMultiSoma(somaPos[0], somaPos[1], somaPos[2], 100)
            this.mSomaBall.visible = flag
            this.mSomaBall.position = new THREE.Vector3(somaPos[0] / 25 + this.centerShift.x, -somaPos[1] / 25 - this.centerShift.y, -somaPos[2] / 25 - this.centerShift.z)
            this.multiViewerSoma.set(neuronId, this.mSomaBall)
          }
          return null
        }
      }
    }

    public unloadMultiViewerSomaBall () {
      this.multiViewerSoma.forEach((neuronID:string, soma: any) => {
        this.scene.remove(soma)
        soma = null
      })
    }

    public unloadMultiViewerSomaBalls (neuronId:string) {
      let soma = this.multiViewerSoma.get(neuronId)
      this.scene.remove(soma)
      soma = null
    }

    /**
   * 更新ROI的状态
   * @param x ROI在标准脑坐标系下的x坐标
   * @param y ROI在标准脑坐标系下的y坐标
   * @param z ROI在标准脑坐标系下的z坐标
   * @param r ROI的半径
   */
    public updateROIBall (x: number, y: number, z: number, r: number) {
      if (this.roiBall.geometry.parameters.radius !== r) {
        this.unloadROIBall()
        this.loadROIBall(r)
      }
      this.roiBall.position = new THREE.Vector3(x / 25 + this.centerShift.x, -y / 25 - this.centerShift.y, -z / 25 - this.centerShift.z)
    }

    public updateSomaBall (x: number, y: number, z: number, r: number) {
      if (this.somaBall.geometry.parameters.radius !== r) {
        this.unloadSomaBall()
        this.loadSoma(r)
      }
      this.somaBall.position = new THREE.Vector3(x / 25 + this.centerShift.x, -y / 25 - this.centerShift.y, -z / 25 - this.centerShift.z)
    }

    public updateMultiViewerSomaBall (x: number, y: number, z: number, r: number) {
      this.somaBall.position = new THREE.Vector3(x / 25 + this.centerShift.x, -y / 25 - this.centerShift.y, -z / 25 - this.centerShift.z)
    }
    public destroyed () {
      this.resizeObserve.disconnect()
    }

    public toggleRotation () {
      this.isRotating = !this.isRotating
      if (this.isRotating) {
        this.playAnimate()
      }
    }

    public playAnimate () {
      if (!this.isRotating) return // 如果不应该旋转，则直接返回

      requestAnimationFrame(this.animate)
      if (this.loadedObj) {
        this.loadedObj.rotation.y += 10
        this.renderer.render(this.scene, this.camera)
      }
    }
}
</script>

<style scoped lang="less">
.neuron-scene {
  width: 100%;
  height: 100%;
  position: relative;
  z-index: var(--zIndex);
  .position {
    position: absolute;
    top: 0;
    left: 0;
  }
  .neuron-tip {
    width: 200px;
    position: absolute;
    bottom: var(--bottom);
    left: var(--left);
  }
}
.top-button {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 50%;
}
.right-top {
  top: 10px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  z-index: 999;
}
.view_button {
  width:32px;
  height:30px
}
</style>
