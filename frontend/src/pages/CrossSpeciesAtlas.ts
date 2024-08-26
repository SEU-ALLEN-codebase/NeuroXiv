import Vue from 'vue'
import App from './CrossSpeciesAtlasApp.vue'
import '@/registerServiceWorker'
import router from '@/router/CrossSpeciesAtlas'
import store from '@/store/mouse'
import '@/plugins/element'

import '@/styles/main.less'
import i18n from '@/i18n/mouse'
import '@/polyfill'
import '@/pageInitSetup'

Vue.config.productionTip = false

declare global {
  interface Window {
    vm: Vue
  }
}

window.vm = new Vue({
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount('#app')
