import * as THREE from 'three'

const SagittalLimit = 456
const AxialLimit = 320
const CoronalLimit = 528

type SliceSize = [number, number];

const SliceNameList = ['Sagittal', 'Axial', 'Coronal']

const SliceSizeMap = new Map<string, SliceSize>()

SliceSizeMap.set(SliceNameList[0], [AxialLimit, CoronalLimit])
SliceSizeMap.set(SliceNameList[1], [SagittalLimit, CoronalLimit])
SliceSizeMap.set(SliceNameList[2], [SagittalLimit, AxialLimit])

const centerPoint = [SagittalLimit / 2, AxialLimit / 2, CoronalLimit / 2]

export default class Slice {
  public name: string = ''
  public min: number = 0
  public max: number = 0
  public center:number = 0
  public src: string = ''
  public maskSrc: string = ''
  public mesh: any = null
  public geometry: any = null
  public texture: any = null
  public mask: any = null
  public location: number = this.center
  public atlas:string = 'fMOST'

  // eslint-disable-next-line no-useless-constructor
  public constructor (name: string, atlas:string, func: any = () => {}) {
    this.name = name
    this.atlas = atlas
    this.min = 0
    switch (name) {
      case 'Sagittal':
        this.max = SagittalLimit
        break
      case 'Axial':
        this.max = AxialLimit
        break
      case 'Coronal':
        this.max = CoronalLimit
        break
    }
    this.center = this.max / 2

    this.texture = this.creatSliceTexture()
    this.mask = this.creatSliceTexture()

    const material = this.creatSliceMaterial(this.texture, this.mask)
    this.mesh = this.creatSliceMesh(this.name, material)
    this.location = this.center
    this.update(this.location, this.atlas, func)
  }

  public setAtlas (atlas:string) {
    this.atlas = atlas
  }
  /**
   * 更新Slice
   * @param location Slice的某一层
   * @param atlas
   * @param func 回调函数，用于slice加载完后渲染
   */
  public update (location: number, atlas:string, func: any = () => {}) {
    this.setLocation(location)
    const textureDir = '/tmp/ft_local/slices/'
    // const textureDir = '/slices/'
    if (atlas === 'CCFv3') {
      switch (this.name) {
        case 'Sagittal':
          this.src = textureDir + 'CCFv3/brain/sagittal_' + location + '.png'
          this.maskSrc = textureDir + 'CCFv3/mask/sagittal_' + location + '_mask.png'
          break
        case 'Axial':
          this.src = textureDir + 'CCFv3/brain/axial_' + location + '.png'
          this.maskSrc = textureDir + 'CCFv3/mask/axial_' + location + '_mask.png'
          break
        case 'Coronal':
          this.src = textureDir + 'CCFv3/brain/coronal_' + location + '.png'
          this.maskSrc = textureDir + 'CCFv3/mask/coronal_' + location + '_mask.png'
          break
      }
    } else {
      switch (this.name) {
        case 'Sagittal':
          this.src = textureDir + 'fMOST/brain/fmost_sagittal_' + location + '.png'
          this.maskSrc = textureDir + 'fMOST/mask/fmost_sagittal_' + location + '_mask.png'
          break
        case 'Axial':
          this.src = textureDir + 'fMOST/brain/fmost_axial_' + location + '.png'
          this.maskSrc = textureDir + 'fMOST/mask/fmost_axial_' + location + '_mask.png'
          break
        case 'Coronal':
          this.src = textureDir + 'fMOST/brain/fmost_coronal_' + location + '.png'
          this.maskSrc = textureDir + 'fMOST/mask/fmost_coronal_' + location + '_mask.png'
          break
      }
    }
    const loader = new THREE.TextureLoader()
    loader.load(
      this.src,
      (texture) => {
        this.mesh.material.map.image = texture.image
        this.mesh.material.map.needsUpdate = true
      }
    )
    const loader1 = new THREE.TextureLoader()
    loader1.load(
      this.maskSrc,
      (texture1) => {
        this.mesh.material.alphaMap.image = texture1.image
        this.mesh.material.alphaMap.needsUpdate = true
        func()
      }
    )
  }

  /**
   * 设置Slice的位置
   * @param location Slice的位置
   */
  public setLocation (location: number) {
    switch (this.name) {
      case 'Sagittal':
        this.mesh.position.set(0, 0, centerPoint[0] - location)
        break
      case 'Axial':
        this.mesh.position.set(0, centerPoint[1] - location, 0)
        break
      case 'Coronal':
        this.mesh.position.set(location - centerPoint[2], 0, 0)
        break
    }
  }

  /**
   * 创建Slice的Texture
   */
  public creatSliceTexture () {
    let texture = new THREE.Texture()
    texture.generateMipmaps = false
    texture.wrapS = texture.wrapT = THREE.ClampToEdgeWrapping
    texture.magFilter = THREE.NearestFilter
    texture.minFilter = THREE.NearestFilter
    return texture
  }

  /**
   * 创建Slice的Material
   * @param texture SLice的纹理
   * @param maskTexture Slice的mask纹理，用于控制纹理的透明度
   */
  public creatSliceMaterial (texture: THREE.Texture, maskTexture: THREE.Texture) {
    return new THREE.MeshBasicMaterial({
      map: texture,
      alphaMap: maskTexture,
      alphaTest: 0.5,
      color: 0xffffff,
      side: THREE.DoubleSide,
      opacity: 1.0,
      transparent: false,
      depthTest: true
    })
  }

  /**
   * 创建Slice的Mesh
   * @param name SLice的方向名称
   * @param material Slice的material
   */
  public creatSliceMesh (name: string, material: THREE.Material) {
    const size = SliceSizeMap.get(name)
    if (size) {
      this.geometry = new THREE.PlaneGeometry(size[0], size[1], 32)
      switch (name) {
        case 'Sagittal':
          this.geometry.rotateZ(Math.PI / 2)
          this.geometry.rotateX(Math.PI)
          break
        case 'Axial':
          this.geometry.rotateZ(Math.PI / 2)
          this.geometry.rotateX(Math.PI / 2)
          break
        case 'Coronal':
          this.geometry.rotateY(Math.PI / 2)
          break
      }
    }
    return new THREE.Mesh(this.geometry, material)
  }
}
