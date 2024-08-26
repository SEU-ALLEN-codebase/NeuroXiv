<template>
  <div class="search-panel">
    <section class="all-conditions condition-section">
      <h3 class="section-label">
        AI Advice
      </h3>
      <div class="conditions-container">
        <el-input
          v-model="AIAdvice"
          class="condition-filter-input"
          placeholder="advice provided by AIGC model"
          size="mini"
        />
      </div>
    </section>
    <section class="all-conditions condition-section">
      <h3 class="section-label">
        Your Question
      </h3>
      <div class="conditions-container">
        <el-input
          v-model="userQuestion"
          @input="handleQuestion"
          class="condition-filter-input"
          placeholder="input your question"
          size="mini"
        />
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Ref, Watch } from 'vue-property-decorator'
import { ElTree } from 'element-ui/types/tree'
import NeuronSearchConditionPicker from '@/components/mouse/NeuronSearchConditionPicker.vue'
import moment from 'moment'
import { debounce } from 'lodash'

const searchConditions = require('./search_conditions.json')
@Component({
  components: { NeuronSearchConditionPicker }
})
export default class NeuronLLM extends Vue {
    @Ref('searchConditionsTree') readonly searchConditionsTree!: ElTree<any, any>
    @Ref('conditionPicker') readonly conditionPicker!: NeuronSearchConditionPicker

    private searchConditions: any[] = searchConditions.children
    public selectedConditions: any[] = []
    private AIAdvice: string = ''
    private userQuestion: string = ''
    private debounceAllConditionFilter: any = null

    // 选中的搜索条件 map, key 为 query_name
    get selectedConditionsMap () {
      return this.selectedConditions.reduce((prev: any, current: any) => {
        prev[current.querry_name] = true
        return prev
      }, {})
    }

    public getQuestion () {
      return this.userQuestion
    }
    // private handleQuestion () {
    //   return question
    // }
    /**
     * 获取当前选中的搜索条件参数
     */
    public getSearchCriteria () {
      return this.selectedConditions.reduce((prev: any, current: any) => {
        let type = current.type
        let query = current.querry_name
        if (type === 'category') {
          prev[query] = current.selectedCategory
        } else if (type === 'binary') {
          prev[query] = current.selectedBinary
        } else if (type === 'range') {
          prev[query] = [current.default_min, current.default_max]
        }
        return prev
      }, {})
    }

    /**
     * category 类型的搜索条件选择类型
     * @param candidates 待选择的类型列表
     * @param selectedCandidates 已选择的类型列表
     * @param searchConditionLabel 当前的搜索条件名称
     */
    private searchCategorySelect (candidates: string[], selectedCandidates: string[], searchConditionLabel: string) {
      this.conditionPicker.show = true
      this.conditionPicker.conditionName = searchConditionLabel
      this.conditionPicker.setData(candidates, selectedCandidates)
      return new Promise((resolve, reject) => {
        this.conditionPicker.$once('confirm', resolve) // 点击确认按钮的时候先触发 confirm 事件, 再触发 close 事件, confirm 的时候 promise 已经 fulfilled 了, 所以不会受到后面的 close 事件的影响
        this.conditionPicker.$once('close', reject)
      })
    }

    /**
     * 添加搜索条件
     * @param data 选中的搜索条目信息
     * @private
     */
    private async addCondition (data: any) {
      if (data.type === 'category') {
        try {
          const selectedCategory = await this.searchCategorySelect(data.candidates, [], data.name)
          this.selectedConditions.push({
            ...data,
            visible: true,
            selectedCategory
          })
        } catch (e) {
          console.warn('cancel category select')
        }
      } else if (data.type === 'binary') {
        this.selectedConditions.push({
          ...data,
          visible: true,
          selectedBinary: true
        })
      } else if (data.type === 'range') {
        this.selectedConditions.push({
          ...data,
          visible: true
        })
      }
    }

    /**
     * 编辑搜索条件 category
     * @param data 搜索条目信息
     */
    private async editCategory (data: any) {
      try {
        data.selectedCategory = await this.searchCategorySelect(data.candidates, data.selectedCategory, data.name)
      } catch (e) {
        console.warn('cancel category select')
      }
    }

    /**
     * 删除搜索条件
     * @param index 要删除的搜索条件索引
     * @private
     */
    private removeCondition (index: number) {
      this.selectedConditions.splice(index, 1)
    }

    /**
     * 筛选所有的搜索条件
     * @param value 输入的关键字
     * @param data 搜索条目信息
     * @param node 节点
     * @private
     */
    private filterAllConditions (value: string, data: any, node: any) {
      if (!value) return true
      return this.findSearchKey(node, value)
    }
    /**
     * 递归往上查找 node.label 是否包含 key
     * @param node 节点
     * @param key 要查找的 key
     */
    private findSearchKey (node:any, key: string): boolean {
      if (!node.label) {
        return false
      }
      if (node.label.indexOf(key) !== -1) {
        return true
      }
      if (!node.parent) {
        return false
      }
      return this.findSearchKey(node.parent, key)
    }



    @Watch('allConditionFilterText')
    allConditionFilterChanged (newVal: string) {
      if (!this.debounceAllConditionFilter) {
        this.debounceAllConditionFilter = debounce(this.searchConditionsTree.filter, 500)
      }
      this.debounceAllConditionFilter(newVal)
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.search-panel {
  display: flex;
  flex-flow: column;
  .condition-section {
    width: 100%;
    flex: 1 1 auto;
    position: relative;
    margin-bottom: 20px;
    .section-label {
      margin-top: 0;
    }
    .button-config {
      position: absolute;
      top: 0;
      right: 0;
      .el-button {
        padding: 0;
        margin-right: 20px;
      }
    }
    .conditions-container {
      border: 1px solid grey;
      max-height: 200px;
      height: calc(70vh - 250px);
      overflow: auto;
      border-radius: 3px;
      padding: 10px;
      .condition-filter-input {
        height: 100%;
        margin-bottom: 10px;
      }
    }
  }
  .all-conditions {
    margin-right: 20px;
    .conditions-container {
      .search-conditions-tree {
        .custom-tree-node {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding-right: 8px;
        }
      }
    }
  }
  .selected-conditions {
    .conditions-list {
      .condition-item {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 5px;
        .condition-name {
          cursor: pointer;
          width: 150px;
        }
        .condition-value {
          // width: 300px;
          &.category-value {
            .selected-category, .category-edit-button {
              vertical-align: middle;
            }
            .selected-category {
              cursor: pointer;
              max-width: 260px;
            }
          }
          &.range-value {
            .range-item {
              width: 130px;
            }
          }
        }
      }
    }
  }
  .action {
    white-space: nowrap;
    .el-button {
      display: inline;
    }
  }
}
</style>
