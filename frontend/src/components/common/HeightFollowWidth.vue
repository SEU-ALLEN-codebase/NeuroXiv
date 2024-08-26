<template>
  <div
    ref="container"
    class="s-height-follow-width-container"
  >
    <div class="abs-full">
      <slot />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop, Ref } from 'vue-property-decorator'

@Component
export default class HeightFollowWidth extends Vue {
  @Prop({ default: 1 }) widthHeightRatio!: number // 宽度和高度的比例
  @Ref('container') readonly container!: HTMLDivElement

  mounted () {
    this.container.style.setProperty('--widthHeightRatio', String(this.widthHeightRatio))
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.s-height-follow-width-container {
  position: relative;
  &:before {
    content: '';
    display: block;
    padding-top: calc(1 / var(--widthHeightRatio) * 100%);
  }
  .abs-full {
    position: absolute;
    width: 100%;
    height: 100%;
    left: 0;
    top: 0;
  }
}
</style>
