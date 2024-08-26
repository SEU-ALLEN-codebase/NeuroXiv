<template>
  <section class="container">
    <header>
      <h1>{{ headerTitle }}</h1>
      <LangSwitcher class="lang-switcher" />
    </header>
    <main>
      <section class="slot-content">
        <slot></slot>
      </section>
    </main>
    <footer>
      <p>Copyright © 1998 - 2018 Sange The Master. All Rights Reserved.</p>
    </footer>
  </section>
</template>

<script lang="ts">
  import { Component, Vue, Prop } from 'vue-property-decorator'
  // @ts-ignore
  import LangSwitcher from "@/components/common/LangSwitcher.vue"

  @Component({
    components: {
      LangSwitcher
    }
  })
  export default class PageWithHeaderFooter extends Vue {
    @Prop() readonly headerTitle!: string
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
  .container {
    height: 100%;
    display: flex;
    flex-flow: column nowrap;
    header {
      position: absolute;
      width: 100%;
      h1 {
        color: var(--primary-color);
        text-align: left;
        padding-left: 30px;
      }
      .lang-switcher {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        right: 30px;
      }
    }
    main {
      height: 0;
      flex: 1 1 auto;
      display: flex;
      .slot-content {
        margin: auto;
      }
    }
    footer {
      p {
        color: grey;
        font-size: .8em;
        text-align: center;
      }
    }
  }
</style>
