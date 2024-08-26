import Vue from 'vue'
import App from './IndexApp.vue'
import '@/registerServiceWorker'
import router from '@/router'
import store from '@/store'
import '@/plugins/element'

import '@/styles/main.less'
import i18n from '@/i18n'
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
