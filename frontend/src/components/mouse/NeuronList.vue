<template>
  <div class="neuron-list-container">
    <div class="batch-actions">
      <div class="batch-select">
        <el-checkbox
          v-model="checkAll"
          label="select this page"
          :indeterminate="isIndeterminate"
          @change="batchSelectHandler"
        />
        <el-checkbox
          v-model="checkAllPages"
          label="select all pages"
          :indeterminate="isIndeterminate"
          @change="batchSelectHandlerAll"
        />
      </div>
      <el-button
        type="primary"
        size="small"
        class="analysis-button"
        @click="neuronAnalysisHandler"
      >
        Analysis
      </el-button>
      <el-button
        type="primary"
        size="small"
        class="analysis-button"
        @click="viewNeuronsHandler"
      >
        View
      </el-button>
    </div>
    <ul class="neuron-items">
      <li
        v-for="(item, i) in currentPageData"
        :key="i"
        class="neuron-item"
      >
        <el-checkbox
          v-model="item.selected"
          @change="checkNeuronCallback(item)"
        />
        <img
          :src="item.img_src"
          :title="item.id"
          alt="neuron thumb"
          class="neuron-thumb"
        >
        <div class="neuron-tags">
          <!--          <el-tag-->
          <!--            class="neuron-tag-item-cell-type"-->
          <!--            :color="getTagColor(item.celltype)"-->
          <!--            effect="dark"-->
          <!--            size="mini"-->
          <!--            @click="jumpAtlasWeb(item)"-->
          <!--          >-->
          <!--            {{ item.celltype }}-->
          <!--          </el-tag>-->
          <el-tag
            class="neuron-tag-item-cell-type"
            :color="getTagColor(item.celltype)"
            effect="dark"
            size="mini"
          >
            {{ item.celltype }}
          </el-tag>
          <el-tag
            class="neuron-tag-item"
            :color="getTagColor('hemisphere')"
            effect="dark"
            size="mini"
          >
            {{ item.hemisphere }}
          </el-tag>
          <el-tag
            v-for="(prop, j) in ['axon', 'dendrite', 'apical']"
            :key="j"
            class="neuron-tag-item-morpho"
            :class="{ disabled: !item[`has_${prop}`] }"
            :color="getTagColor(item, prop)"
            effect="dark"
            size="mini"
            @click="!item[`has_${prop}`] || openColorPicker(prop, item, $event)"
          >
            <template v-if="prop === 'dendrite'">
              basal
            </template>
            <template v-else>
              {{ prop }}
            </template>
          </el-tag>
          <el-tag
            class="neuron-tag-item"
            :color="getTagColor(item.id.split('_')[0].split('-')[0])"
            effect="dark"
            size="mini"
          >
            <template v-if="item.id.split('_')[0].split('-')[0] === 'MouseLight'">
              Janelia
            </template>
            <template v-else-if="item.id.split('_')[0].split('-')[0] === 'SEU'">
              seuallen
            </template>
            <template v-else>
              ION
            </template>
          </el-tag>
        </div>
        <el-button
          type="primary"
          size="small"
          @click="neuronViewHandler(item)"
        >
          Info
        </el-button>
      </li>
    </ul>
    <el-pagination
      class="pager"
      background
      small
      layout="prev, pager, next"
      :total="data.length"
      :page-size="pageSize"
      :current-page.sync="currentPage"
      :pager-count="7"
      @current-change="gotoPage"
    />
    <el-row
      class="pager"
      type="flex"
      justify="center"
    >
      <el-col :span="8">
        <el-input
          v-model="targetPage"
          placeholder="跳转到页码"
        />
      </el-col>
      <el-col :span="8">
        <el-button
          type="primary"
          @click="goToTargetPage"
        >
          go to page
        </el-button>
      </el-col>
    </el-row>
    <sketch-picker
      v-if="showColorPicker"
      ref="colorPicker"
      :value="selectedColor"
      :style="{ position: 'fixed', top: colorPickerPosition.top, left: colorPickerPosition.left, zIndex: 9999 }"
      @input="handleColorChange"
      @change="updateColor"
      @dblclick="applyColorAndClose"
    />
  </div>
</template>

