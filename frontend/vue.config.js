const APP_CONFIG = require('./config')
const CompressionWebpackPlugin = require('compression-webpack-plugin')

module.exports = {
  lintOnSave: false,
  productionSourceMap: false,

  devServer: {
    clientLogLevel: 'warn',
    proxy: {
      '/api': {
        // target: 'http://localhost:8083',
        target: 'http://127.0.0.1:5000',
        pathRewrite: { '^/api': '' },
        changeOrigin: true
      },
      '/data': {
        // target: 'http://localhost:8083',
        target: 'http://127.0.0.1:5000',
        pathRewrite: { '^/data': '' },
        changeOrigin: true
      },
      '/tmp': {
        // target: 'http://localhost:8083',
        target: 'http://127.0.0.1:5000',
        pathRewrite: { '^/tmp': '' },
        changeOrigin: true
      },
      '/socket.io': {
        target: 'ws://localhost:3000',
        ws: true
      }
    }
  },

  pages: {
    mouse: {
      // entry for the page
      entry: 'src/pages/mouse.ts',
      // the source template
      template: 'public/mouse.html',
      // output as dist/mouse.html
      filename: 'mouse.html',
      // when using title option,
      // template title tag needs to be <title><%= htmlWebpackPlugin.options.title %></title>
      title: 'neuroXiv',
      // chunks to include on this page, by default includes
      // extracted common chunks and vendor chunks.
      chunks: ['chunk-vendors', 'chunk-common', 'mouse']
    },
    index: {
      // entry for the page
      entry: 'src/pages/index.ts',
      // the source template
      template: 'public/index.html',
      // output as dist/index.html
      filename: 'index.html',
      // when using title option,
      // template title tag needs to be <title><%= htmlWebpackPlugin.options.title %></title>
      title: 'neuroXiv',
      // chunks to include on this page, by default includes
      // extracted common chunks and vendor chunks.
      chunks: ['chunk-vendors', 'chunk-common', 'index']
    },
    // when using the entry-only string format,
    // template is inferred to be `public/subpage.html`
    // and falls back to `public/index.html` if not found.
    // Output filename is inferred to be `subpage.html`.
    proxy: { // QQ 登录成功回调页面
      // entry for the page
      entry: 'src/pages/proxy.ts',
      // the source template
      template: 'public/proxy.html',
      // output as dist/index.html
      filename: 'proxy.html',
      appId: APP_CONFIG.QQ_LOGIN_APP_ID
    },
    CrossSpeciesAtlas: {
      // entry for the page
      entry: 'src/pages/CrossSpeciesAtlas.ts',
      // the source template
      template: 'public/CrossSpeciesAtlas.html',
      // output as dist/index.html
      filename: 'CrossSpeciesAtlas.html',
      // when using title option,
      // template title tag needs to be <title><%= htmlWebpackPlugin.options.title %></title>
      title: 'neuroXiv',
      // chunks to include on this page, by default includes
      // extracted common chunks and vendor chunks.
      chunks: ['chunk-vendors', 'chunk-common', 'CrossSpeciesAtlas']
    }
  },

  pluginOptions: {
    i18n: {
      locale: 'en',
      fallbackLocale: 'en',
      localeDir: 'locales',
      enableInSFC: false
    }
  },

  chainWebpack: config => {
    config.module
      .rule('i18n')
      .resourceQuery(/blockType=i18n/)
      .type('javascript/auto')
      .use('i18n')
      .loader('@kazupon/vue-i18n-loader')
      .end()
  },
  configureWebpack: {
    plugins: [
      require('./prerender.config'),
      new CompressionWebpackPlugin({
        filename: '[path].gz[query]',
        algorithm: 'gzip',
        test: /\.(js|css|html|svg)$/,
        threshold: 10240,
        minRatio: 0.8
      })
    ]
  }
  // configureWebpack: {
  //   plugins: process.env.NODE_ENV === 'production' ? [
  //     require('./prerender.config'),
  //     new CompressionWebpackPlugin({
  //       filename: '[path].gz[query]',
  //       algorithm: 'gzip',
  //       test: /\.(js|css|html|svg)$/,
  //       threshold: 10240,
  //       minRatio: 0.8
  //     })
  //   ] : []
  // }
}
