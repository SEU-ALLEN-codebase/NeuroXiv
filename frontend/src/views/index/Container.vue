<template>
  <div class="home">
    <section class="mouse-content">
      <NeuronLogo class="neuron-logo" />
      <p>Beyond Static Brain Atlases: AI Powered Open Databasing and Dynamic Mining of Brain-Wide Neuron Morphometry</p>
      <div class="mouse-features-container">
        <img
          class="dendrite-img"
          src="@/assets/dendrite_260.png"
          alt="dendrite"
        >
        <div class="mouse-features-list">
          <h3 class="list-title">
            Mouse Brain Neuron Atlases
          </h3>
          <ul class="feature-list">
            <li class="feature-item">
              #neurons: 177,186 unique neurons
            </li>
            <li class="feature-item">
              #reconstructions: 349,777
            </li>
            <li class="feature-item">
              #cell-types: 294+
            </li>
            <li class="feature-item">
              #morphological features: 32+
            </li>
            <li class="feature-item">
              Atlas 1: CCFv3 (all)
            </li>
            <li class="feature-item">
              Atlas 2: CCF-thin (for fMOST-like serial thin sections)
            </li>
            <li class="feature-item">
              Atlas 3: CCF-ME (dendrite microenv based atlas)
            </li>
            <li class="feature-item">
              #brain areas with neurite arbors: 316
            </li>
            <li class="feature-item">
              #CCF-ME subregions: 388
            </li>
          </ul>
          <div class="actions">
            <a
              href="/mouse.html"
              class="action-item"
            >
              <el-button
                type="primary"
                size="mini"
                plain
              >
                Enter
              </el-button>
            </a>
            <a
              href="/neuroXiv_user_instruction.pdf"
              class="action-item"
              target="_blank"
            >
              <el-button
                type="primary"
                size="mini"
                plain
              >
                How to use
              </el-button>
            </a>
            <a
              href="/neuroXiv_Mousebrain_Data.pdf"
              class="action-item"
              target="_blank"
            >
              <el-button
                type="primary"
                size="mini"
                plain
              >
                Documentation
              </el-button>
            </a>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import NeuronLogo from '@/components/common/NeuronLogo.vue'

@Component({
  components: { NeuronLogo }
})
export default class Container extends Vue {}
</script>

<style lang="less" scoped>
.home {
  color: var(--primary-color);
  .mouse-content {
    width: fit-content;
    margin: 30px auto 0;
    text-align: center;
    font-weight: 500;
    .neuron-logo {
      font-size: 90px;
    }
    .mouse-features-container {
      text-align: left;
      margin-top: 60px;
      border: 1px solid #02379324;
      padding: 20px;
      border-radius: 5px;
      .dendrite-img, .mouse-features-list {
        display: inline-block;
        vertical-align: middle;
      }
      .dendrite-img {
        width: 300px;
      }
      .mouse-features-list {
        margin-left: 30px;
        .list-title {
          color: var(--primary-color);
        }
        .feature-list {
          list-style: inside;
        }
      }
      .actions {
        margin-top: 20px;
        .action-item {
          margin-right: 20px;
        }
      }
    }
  }
}
</style>
