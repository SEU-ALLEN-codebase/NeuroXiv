<template>
  <div class="about-container">
    <h1 class="title">
      About
    </h1>
    <div class="content">
      <p>
        To understand brain connectivity and functions, it is important to study neuronal classifications and projections in single cell resolution and also at the brain-wide scale. This website provides a coordinated platform for neuron morphology, projection, and connectivity analysis. Our approach is to perform a joint and comparative analysis at the whole brain scale by aggregating datasets from multiple research centers that have adopted different, complementary experimental protocols to generate large-scale datasets of single neurons.
      </p>
    </div>
    <h1 class="title">
      Consortium
    </h1>
    <div class="content">
      <ul>
        <li>Institute for Brain and Intelligence</li>
        <li>Tencent AI Lab</li>
        <li>Other collaboration organizations are being updated</li>
      </ul>
    </div>
    <h1 class="title">
      Publications
    </h1>
    <div class="content">
      <ul>
        <li>Paper in submission</li>
      </ul>
    </div>
    <h1 class="title">
      Contact
    </h1>
    <div class="content">
      <p>
        <span>For questions, feedback, and collaboration requests, please contact us: </span>
      </p>
      <ul class="contact-email-list">
        <li class="email-item">
          <a href="mailto:shengdianjiang@seu.edu.cn">shengdianjiang@seu.edu.cn</a> or <a href="mailto:lijunwang@seu.edu.cn">lijunwang@seu.edu.cn</a>
        </li>
        <li class="email-item">
          <a href="mailto:h@braintell.org">h@braintell.org</a> or <a href="mailto:ljliu@braintell.org">ljliu@braintell.org</a>
        </li>
      </ul>
    </div>
    <h1
      v-show="false"
      class="title"
    >
      Terms of Use
    </h1>
    <div
      v-show="false"
      class="content"
    >
      <p>TBD</p>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class About extends Vue {}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.about-container {
  padding: 20px 50px;
  font-weight: 500;
  .title {
    color: var(--primary-color);
  }
  ul {
    list-style: inside;
  }
}
</style>
