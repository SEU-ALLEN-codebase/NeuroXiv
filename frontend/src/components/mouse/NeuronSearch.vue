<template>
  <div class="search-panel">
    <section class="all-conditions condition-section">
      <h3 class="section-label">
        Menu
      </h3>
      <div class="conditions-container">
        <el-input
          v-model="allConditionFilterText"
          class="condition-filter-input"
          placeholder="Filter keyword"
          size="mini"
        />
        <el-tree
          ref="searchConditionsTree"
          class="search-conditions-tree"
          :data="searchConditions"
          node-key="querry_name"
          :props="{ label: 'name' }"
          :filter-node-method="filterAllConditions"
        >
          <span
            slot-scope="{ node, data }"
            class="custom-tree-node"
          >
            <span :title="data.help_info">{{ node.label }}</span>
            <span>
              <el-button
                v-if="node.isLeaf"
                :disabled="selectedConditionsMap[data.querry_name]"
                type="text"
                size="mini"
                @click="addCondition(data)"
              >
                Add
              </el-button>
            </span>
          </span>
        </el-tree>
      </div>
    </section>
    <section class="selected-conditions condition-section">
      <h3 class="section-label">
        Current Query
      </h3>
      <div class="upload-config">
        <el-upload
          action=""
          accept=".csv,.json"
          :show-file-list="false"
          :before-upload="beforeUploadFile"
          :on-change="loadNeuronList"
        >
          <el-button type="text">
            Load Neuron List
          </el-button>
        </el-upload>
      </div>
      <div class="button-config">
        <el-button
          type="text"
          @click="loadSearchConfig"
        >
          Load Search Config
        </el-button>
        <el-button
          type="text"
          :disabled="selectedConditions.length === 0"
          @click="saveSearchConfig"
        >
          Save Search Config
        </el-button>
      </div>
      <div class="conditions-container">
        <el-input
          v-model="selectedConditionFilterText"
          class="condition-filter-input"
          placeholder="Filter keyword"
          size="mini"
        />
        <ul class="conditions-list">
          <template v-for="(item, i) in selectedConditions">
            <li
              v-if="item.visible"
              :key="i"
              class="condition-item"
            >
              <span
                class="condition-name text-ellipsis"
                :title="item.display_name"
              >
                {{ item.display_name }}
              </span>
              <span
                v-if="item.type === 'category'"
                class="condition-value category-value"
              >
                <span
                  class="selected-category text-ellipsis"
                  :title="item.selectedCategory"
                >
                  {{ item.selectedCategory }}
                </span>
                <el-button
                  type="text"
                  size="mini"
                  class="category-edit-button"
                  @click="editCategory(item)"
                >
                  Edit
                </el-button>
              </span>
              <span
                v-if="item.type === 'binary'"
                class="condition-value binary-value"
              >
                <el-radio
                  v-model="item.selectedBinary"
                  :label="true"
                >True</el-radio>
                <el-radio
                  v-model="item.selectedBinary"
                  :label="false"
                >False</el-radio>
              </span>
              <span
                v-if="item.type === 'range'"
                class="condition-value range-value"
              >
                min:
                <el-input-number
                  v-model="item.default_min"
                  :step="0.1"
                  :min="item.min_value"
                  :max="item.max_value === null ? Infinity : item.max_value"
                  size="mini"
                  class="range-item"
                />
                max:
                <el-input-number
                  v-model="item.default_max"
                  :step="0.1"
                  :min="item.min_value"
                  :max="item.max_value === null ? Infinity : item.max_value"
                  size="mini"
                  class="range-item"
                />
              </span>
              <el-button
                type="text"
                size="mini"
                @click="removeCondition(i)"
              >
                Delete
              </el-button>
            </li>
          </template>
        </ul>
      </div>
    </section>
    <!-- category 类型的搜索条件类别选择穿梭框 -->
    <NeuronSearchConditionPicker ref="conditionPicker" />
    <!-- Search Config对话框  -->
    <el-dialog
      title="Load Search Config"
      :visible.sync="searchConfigDialogVisible"
      center
      width="650px"
      :close-on-click-modal="false"
      :append-to-body="true"
    >
      <el-table
        :data="searchConfigs"
        style="width: 100%"
      >
        <el-table-column
          label="time"
          width="240px"
        >
          <template slot-scope="scope">
            <i class="el-icon-time" />
            <span style="margin-left: 10px">{{ scope.row.configTime }}</span>
          </template>
        </el-table-column>
        <el-table-column
          label="Search config name"
          width="180px"
        >
          <template slot-scope="scope">
            <span style="margin-left: 10px">{{ scope.row.configName }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Action">
          <template slot-scope="scope">
            <div class="action">
              <el-button
                size="mini"
                @click="handleSelect(scope.$index)"
              >
                Select
              </el-button>
              <el-button
                size="mini"
                type="danger"
                @click="handleDelete(scope.$index)"
              >
                Delete
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Ref, Watch } from 'vue-property-decorator'
import { ElTree } from 'element-ui/types/tree'
import NeuronSearchConditionPicker from '@/components/mouse/NeuronSearchConditionPicker.vue'
import moment from 'moment'
import { debounce } from 'lodash'
import Papa from 'papaparse'

const searchConditions = require('./search_conditions.json')
@Component({
  components: { NeuronSearchConditionPicker }
})
export default class NeuronSearch extends Vue {
  @Ref('searchConditionsTree') readonly searchConditionsTree!: ElTree<any, any>
  @Ref('conditionPicker') readonly conditionPicker!: NeuronSearchConditionPicker

