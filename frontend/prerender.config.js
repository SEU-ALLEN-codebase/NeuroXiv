// 这里预渲染生成的文件, 例如 `http://localhost/en/index.html`, 访问的时候需要输入完整路径才有预渲染效果
// 访问 `http://localhost/en/` 由于 history fallback 的设置, 实际访问的文件是 `http://localhost/index.html`, 虽然显示的内容一样, 但是这个并没有 SEO 的效果
// 代码里面跳转的路由没有添加 `index.html` 后缀, 所以会跳转到没有 pre render 的页面
// 虽然有这些问题, 但是应该没什么影响, 只要搜索引擎可以搜索到带有 `index.html` 后缀的文件就可以了, 而且这个文件的路由跳转也是没有问题的

const path = require('path')
const PrerenderSPAPlugin = require('prerender-spa-plugin')
// const Renderer = PrerenderSPAPlugin.PuppeteerRenderer

const plugin = new PrerenderSPAPlugin({
  // Required - The path to the webpack-outputted app to pre render.
  staticDir: path.join(__dirname, 'dist'),
  // Required - Routes to render.
  // todo: 这里要动态生成
  routes: [ '/', '/mouse', '/CrossSpeciesAtlas' ],
  postProcess (renderedRoute) {
    // Remove /index.html from the output path if the dir name ends with a .html file extension.
    // For example: /dist/dir/special.html/index.html -> /dist/dir/special.html
    if (renderedRoute.route.endsWith('.html')) {
      renderedRoute.outputPath = path.join(__dirname, 'dist', renderedRoute.route)
    }
    return renderedRoute
  }
  // 下面的设置添加了之后会报错...
  // renderer: new Renderer({
  //   // Optional - defaults to 0, no limit.
  //   // Routes are rendered asynchronously.
  //   // Use this to limit the number of routes rendered in parallel.
  //   // maxConcurrentRoutes: 4,
  //
  //   // Optional - Wait to render until the specified event is dispatched on the document.
  //   // eg, with `document.dispatchEvent(new Event('custom-render-trigger'))`
  //   // renderAfterDocumentEvent: 'custom-render-trigger',
  //
  //   // Optional - Wait to render until the specified element is detected using `document.querySelector`
  //   // renderAfterElementExists: 'my-app-element',
  //
  //   // Optional - Wait to render until a certain amount of time has passed.
  //   // NOT RECOMMENDED
  //   // renderAfterTime: 5000, // Wait 5 seconds.
  //
  //   // Other puppeteer options.
  //   // (See here: https://github.com/GoogleChrome/puppeteer/blob/master/docs/api.md#puppeteerlaunchoptions)
  //   headless: false // Display the browser window when rendering. Useful for debugging.
  // })
})

module.exports = plugin