<script lang="ts">
import { Component, Ref, Vue, Watch } from 'vue-property-decorator'
import { Sketch } from 'vue-color'
import NeuronScene from '@/components/mouse/NeuronScene.vue'

@Component({
  components: {
    'sketch-picker': Sketch,
    NeuronScene
  }
})
export default class NeuronList extends Vue {
    @Ref('neuronScene') neuronScene!: NeuronScene
    // 搜索结果的所有数据
    private data: any[] = []
    // 当前分页的数据
    private currentPageData: any[] = []
    private pageSize: number = 10
    private currentPage: number = 1
    private targetPage : number = 1
    private checkAll: boolean = false
    private checkAllPages: boolean = false
    private isIndeterminate: boolean = false

    private showColorPicker: boolean = false;
    private selectedColor: any = { hex: '#000000', rgba: { r: 0, g: 0, b: 0, a: 1 } };
    private selectedProp: string = '';
    private selectedItem: any = null;
    private colorPickerPosition = { top: '0px', left: '0px' };

    mounted () {
      document.addEventListener('click', this.handleClickOutside)
    }

    beforeDestroy () {
      document.removeEventListener('click', this.handleClickOutside)
    }

    private openColorPicker (prop: string, item: any, event: MouseEvent) {
      console.log('openColorPicker triggered', { prop, item, event })
      this.selectedProp = prop
      this.selectedItem = item

      // 设置颜色选择器位置
      this.colorPickerPosition = {
        top: `${event.clientY}px`,
        left: `${event.clientX}px`
      }

      // 初始化颜色
      this.selectedColor = item.customTagColors?.[prop] || { hex: '#000000', rgba: { r: 0, g: 0, b: 0, a: 1 } }

      // 延迟显示颜色选择器以避免立即关闭
      setTimeout(() => {
        this.showColorPicker = true
      }, 0)
    }

    private handleColorChange (color: any) {
      this.selectedColor = color
    }

    private updateColor () {
      if (this.selectedItem && this.selectedProp) {
        this.selectedItem.customTagColors[this.selectedProp] = `rgb(${this.selectedColor.rgba.r}, ${this.selectedColor.rgba.g}, ${this.selectedColor.rgba.b})`
      }
    }

    private applyColorAndClose () {
      this.updateColor() // 应用颜色
      this.closeColorPicker() // 关闭颜色选择器
      console.log('Color picker closed on double-click')
    }

    private closeColorPicker () {
      this.showColorPicker = false
      console.log('Color picker manually closed')
    }

    private handleClickOutside (event: MouseEvent) {
      const colorPickerInstance = this.$refs.colorPicker as Vue | undefined

      if (colorPickerInstance && colorPickerInstance.$el) {
        const colorPickerElement = colorPickerInstance.$el as HTMLElement

        // 检查点击是否在颜色选择器外部
        if (!colorPickerElement.contains(event.target as Node)) {
          console.log('Click detected outside of color picker')
          this.applyColorAndClose()
        }
      } else {
        console.log('Color picker instance not found or not yet rendered')
      }
    }
    /**
     * 获取列表第一个数据
     */
    public getFirstItem () {
      return this.data.length ? this.data[0] : null
    }

    /**
     * 获取列表中勾选的数据
     */
    public getSelectedItems () {
      return this.data.filter((item: any) => item.selected)
    }

    /**
     * 设置列表的数据
     * @param listData 列表数据
     */
    public setListData (listData: any[]) {
      listData.forEach((item: any) => {
        item.selected = false

        // 初始化 axon, dendrite, apical 的颜色
        item.customTagColors = {
          axon: 'rgb(255, 0, 0)', // 初始颜色
          dendrite: 'rgb(0, 80, 255)',
          apical: 'rgb(255, 0, 255)'
        }
      })

      this.data = listData
      this.gotoPage(1)
      this.checkAll = false
    }

    /**
     * 批量选择
     * @param val 选择或者取消选择
     */
    private batchSelectHandler (val: boolean) {
      this.currentPageData.forEach((item: any) => {
        item.selected = val
        this.$emit('checkNeuron', item)
      })
      this.isIndeterminate = false
    }

    private batchSelectHandlerAll (val: boolean) {
      this.data.forEach((item: any) => {
        item.selected = val
        this.$emit('checkNeuron', item)
      })
      this.isIndeterminate = false
    }

