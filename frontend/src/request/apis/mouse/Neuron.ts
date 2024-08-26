import { RequestOptions } from '@/types/Request'
import { request } from '@/request/RequestWrapper'

const REQUEST_NAME_SPACE = ''

/**
 * 神经元搜索
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param id_list 根据神经元 id 搜索
 * @param criteria 根据搜索条件搜索, 优先根据 id 搜索
 * @param requestOptions { RequestOptions } 请求选项
 */
// eslint-disable-next-line camelcase
function searchNeurons (loadingTarget: HTMLElement | null, { id_list, criteria }: any, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}search`
  console.log(arguments[1])
  const options: RequestInit = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept-Encoding': 'gzip' // 添加gzip支持
    },
    body: JSON.stringify(arguments[1])
  }
  console.log(options.body)
  requestOptions.errorMsg = requestOptions.errorMsg || 'search error'
  const params = { url, loadingTarget, options, ...requestOptions }
  console.log(params)
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    data.plot.hist_plot.forEach((item: any) => {
      item.center = item.center.map((x: number) => parseFloat(x.toFixed(2)))
    })
    return data
  })
  return r
}

/**
 * 根据神经元 id 获取神经元信息
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param id 神经元 id
 * @param atlas
 * @param requestOptions { RequestOptions } 请求选项
 */
function getNeuronInfo (loadingTarget: HTMLElement | null, id: string, atlas: string, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}neurons/${id}`
  const neuronInfo = {
    'neuron_id': id,
    'atlas': atlas
  }
  const options: RequestInit = {
    // method: 'get'
    body: JSON.stringify(neuronInfo)
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'get neuron info error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    // data.img_src 把第二个之后的 slides 数组反序
    // for (let i = 1; i < data.img_src.length; i++) {
    //   data.img_src[i].slides.reverse()
    // }
    return data
  })
  console.log(r)
  return r
}

/**
 * 根据神经元 id 获取神经元信息
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param question 用户提问
 * @param requestOptions { RequestOptions } 请求选项
 */
function AIChat (loadingTarget: HTMLElement | null, question: string, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}AI_Chat/${question}`
  const options: RequestInit = {
    // method: 'post',
    // body: JSON.stringify(question)
    body: question
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'get AI advice error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    return data
  })
  return r
}

function AI_RAG (loadingTarget: HTMLElement | null, question: string, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}AI_RAG/${question}`
  const options: RequestInit = {
    // method: 'post',
    // body: JSON.stringify(question)
    body: question
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'get AI advice error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    return data
  })
  return r
}

function ArticleSearch (loadingTarget: HTMLElement | null, question: string, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}Article/${question}`
  const options: RequestInit = {
    // method: 'post',
    // body: JSON.stringify(question)
    body: question
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'get Articles error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    return data
  })
  return r
}

function CodeGenerator (loadingTarget: HTMLElement | null, question: string, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}GenerateCode/${question}`
  const options: RequestInit = {
    // method: 'post',
    // body: JSON.stringify(question)
    body: question
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'get Code error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    return data
  })
  return r
}

function executeCode (loadingTarget: HTMLElement | null, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}save_code`
  const options: RequestInit = {
    // method: 'post',
    // body: JSON.stringify(question)
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'execute Code error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    return data
  })
  return r
}

/**
 * 根据神经元 id 获取神经元信息
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param question 用户提问
 * @param requestOptions { RequestOptions } 请求选项
 */
function getSearchIntent (loadingTarget: HTMLElement | null, question: string, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}GetIntent/${question}`
  const options: RequestInit = {
    // method: 'post',
    // body: JSON.stringify(question)
    body: question
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'get Intent error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    return data
  })
  return r
}

function getSearchCondition (loadingTarget: HTMLElement | null, question: string, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}GetSearchCondition/${question}`
  const options: RequestInit = {
    body: question
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'get search condition error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    return data
  })
  return r
}

/**
 * 上传神经元并计算神经元的特征
 * 注：不能往headers里设置'Content-Type' 浏览器会根据类型自动设置并添加boundary
 * 否则自己主动添加没法添加boundary 服务器则无法分割
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param fd 上传的文件
 * @param requestOptions { RequestOptions } 请求选项
 */
function uploadNeuron (loadingTarget: HTMLElement | null, fd: FormData, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}upload`
  const options: RequestInit = {
    method: 'POST',
    body: fd,
    headers: {
      'Accept': 'application/json'
    }
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'upload neuron error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    // data.img_src slides 数组反序
    // for (let i = 0; i < data.img_src.length; i++) {
    //   data.img_src[i].slides.reverse()
    // }
    return data
  })
  return r
}

/**
 * 搜索相似神经元，返回搜索条件
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param neuronInfo 神经元的信息
 * @param requestOptions { RequestOptions } 请求选项
 */
function searchSimilarNeuron (loadingTarget: HTMLElement | null, neuronInfo: any, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}search_similar_neurons`
  const options: RequestInit = {
    body: JSON.stringify(neuronInfo)
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'search similar neurons error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    return data
  })
  return r
}

/**
 * 根据ROI搜索神经元
 * @param loadingTarget { HTMLElement | null } 要显示 loading 的元素
 * @param roiParameter ROI的位置与半径，用字符串表示，x_y_z_r
 * @param atlas
 * @param requestOptions { RequestOptions } 请求选项
 */
function searchROINeuron (loadingTarget: HTMLElement | null, roiParameter: string, atlas: string, requestOptions: RequestOptions = {}) {
  const url = `${REQUEST_NAME_SPACE}search_roi/${roiParameter}`
  const roiInfo = {
    'roi_parameter': roiParameter,
    'atlas': atlas
  }
  const options: RequestInit = {
    body: JSON.stringify(roiInfo)
  }
  requestOptions.errorMsg = requestOptions.errorMsg || 'search roi error'
  const params = { url, loadingTarget, options, ...requestOptions }
  let r = request(params)
  let originR = r.start.bind(r)
  r.start = () => originR().then((data: any) => {
    data.plot.hist_plot.forEach((item: any) => {
      item.center = item.center.map((x: number) => parseFloat(x.toFixed(2)))
    })
    return data
  })
  return r
}

export { searchNeurons, getNeuronInfo, uploadNeuron, searchSimilarNeuron, searchROINeuron, AIChat, AI_RAG, getSearchIntent, ArticleSearch, CodeGenerator, executeCode, getSearchCondition }
