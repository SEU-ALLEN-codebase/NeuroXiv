<template>
  <div class="nav-aside" :class="{ collapse: isCollapse }">
    <div class="logo">
      <div class="complete-logo">
        <img src="@/assets/logo.png" alt="logo" class="logo-img scale-rotate-animation" />
        <span class="logo-word">SANGEEEEE</span>
      </div>
      <div class="collapse-logo abs-full vertical-middle">
        <img class="logo-img centered scale-rotate-animation" src="@/assets/logo.png" alt="logo" />
      </div>
    </div>
    <el-menu :collapse="isCollapse" :default-active="$route.name" class="nav-menu">
      <template v-for="(menu, i) in menus">
        <el-submenu :index="menu.name" v-if="menu.children && menu.children.length > 0" :key="i" :popper-append-to-body="false">
          <template slot="title">
            <i :class="menu.icon"></i>
            <span class="menu-name text-ellipsis" :title="$t(`nav.${menu.name}`)">{{ $t(`nav.${menu.name}`) }}</span>
          </template>
          <el-menu-item
            v-for="(submenu, j) in menu.children"
            :key="`${i}-${j}`"
            :class="{ disabled: submenu.disabled }"
            :index="submenu.name">
            <router-link class="nav-link abs-full" :to="getCompleteRouteByPathString(submenu.route)">
              <span class="menu-name text-ellipsis" :title="$t(`nav.${submenu.name}`)">{{ $t(`nav.${submenu.name}`) }}</span>
            </router-link>
          </el-menu-item>
        </el-submenu>
        <el-menu-item
          :index="menu.name"
          v-else
          :class="{ disabled: menu.disabled }"
          :key="i">
          <router-link class="nav-link abs-full" :to="getCompleteRouteByPathString(menu.route)">
            <i :class="menu.icon"></i>
            <span class="menu-name text-ellipsis" :title="$t(`nav.${menu.name}`)">{{ $t(`nav.${menu.name}`) }}</span>
          </router-link>
        </el-menu-item>
      </template>
    </el-menu>
    <div class="menu-collapse">
      <i class="el-icon-arrow-left collapse-trigger" @click="isCollapse = !isCollapse"></i>
    </div>
  </div>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import { NavMenu } from '@/types/NavBar'
import RouterHelper from '@/mixins/RouterHelper.vue'

const menus: NavMenu = [
  { icon: 'icomoon-icon-chrome', name: 'plans', route: 'plans' },
  { icon: 'el-icon-menu', name: 'userInfo', children: [
    { icon: 'el-icon-location', name: 'accountSetting', route: 'accountSetting', disabled: true },
    { icon: 'el-icon-location', name: 'connectSetting', route: 'connectSetting' },
    { icon: 'el-icon-location', name: 'subscribeRecord', route: 'subscribeRecord' }
  ] }
]

@Component
export default class NavBar extends RouterHelper {
  public isCollapse: boolean = false
  private menus: NavMenu = menus
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.nav-aside {
  --nav-width: 230px;
  --transition-duration: 1.3s;
  background-color: var(--panel-background-color);
  display: flex;
  flex-flow: column nowrap;
  width: max-content;
  .logo {
    font-weight: bold;
    color: var(--primary-color);
    text-decoration: none;
    position: relative;
    .complete-logo, .collapse-logo {
      transition-property: width, opacity, visibility;
      transition-duration: var(--transition-duration);
    }
    .complete-logo {
      text-align: center;
      font-size: 1.6em;
      padding: 13px;
      white-space: nowrap;
      overflow: hidden;
      width: var(--nav-width);
      .logo-img, .logo-word {
        vertical-align: middle;
      }
      .logo-img {
        width: 30px;
        margin-right: 10px;
        animation-delay: 1.5s;
      }
    }
    .collapse-logo {
      opacity: 0;
      visibility: hidden;
      text-align: center;
      .logo-img {
        width: 30px;
      }
    }
  }
  .nav-menu {
    background-color: inherit;
    flex: 1 1 auto;
    border-top: 1px solid var(--separator-line-color);
    border-bottom: 1px solid var(--separator-line-color);
    font-weight: bold;
    [class^="icomoon-icon-"] {
      vertical-align: middle;
      margin-right: 10px;
      width: 24px;
      text-align: center;
      font-size: 18px;
      color: var(--primary-color);
      font-weight: bold;
    }
    .menu-name {
      max-width: 150px;
    }
    .el-menu-item {
      position: relative;
      .nav-link {
        text-decoration: none;
        padding: inherit;
        color: inherit;
      }
      &.is-active {
        background-color: var(--primary-color);
        background-image: var(--rect-gradient);
        color: white;
        i {
          color: inherit;
        }
      }
    }
    &:not(.el-menu--collapse) {
      width: var(--nav-width);
      padding: 5px;
    }
  }
  .menu-collapse {
    text-align: right;
    padding: 10px;
    .collapse-trigger {
      font-weight: bold;
      cursor: pointer;
      transition: transform var(--transition-duration);
    }
  }
  &.collapse {
    .logo {
      .complete-logo {
        width: 0;
        opacity: 0;
        visibility: hidden;
      }
      .collapse-logo {
        opacity: 1;
        visibility: visible;
        transition-delay: 1s;
      }
    }
    .menu-collapse {
      .collapse-trigger {
        transform: scaleX(-1);
      }
    }
  }
}
</style>