    /**
     * 批量选择神经元之后点击统计分析按钮
     */
    private neuronAnalysisHandler () {
      const selectedNeuronIds = this.data.filter((item: any) => item.selected).map((item: any) => item.id)
      if (selectedNeuronIds.length === 0) {
        this.$message.warning('No neuron selected')
        return
      }
      this.$emit('neuronAnalysis', selectedNeuronIds)
    }

    /**
     * 批量选择神经元之后3D可视化
     */
    private viewNeuronsHandler () {
      this.$emit('viewNeurons')
    }

    /**
     * 点击查看按钮
     * @param neuronDetail 神经元信息
     */
    private neuronViewHandler (neuronDetail: any) {
      this.$emit('neuronView', neuronDetail)
    }

    /**
     * 选中或取消右方神经元列表中的神经元的神经元的回调函数
     * @param neuronDetail 神经元信息
     */
    private checkNeuronCallback (neuronDetail: any) {
      this.$emit('checkNeuron', neuronDetail)
    }

    private parseColor (color: string) {
      // If the color is a string in "rgb(r, g, b)" format
      const rgbRegex = /^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/
      const result = rgbRegex.exec(color)
      if (result) {
        return {
          r: parseInt(result[1], 10),
          g: parseInt(result[2], 10),
          b: parseInt(result[3], 10)
        }
      }
    }
    /**
     * 获取 neuron 属性标签对应的颜色
     * @param item
     * @param prop 属性名称
     * @private
     */
    // eslint-disable-next-line camelcase
    private getTagColor (item: any, prop?: string) {
      if (prop) {
        const colorObj = item.customTagColors?.[prop]
        const rgbvalues = this.parseColor(colorObj)
        if (rgbvalues) {
          // if (item.hasOwnProperty('customTagColors')) { this.neuronScene.updateObjColor(item.id, [rgbvalues.r, rgbvalues.g, rgbvalues.b]) }
          return `rgb(${rgbvalues.r}, ${rgbvalues.g}, ${rgbvalues.b})`
        }
        return 'rgb(0, 0, 0)' // Or customize the default handling as needed
      }
      // 处理其他标签颜色逻辑
      const colorMap: { [key: string]: string } = {
        axon: 'rgb(255, 0, 0)',
        bouton: 'rgb(253, 242, 208)',
        dendrite: 'rgb(0, 80, 255)',
        apical: 'rgb(255, 0, 255)',
        arbor: 'rgb(255, 121, 108)',
        CCFv3: 'rgb(214, 253, 254)',
        fMOST: 'rgb(159, 205, 99)',
        ION: 'rgb(6,194,172)',
        SEU: 'rgb(6,194,172)',
        MouseLight: 'rgb(6,194,172)',
        hemisphere: 'rgb(255, 121, 108)'
      }
      return colorMap[item] || 'white'
    }

    // private getTagColor (prop: string) {
    //   const colorMap: { [key: string]: string } = {
    //     axon: 'rgb(255, 0, 0)',
    //     bouton: 'rgb(253, 242, 208)',
    //     dendrite: 'rgb(0, 80, 255)',
    //     apical: 'rgb(255, 0, 255)',
    //     arbor: 'rgb(255, 121, 108)',
    //     CCFv3: 'rgb(214, 253, 254)',
    //     fMOST: 'rgb(159, 205, 99)',
    //     ION: 'rgb(6,194,172)',
    //     SEU: 'rgb(6,194,172)',
    //     MouseLight: 'rgb(6,194,172)',
    //     hemisphere: 'rgb(255, 121, 108)'
    //   }
    //   // console.log(colorMap[prop] || 'white')
    //   return colorMap[prop] || 'white'
    // }

    /**
     * 切换分页
     * @param whichPage 要切换的页数
     * @private
     */
    private gotoPage (whichPage: number) {
      let currentPage = whichPage || this.currentPage
      let start = this.pageSize * (currentPage - 1)
      let end = start + this.pageSize
      this.currentPageData = this.data.slice(start, end)
      this.currentPage = currentPage
    }
    private goToTargetPage () {
      let currentPage = this.targetPage
      let start = this.pageSize * (currentPage - 1)
      let end = start + this.pageSize
      this.currentPageData = this.data.slice(start, end)
      this.currentPage = currentPage
    }

