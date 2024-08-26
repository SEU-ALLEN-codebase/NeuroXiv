import Vue from 'vue'
import VueRouter from 'vue-router'
import Container from '../views/mouse/Container.vue'
import store from '@/store/mouse'
import { CreateElement } from 'vue/types/umd'
import { setI18nLanguage } from '@/i18n/mouse'

Vue.use(VueRouter)

let routerBase = 'mouse'
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
        component: Container,
        children: [
          {
            path: '/'
            // redirect: () => `/${getLangParam()}/plans`
          },
          {
            path: 'plans',
            name: 'plans',
            component: () => import(/* webpackChunkName: "plans" */ '../views/mouse/Plans.vue')
          },
          {
            path: 'accountSetting',
            name: 'accountSetting',
            component: () => import(/* webpackChunkName: "accountSetting" */ '../views/mouse/AccountSetting.vue')
          },
          {
            path: 'connectSetting',
            name: 'connectSetting',
            component: () => import(/* webpackChunkName: "connectSetting" */ '../views/mouse/ConnectSetting.vue')
          },
          {
            path: 'subscribeRecord',
            name: 'subscribeRecord',
            component: () => import(/* webpackChunkName: "subscribeRecord" */ '../views/mouse/SubscribeRecord.vue')
          }
        ]
      },
      {
        path: 'login',
        alias: 'login.html',
        name: 'login',
        // route level code-splitting
        // this generates a separate chunk (login.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () => import(/* webpackChunkName: "login" */ '../views/mouse/Login.vue')
      },
      {
        path: 'register',
        alias: 'register.html',
        name: 'register',
        component: () => import(/* webpackChunkName: "register" */ '../views/mouse/Register.vue')
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
