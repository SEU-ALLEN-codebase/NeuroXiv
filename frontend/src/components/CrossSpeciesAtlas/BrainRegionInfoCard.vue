<template>
  <el-popover
    v-model="brainRegionInfoVisible"
    class="brain-region-info"
    :style="brainRegionInfoStyle"
    placement="top-start"
    trigger="manual"
  >
    <p v-if="brainRegionInfo">
      species: {{ brainRegionInfo.species }}
    </p>
    <p v-if="brainRegionInfo">
      atlas: {{ brainRegionInfo.atlas }}
    </p>
    <p v-if="brainRegionInfo">
      brain region: {{ brainRegionInfo.name }}({{ brainRegionInfo.acronym }})
    </p>
    <div
      v-if="brainRegionInfo"
      class="brain-region-info-neuron"
    >
      <p class="neuron-label">
        neuron collections:
      </p>
      <el-button
        type="text"
        class="neuron-button"
        :disabled="brainRegionInfo.neurons_num === 0"
        @click.native="jumpNeuronWeb"
      >
        {{ brainRegionInfo.neurons_num }}
      </el-button>
    </div>
    <p
      v-if="brainRegionInfo"
      class="p-main-text"
    >
      adjacent brain regions:
    </p>
    <ul v-if="brainRegionInfo">
      <li
        v-for="(item, i) in brainRegionInfo.adjacent_brain_regions"
        :key="i"
      >
        <el-button
          type="text"
          @click.native="SelectAdjacentBrainRegion(item)"
          @mouseenter.native="GetAdjacentBrainRegionInfo(item)"
          @mouseleave.native="leaveBrainRegion"
        >
          {{ item.name }}({{ item.acronym }})
        </el-button>
      </li>
    </ul>
    <p
      v-if="brainRegionInfo"
      class="p-main-text"
    >
      related brain regions:
    </p>
    <ul v-if="brainRegionInfo">
      <li
        v-for="(item, i) in brainRegionInfo.related_brain_regions"
        :key="i"
      >
        <p class="p-second-main-text">{{ item.atlas }}:</p>
        <ul>
          <li
            v-for="(bItem, b) in item.brain_regions"
            :key="b"
          >
            <el-button
              type="text"
              @click="SelectRelatedBrainRegion(item, bItem)"
              @mouseenter.native="GetRelatedBrainRegionInfo(item, bItem)"
              @mouseleave.native="leaveBrainRegion"
            >
              {{ bItem.name }}({{ bItem.acronym }})
            </el-button>
          </li>
        </ul>
      </li>
    </ul>
  </el-popover>
</template>

<script lang="ts">
import { Component, Ref, Vue, Prop } from 'vue-property-decorator'
import RouterHelper from '@/mixins/RouterHelper.vue'
@Component<BrainRegionInfoCard>({
  mounted () {}
})

export default class BrainRegionInfoCard extends RouterHelper {
  @Prop({ required: true }) brainRegionInfoVisible!: boolean
  @Prop({ required: true }) brainRegionInfoStyle!: any
  @Prop({ required: true }) brainRegionInfo!: any
  @Prop({ required: true }) SelectAdjacentBrainRegion!: any
  @Prop({ required: true }) GetAdjacentBrainRegionInfo!: any
  @Prop({ required: true }) SelectRelatedBrainRegion!: any
  @Prop({ required: true }) GetRelatedBrainRegionInfo!: any
  @Prop({ required: true }) leaveBrainRegion!: any

  public jumpNeuronWeb () {
    let acronym = this.brainRegionInfo.acronym
    if ((acronym.indexOf('1') !== -1 ||
      acronym.indexOf('2/3') !== -1 ||
      acronym.indexOf('4') !== -1 ||
      acronym.indexOf('5') !== -1 ||
      acronym.indexOf('6') !== -1 ||
      acronym.indexOf('6a') !== -1 ||
      acronym.indexOf('6b') !== -1) &&
      (acronym !== 'CUL4, 5' &&
        acronym !== 'P5' &&
        acronym !== 'PC5' &&
        acronym !== 'CA1' &&
        acronym !== 'CA2' &&
        acronym !== 'CA3')
    ) {
      if (acronym.indexOf('1') !== -1) {
        acronym = acronym.replace('1', ' Layer1')
      } else if (acronym.indexOf('2/3') !== -1) {
        acronym = acronym.replace('2/3', ' Layer2/3')
      } else if (acronym.indexOf('4') !== -1) {
        acronym = acronym.replace('4', ' Layer4')
      } else if (acronym.indexOf('5') !== -1) {
        acronym = acronym.replace('5', ' Layer5')
      } else if (acronym.indexOf('6a') !== -1) {
        acronym = acronym.replace('6a', ' Layer6a')
      } else if (acronym.indexOf('6b') !== -1) {
        acronym = acronym.replace('6b', ' Layer6b')
      } else if (acronym.indexOf('6') !== -1) {
        acronym = acronym.replace('6', ' Layer6')
      }
    }
    window.location.href = `/mouse.html#/${this.$route.params.lang}/?atlasName=${this.brainRegionInfo.atlas}&brainRegion=${acronym}`
  }
}
</script>

<style scoped lang="less">
.brain-region-info {
  width: 500px;
  //height: 500px;
  //overflow: auto;
  position: absolute;
  top: var(--top);
  left: var(--left);
  .brain-region-info-neuron {
    display: flex;
    .neuron-label {
      margin: 0;
    }
    .neuron-button {
      padding: 0;
    }
  }
  .p-main-text {
    margin-bottom: 0;
  }
  .p-second-main-text {
    margin-top: 13px;
    margin-bottom: 0;
  }
}
</style>
