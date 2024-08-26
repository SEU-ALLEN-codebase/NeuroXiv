<template>
  <a
    href="/"
    class="logo"
  >
    <span>neuro</span>
    <span class="logo-img-container">
      <img
        src="@/assets/neuroxiv_logo_white.png"
        alt="neuro logo"
      >
    </span>
    <span>iv</span>
  </a>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class NeuronLogo extends Vue {}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.logo {
  text-decoration: none;
  color: #023793;
  font-size: 50px;
  font-weight: 500;
  > * {
    vertical-align: middle;
  }
  .logo-img-container {
    display: inline-block;
    background-color: currentColor;
    mask: url("~@/assets/neuroxiv_logo_white.png") center / contain no-repeat;
    img {
      display: block;
      visibility: hidden;
      width: .8em;
    }
  }
}
</style>
