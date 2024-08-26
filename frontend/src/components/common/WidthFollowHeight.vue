<template>
  <div
    class="s-width-follow-height-container"
  >
    <canvas
      :width="widthHeightRatio"
      height="1"
    />
    <div class="abs-full">
      <slot />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator'

@Component
export default class WidthFollowHeight extends Vue {
  @Prop({ default: 1 }) widthHeightRatio!: number // 宽度和高度的比例
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.s-width-follow-height-container {
  position: relative;
  width: fit-content;
  canvas {
    display: block;
    height: 100%;
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
