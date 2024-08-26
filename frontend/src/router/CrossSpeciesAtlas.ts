import Vue from 'vue'
import VueRouter from 'vue-router'
import Container from '@/views/CrossSpeciesAtlas/Container.vue'
import store from '@/store/mouse'
import { CreateElement } from 'vue/types/umd'
import { setI18nLanguage } from '@/i18n/mouse'

Vue.use(VueRouter)

let routerBase = 'CrossSpeciesAtlas'
const hasRouterBase = routerBase && routerBase !== '/'
const getLangParam = () => {
  const pathname = hasRouterBase ? (location.pathname.replace(`/${routerBase}`, '')) : '/'
  return pathname === '/' ? store.state.lang : pathname.match(/\/(\w+)\b/)![1]
}

const routes = [
  {
    path: '/',
    redirect: () => `/${store.state.lang}`
  },
  {
    path: '/:lang',
    component: {
      render: (h: CreateElement) => h('router-view')
    },
    children: [
      {
        path: '',
        alias: 'index.html',
        component: Container
      },
      {
        path: 'mouse',
        alias: 'mouse.html',
        component: () => import('../views/mouse/Container.vue')
      },
      {
        path: '*',
        component: () => import(/* webpackChunkName: "404" */ '../views/common/404.vue')
      }
    ]
  }
]

const router = new VueRouter({
  mode: 'hash',
  base: hasRouterBase ? `/${routerBase}/` : process.env.BASE_URL,
  routes
})

router.beforeEach(async (to, from, next) => {
  // 设置语言
  await setI18nLanguage(to.params.lang)
  next()
})

export default router