  private searchConditions: any[] = searchConditions.children
  public selectedConditions: any[] = []
  private allConditionFilterText: string = ''
  private selectedConditionFilterText: string = ''
  // search config
  private searchConfigs: any[] = []
  private searchConfigDialogVisible: boolean = false
  // 防抖的filter，只在第一次搜索时赋值
  private debounceAllConditionFilter: any = null
  public uploadNeuronList:any[] = []
  public hasNeuronList:boolean = false

  // 选中的搜索条件 map, key 为 query_name
  get selectedConditionsMap () {
    return this.selectedConditions.reduce((prev: any, current: any) => {
      prev[current.querry_name] = true
      return prev
    }, {})
  }

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

  /**
   * 筛选选中的搜索条件
   * @private
   */
  private filterSelectedConditions () {
    this.selectedConditions.forEach((item: any) => {
      item.visible = item.name.indexOf(this.selectedConditionFilterText) !== -1
    })
  }

  /**
   * 保存搜索条件
   * @private
   */
  private async saveSearchConfig () {
    try {
      // @ts-ignore
      const name = (await this.$prompt('Please input your search configure name:')).value
      if (name === null) {
        alert('configure name should not be null!')
        return
      }
      const curTimeStr = moment().format()
      let s = []
      if (localStorage.getItem('searchConfig')) {
        // @ts-ignore
        s = JSON.parse(localStorage.getItem('searchConfig'))
      }
      s.push({
        configName: name,
        configTime: curTimeStr,
        searchConfig: this.selectedConditions
      })
      localStorage.setItem('searchConfig', JSON.stringify(s))
      this.$message({
        message: 'Saved successfully!',
        type: 'success'
      })
    } catch (e) {
      console.log(e)
    }
  }

  /**
   * 加载已保存的搜索条件对话框
   * @private
   */
  private loadSearchConfig () {
    if (localStorage.getItem('searchConfig')) {
      // @ts-ignore
      this.searchConfigs = JSON.parse(localStorage.getItem('searchConfig'))
    } else {
      this.searchConfigs = []
    }
    this.searchConfigDialogVisible = true
  }

  /**
   * 选择某一搜索条件
   * @param index 要选择条件的索引
   * @private
   */
  private handleSelect (index: any) {
    this.selectedConditions = this.searchConfigs[index]['searchConfig']
    this.searchConfigDialogVisible = false
  }

  /**
   * 删除某一搜索条件
   * @param index 要删除条件的索引
   * @private
   */
  private handleDelete (index: any) {
    this.searchConfigs.splice(index, 1)
    localStorage.setItem('searchConfig', JSON.stringify(this.searchConfigs))
  }

  @Watch('allConditionFilterText')
  allConditionFilterChanged (newVal: string) {
    if (!this.debounceAllConditionFilter) {
      this.debounceAllConditionFilter = debounce(this.searchConditionsTree.filter, 500)
    }
    this.debounceAllConditionFilter(newVal)
  }

  @Watch('selectedConditionFilterText')
  selectedConditionFilterChanged () {
    this.filterSelectedConditions()
  }

  private beforeUploadFile (file: any) {
    const fileSuffix = file.name.substring(file.name.lastIndexOf('.') + 1)
    if (fileSuffix !== 'csv' && fileSuffix !== 'json') {
      this.$message('The upload file must be a csv or json file!')
      return false
    }
    return true
  }

  private async loadNeuronList (param: any) {
    const file = param.raw
    const reader = new FileReader()
    reader.onload = async (e: any) => {
      const fileContent = e.target.result
      if (file.name.endsWith('.csv')) {
        await this.processCsv(fileContent)
      } else if (file.name.endsWith('.json')) {
        await this.processJson(fileContent)
      }
      this.hasNeuronList = true
      this.$emit('neuronAnalysis', this.uploadNeuronList, true)
    }
    reader.readAsText(file)
  }

  private async processCsv (csvContent: string) {
    return new Promise((resolve, reject) => {
      Papa.parse(csvContent, {
        complete: (results: any) => {
          this.uploadNeuronList = results.data.slice(1).map((row: any) => row[0])
          console.log(this.uploadNeuronList)
          resolve(true)
        },
        error: (error: any) => {
          console.error(error)
          reject(error)
        }
      })
    })
  }

  private async processJson (jsonContent: string) {
    return new Promise((resolve, reject) => {
      try {
        const data = JSON.parse(jsonContent)
        if (Array.isArray(data.neuronsList)) {
          this.uploadNeuronList = data.neuronsList.map((item: any) => item.id)
          console.log(this.uploadNeuronList)
          resolve(true)
        } else {
          this.$message('Invalid JSON format: neuronsList is not an array')
          reject(new Error('Invalid JSON format'))
        }
      } catch (error) {
        console.error(error)
        reject(error)
      }
    })
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.search-panel {
  display: flex;
  flex-flow: row nowrap;
  .condition-section {
    width: 50%;
    flex: 1 1 auto;
    position: relative;
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
    .upload-config{
      position: absolute;
      top: 0;
      right: 320px;
      .el-button {
        padding: 0;
        margin-right: 20px;
      }
    }
    .conditions-container {
      border: 1px solid grey;
      max-height: 800px;
      height: calc(70vh - 250px);
      overflow: auto;
      border-radius: 3px;
      padding: 10px;
      .condition-filter-input {
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
