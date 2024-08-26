import { RequestOptions } from '@/types/Request'
import { request } from '@/request/RequestWrapper'

const REQUEST_NAME_SPACE = ''

/**
 * 获取所有species
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param requestOptions { RequestOptions } 请求选项
 */
function getALLSpecies (loadingTarget: HTMLElement | null, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}species_all`
  const options: RequestInit = {
    method: 'get'
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'get all species error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    return data
  })
  return r
}

/**
 * 获取species的信息
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param id species id
 * @param requestOptions { RequestOptions } 请求选项
 */
function getSpeciesInfo (loadingTarget: HTMLElement | null, id: number, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}species/${id}`
  const options: RequestInit = {
    method: 'get'
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'get species info error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    return data
  })
  return r
}

/**
 * 获取species image的相关信息
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param imageInfo image info的参数，包括species的id，图片的类型，以及z slice
 * @param requestOptions { RequestOptions } 请求选项
 */
function getSpeciesImage (loadingTarget: HTMLElement | null, imageInfo: any, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}species_image`
  const options: RequestInit = {
    body: JSON.stringify(imageInfo)
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'get species image error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    return data
  })
  return r
}

/**
 * 获取缩略图列表
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param thumbnailInfo 缩略图列表的参数，包括species的id，图片的类型
 * @param requestOptions { RequestOptions } 请求选项
 */
function getThumbnailList (loadingTarget: HTMLElement | null, thumbnailInfo: any, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}thumbnail_list`
  const options: RequestInit = {
    body: JSON.stringify(thumbnailInfo)
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'get thumbnail list error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    return data
  })
  return r
}

/**
 * 获取脑图谱脑区树状结构的数据
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param id 脑图谱id
 * @param requestOptions { RequestOptions } 请求选项
 */
function getStructuralOntology (loadingTarget: HTMLElement | null, id: number, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}structural_ontology/${id}`
  const options: RequestInit = {
    method: 'get'
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'get structural ontology error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    return data
  })
  return r
}

/**
 * 获取脑图谱svg
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param atlasInfo 脑图谱相关参数，包括脑图谱id和z slice
 * @param requestOptions { RequestOptions } 请求选项
 */
function getSpeciesAtlas (loadingTarget: HTMLElement | null, atlasInfo: any, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}species_atlas`
  const options: RequestInit = {
    body: JSON.stringify(atlasInfo)
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'get species atlas error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    return data
  })
  return r
}

/**
 * 获取脑区信息
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param brainRegionInfo 脑区相关参数，包括脑图谱id和脑区id
 * @param requestOptions { RequestOptions } 请求选项
 */
function getBrainRegionInfo (loadingTarget: HTMLElement | null, brainRegionInfo: any, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}atlas_brain_region`
  const options: RequestInit = {
    body: JSON.stringify(brainRegionInfo)
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'get brain region info error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    return data
  })
  return r
}

export { getALLSpecies, getSpeciesInfo, getSpeciesImage, getThumbnailList, getStructuralOntology, getSpeciesAtlas, getBrainRegionInfo }
