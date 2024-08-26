<template>
  <div class="not-found-container">404</div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class NotFound404 extends Vue {

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.not-found-container {
  font-size: 3em;
  text-align: center;
  padding-top: 1em;
}
</style>
