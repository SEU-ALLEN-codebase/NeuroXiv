import { RawLocation } from "vue-router/types/router"

type NavMenuItem = {
  icon?: string // 字体图标类名
  name: string // 导航菜单名称
  route?: RawLocation
  children?: Array<NavMenuItem>
  disabled?: boolean
}

type NavMenu = Array<NavMenuItem>

export { NavMenu }
