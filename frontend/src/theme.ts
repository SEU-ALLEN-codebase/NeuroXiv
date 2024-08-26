import { Theme } from '@/types/Theme'

const loadedThemes: Array<Theme> = []

export async function setTheme (theme: Theme) {
  if (!loadedThemes.includes(theme)) {
    await import(/* webpackChunkName: "theme-[request]" */ `@/themes/${theme}.less`)
  }
  document.documentElement.classList.remove('light', 'dark')
  document.documentElement.classList.add(theme)
  loadedThemes.push(theme)
  return theme
}