    private jumpAtlasWeb (item: any) {
      window.location.href = `/CrossSpeciesAtlas.html#/${this.$route.params.lang}/?atlasName=${this.$store.state.atlas}&brainRegion=${item.celltype}`
    }

    @Watch('currentPageSelectedItem.length')
    currentPageSelectedChanged (newVal: number) {
      this.checkAll = newVal === this.currentPageData.length
      this.isIndeterminate = newVal > 0 && newVal < this.currentPageData.length
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.neuron-list-container {
  width: 380px;
  height: 100%;
  padding: 20px;
  display: flex;
  //flex-flow: column nowrap;
  flex-flow: column nowrap;
  border-left: 1px solid gray;
  .batch-actions {
    display: flex;
    //flex-flow: column nowrap;
    flex-flow: row nowrap;
    border-bottom: 1px solid gray;
    padding: 0 0 20px 0;
    .analysis-button {
      margin-left: 20px;
    }
  }
  .batch-select {
    display: flex;
    flex-direction: column;
  }
  .neuron-items {
    height: 0;
    overflow: auto;
    flex: 1 1 auto;
    .neuron-item {
      border-bottom: 1px solid gray;
      padding: 15px 0;
      white-space: nowrap;
      > * {
        display: inline-block;
        vertical-align: middle;
        margin-right: 10px;
      }
      .neuron-thumb {
        width: 70px;
        border: 1px solid gray;
      }
      .neuron-tags {
        width: 160px;
        text-align: center;
        white-space: initial;
        .neuron-tag-item {
          display: inline-block;
          margin: 3px;
          width: 60px;
          text-align: center;
          color: black;
        }
        .neuron-tag-item-morpho {
          display: inline-block;
          margin: 3px;
          width: 60px;
          text-align: center;
          color: black;
          cursor: pointer;
        }
        .neuron-tag-item-cell-type {
          display: inline-block;
          margin: 3px;
          width: 60px;
          text-align: center;
          color: black;
        }
        .neuron-tag-item-cell-type:hover {
          cursor: pointer;
        }
      }
    }
  }
  .pager {
    margin-top: 20px;
  }
}
</style>

<!--<template>-->
<!--  <div class="neuron-list-container">-->
<!--    <div class="batch-actions">-->
<!--      <div class="batch-select">-->
<!--        <el-checkbox-->
<!--          v-model="checkAll"-->
<!--          label="select this page"-->
<!--          :indeterminate="isIndeterminate"-->
<!--          @change="batchSelectHandler"-->
<!--        />-->
<!--        <el-checkbox-->
<!--          v-model="checkAllPages"-->
<!--          label="select all pages"-->
<!--          :indeterminate="isIndeterminate"-->
<!--          @change="batchSelectHandlerAll"-->
<!--        />-->
<!--      </div>-->
<!--      <el-button-->
<!--        type="primary"-->
<!--        size="small"-->
<!--        class="analysis-button"-->
<!--        @click="neuronAnalysisHandler"-->
<!--      >-->
<!--        Analysis-->
<!--      </el-button>-->
<!--      <el-button-->
<!--        type="primary"-->
<!--        size="small"-->
<!--        class="analysis-button"-->
<!--        @click="viewNeuronsHandler"-->
<!--      >-->
<!--        View-->
<!--      </el-button>-->
<!--    </div>-->
<!--    <ul class="neuron-items">-->
<!--      <li-->
<!--        v-for="(item, i) in currentPageData"-->
<!--        :key="i"-->
<!--        class="neuron-item"-->
<!--      >-->
<!--        <el-checkbox-->
<!--          v-model="item.selected"-->
<!--          @change="checkNeuronCallback(item)"-->
<!--        />-->
<!--        <img-->
<!--          :src="item.img_src"-->
<!--          :title="item.id"-->
<!--          alt="neuron thumb"-->
<!--          class="neuron-thumb"-->
<!--        >-->
<!--        <div class="neuron-tags">-->
<!--          <el-tag-->
<!--            class="neuron-tag-item-cell-type"-->
<!--            :color="getTagColor(item.celltype)"-->
<!--            effect="dark"-->
<!--            size="mini"-->
<!--            @click="jumpAtlasWeb(item)"-->
<!--          >-->
<!--            {{ item.celltype }}-->
<!--          </el-tag>-->
<!--          <el-tag-->
<!--            class="neuron-tag-item"-->
<!--            :color="getTagColor('hemisphere')"-->
<!--            effect="dark"-->
<!--            size="mini"-->
<!--          >-->
<!--            {{ item.hemisphere }}-->
<!--          </el-tag>-->
<!--          <el-tag-->
<!--            v-for="(prop, j) in ['axon', 'dendrite', 'apical']"-->
<!--            :key="j"-->
<!--            class="neuron-tag-item"-->
<!--            :class="{ disabled: !item[`has_${prop}`] }"-->
<!--            :color="getTagColor(prop)"-->
<!--            effect="dark"-->
<!--            size="mini"-->
<!--          >-->
<!--            <template v-if="prop === 'dendrite'">-->
<!--              basal-->
<!--            </template>-->
<!--            <template v-else>-->
<!--              {{ prop }}-->
<!--            </template>-->
<!--          </el-tag>-->
<!--          <el-tag-->
<!--            class="neuron-tag-item"-->
<!--            :color="getTagColor(item.id.split('_')[0].split('-')[0])"-->
<!--            effect="dark"-->
<!--            size="mini"-->
<!--          >-->
<!--            <template v-if="item.id.split('_')[0].split('-')[0] === 'MouseLight'">-->
<!--              Janelia-->
<!--            </template>-->
<!--            <template v-else-if="item.id.split('_')[0].split('-')[0] === 'SEU'">-->
<!--              seuallen-->
<!--            </template>-->
<!--            <template v-else>-->
<!--              ION-->
<!--            </template>-->
<!--          </el-tag>-->
<!--        </div>-->
<!--        <el-button-->
<!--          type="primary"-->
<!--          size="small"-->
<!--          @click="neuronViewHandler(item)"-->
<!--        >-->
<!--          Info-->
<!--        </el-button>-->
<!--      </li>-->
<!--    </ul>-->
<!--    <el-pagination-->
<!--      class="pager"-->
<!--      background-->
<!--      small-->
<!--      layout="prev, pager, next"-->
<!--      :total="data.length"-->
<!--      :page-size="pageSize"-->
<!--      :current-page.sync="currentPage"-->
<!--      :pager-count="7"-->
<!--      @current-change="gotoPage"-->
<!--    />-->
<!--    <el-row-->
<!--      class="pager"-->
<!--      type="flex"-->
<!--      justify="center"-->
<!--    >-->
<!--      <el-col :span="8">-->
<!--        <el-input-->
<!--          v-model="targetPage"-->
<!--          placeholder="跳转到页码"-->
<!--        />-->
<!--      </el-col>-->
<!--      <el-col :span="8">-->
<!--        <el-button-->
<!--          type="primary"-->
<!--          @click="goToTargetPage"-->
<!--        >-->
<!--          go to page-->
<!--        </el-button>-->
<!--      </el-col>-->
<!--    </el-row>-->
<!--  </div>-->
<!--</template>-->

<!--<script lang="ts">-->
<!--import { Component, Vue, Watch } from 'vue-property-decorator'-->
<!--import ColorPicker from './ColorPicker.vue'-->

<!--@Component-->
<!--export default class NeuronList extends Vue {-->
<!--    // 搜索结果的所有数据-->
<!--    private data: any[] = []-->
<!--    // 当前分页的数据-->
<!--    private currentPageData: any[] = []-->
<!--    private pageSize: number = 10-->
<!--    private currentPage: number = 1-->
<!--    private targetPage : number = 1-->
<!--    private checkAll: boolean = false-->
<!--    private checkAllPages: boolean = false-->
<!--    private isIndeterminate: boolean = false-->

<!--    // 当前这一页选中的 item-->
<!--    get currentPageSelectedItem () {-->
<!--      console.log(this.currentPageData)-->
<!--      return this.currentPageData.filter((item: any) => item.selected === true)-->
<!--    }-->

<!--    /**-->
<!--     * 获取列表第一个数据-->
<!--     */-->
<!--    public getFirstItem () {-->
<!--      return this.data.length ? this.data[0] : null-->
<!--    }-->

<!--    /**-->
<!--     * 获取列表中勾选的数据-->
<!--     */-->
<!--    public getSelectedItems () {-->
<!--      console.log('getSelectedItems-&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;')-->
<!--      console.log(this.data.filter((item: any) => item.selected))-->
<!--      return this.data.filter((item: any) => item.selected)-->
<!--    }-->

<!--    /**-->
<!--     * 设置列表的数据-->
<!--     * @param listData 列表数据-->
<!--     */-->
<!--    public setListData (listData: any[]) {-->
<!--      console.log('listData')-->
<!--      console.log(listData)-->
<!--      listData.forEach((item: any) => {-->
<!--        item.selected = false-->
<!--      })-->
<!--      this.data = listData-->
<!--      this.gotoPage(1)-->
<!--      this.checkAll = false-->
<!--    }-->

<!--    /**-->
<!--     * 批量选择-->
<!--     * @param val 选择或者取消选择-->
<!--     */-->
<!--    private batchSelectHandler (val: boolean) {-->
<!--      this.currentPageData.forEach((item: any) => {-->
<!--        item.selected = val-->
<!--        this.$emit('checkNeuron', item)-->
<!--      })-->
<!--      this.isIndeterminate = false-->
<!--    }-->

<!--    private batchSelectHandlerAll (val: boolean) {-->
<!--      console.log(val)-->
<!--      this.data.forEach((item: any) => {-->
<!--        item.selected = val-->
<!--        this.$emit('checkNeuron', item)-->
<!--      })-->
<!--      this.isIndeterminate = false-->
<!--    }-->

<!--    /**-->
<!--     * 批量选择神经元之后点击统计分析按钮-->
<!--     */-->
<!--    private neuronAnalysisHandler () {-->
<!--      const selectedNeuronIds = this.data.filter((item: any) => item.selected).map((item: any) => item.id)-->
<!--      console.log(selectedNeuronIds)-->
<!--      if (selectedNeuronIds.length === 0) {-->
<!--        this.$message.warning('No neuron selected')-->
<!--        return-->
<!--      }-->
<!--      this.$emit('neuronAnalysis', selectedNeuronIds)-->
<!--    }-->

<!--    /**-->
<!--     * 批量选择神经元之后3D可视化-->
<!--     */-->
<!--    private viewNeuronsHandler () {-->
<!--      this.$emit('viewNeurons')-->
<!--    }-->

<!--    /**-->
<!--     * 点击查看按钮-->
<!--     * @param neuronDetail 神经元信息-->
<!--     */-->
<!--    private neuronViewHandler (neuronDetail: any) {-->
<!--      this.$emit('neuronView', neuronDetail)-->
<!--    }-->

<!--    /**-->
<!--     * 选中或取消右方神经元列表中的神经元的神经元的回调函数-->
<!--     * @param neuronDetail 神经元信息-->
<!--     */-->
<!--    private checkNeuronCallback (neuronDetail: any) {-->
<!--      console.log('checkNeuronCallback')-->
<!--      console.log(neuronDetail)-->
<!--      this.$emit('checkNeuron', neuronDetail)-->
<!--    }-->

<!--    /**-->
<!--     * 获取 neuron 属性标签对应的颜色-->
<!--     * @param prop 属性名称-->
<!--     * @private-->
<!--     */-->
<!--    private getTagColor (prop: string) {-->
<!--      const colorMap: { [key: string]: string } = {-->
<!--        axon: 'rgb(255, 0, 0)',-->
<!--        bouton: 'rgb(253, 242, 208)',-->
<!--        dendrite: 'rgb(0, 80, 255)',-->
<!--        apical: 'rgb(255, 0, 255)',-->
<!--        arbor: 'rgb(255, 121, 108)',-->
<!--        CCFv3: 'rgb(214, 253, 254)',-->
<!--        fMOST: 'rgb(159, 205, 99)',-->
<!--        ION: 'rgb(6,194,172)',-->
<!--        SEU: 'rgb(6,194,172)',-->
<!--        MouseLight: 'rgb(6,194,172)',-->
<!--        hemisphere: 'rgb(255, 121, 108)'-->
<!--      }-->
<!--      // console.log(colorMap[prop] || 'white')-->
<!--      return colorMap[prop] || 'white'-->
<!--    }-->

<!--    /**-->
<!--     * 切换分页-->
<!--     * @param whichPage 要切换的页数-->
<!--     * @private-->
<!--     */-->
<!--    private gotoPage (whichPage: number) {-->
<!--      let currentPage = whichPage || this.currentPage-->
<!--      let start = this.pageSize * (currentPage - 1)-->
<!--      let end = start + this.pageSize-->
<!--      this.currentPageData = this.data.slice(start, end)-->
<!--      this.currentPage = currentPage-->
<!--    }-->
<!--    private goToTargetPage () {-->
<!--      let currentPage = this.targetPage-->
<!--      let start = this.pageSize * (currentPage - 1)-->
<!--      let end = start + this.pageSize-->
<!--      this.currentPageData = this.data.slice(start, end)-->
<!--      this.currentPage = currentPage-->
<!--    }-->

<!--    private jumpAtlasWeb (item: any) {-->
<!--      window.location.href = `/CrossSpeciesAtlas.html#/${this.$route.params.lang}/?atlasName=${this.$store.state.atlas}&brainRegion=${item.celltype}`-->
<!--    }-->

<!--    @Watch('currentPageSelectedItem.length')-->
<!--    currentPageSelectedChanged (newVal: number) {-->
<!--      this.checkAll = newVal === this.currentPageData.length-->
<!--      this.isIndeterminate = newVal > 0 && newVal < this.currentPageData.length-->
<!--    }-->
<!--}-->
<!--</script>-->

<!--&lt;!&ndash; Add "scoped" attribute to limit CSS to this component only &ndash;&gt;-->
<!--<style scoped lang="less">-->
<!--.neuron-list-container {-->
<!--  width: 380px;-->
<!--  height: 100%;-->
<!--  padding: 20px;-->
<!--  display: flex;-->
<!--  //flex-flow: column nowrap;-->
<!--  flex-flow: column nowrap;-->
<!--  border-left: 1px solid gray;-->
<!--  .batch-actions {-->
<!--    display: flex;-->
<!--    //flex-flow: column nowrap;-->
<!--    flex-flow: row nowrap;-->
<!--    border-bottom: 1px solid gray;-->
<!--    padding: 0 0 20px 0;-->
<!--    .analysis-button {-->
<!--      margin-left: 20px;-->
<!--    }-->
<!--  }-->
<!--  .batch-select {-->
<!--    display: flex;-->
<!--    flex-direction: column;-->
<!--  }-->
<!--  .neuron-items {-->
<!--    height: 0;-->
<!--    overflow: auto;-->
<!--    flex: 1 1 auto;-->
<!--    .neuron-item {-->
<!--      border-bottom: 1px solid gray;-->
<!--      padding: 15px 0;-->
<!--      white-space: nowrap;-->
<!--      > * {-->
<!--        display: inline-block;-->
<!--        vertical-align: middle;-->
<!--        margin-right: 10px;-->
<!--      }-->
<!--      .neuron-thumb {-->
<!--        width: 70px;-->
<!--        border: 1px solid gray;-->
<!--      }-->
<!--      .neuron-tags {-->
<!--        width: 160px;-->
<!--        text-align: center;-->
<!--        white-space: initial;-->
<!--        .neuron-tag-item {-->
<!--          display: inline-block;-->
<!--          margin: 3px;-->
<!--          width: 60px;-->
<!--          text-align: center;-->
<!--          color: black;-->
<!--        }-->
<!--        .neuron-tag-item-cell-type {-->
<!--          display: inline-block;-->
<!--          margin: 3px;-->
<!--          width: 60px;-->
<!--          text-align: center;-->
<!--          color: black;-->
<!--        }-->
<!--        .neuron-tag-item-cell-type:hover {-->
<!--          cursor: pointer;-->
<!--        }-->
<!--      }-->
<!--    }-->
<!--  }-->
<!--  .pager {-->
<!--    margin-top: 20px;-->
<!--  }-->
<!--}-->
<!--</style>-->
