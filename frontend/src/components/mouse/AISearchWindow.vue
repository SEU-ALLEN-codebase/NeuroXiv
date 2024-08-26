<template>
  <div class="chat-window">
    <div class="chat-messages">
      <div
        v-for="(message, index) in messages"
        :key="index"
        class="message-container"
        :class="{'user-message-container': message.isUser, 'system-message-container': !message.isUser}"
      >
        <img
          v-if="!message.isUser"
          src="../../../public/img/AIPOM.png"
          alt="System Avatar"
          class="avatar system-avatar"
        >
        <div
          class="message-bubble"
          :class="{'user-message': message.isUser, 'system-message': !message.isUser}"
        >
          <span v-html="message.text" />
          <button
            v-if="isPythonCode(message.text)"
            class="execute-code-btn"
            @click="executePythonCode(message.text)"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="icon-play"
            >
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
          </button>
          <div class="message-timestamp">
            {{ message.timestamp }}
          </div>
        </div>
        <img
          v-if="message.isUser"
          src="../../../public/img/User.png"
          alt="User Avatar"
          class="avatar user-avatar"
        >
      </div>
    </div>
    <input
      v-model="userInput"
      placeholder="Type a message..."
      class="input-box"
      @keyup.enter="$emit('AISearch')"
    >
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import searchConditions from './search_conditions.json'

interface Criteria {
  [key: string]: any
}

interface SearchNode {
  // eslint-disable-next-line camelcase
  querry_name: string
  type: string
  // eslint-disable-next-line camelcase
  display_name: string
  // eslint-disable-next-line camelcase
  help_info: string
  // eslint-disable-next-line camelcase
  structure_tree: string
  candidates: any[]
  // eslint-disable-next-line camelcase
  min_value: number | null
  // eslint-disable-next-line camelcase
  max_value: number | null
  // eslint-disable-next-line camelcase
  default_min: number | null
  // eslint-disable-next-line camelcase
  default_max: number | null
  name: string
  children?: SearchNode[]
}

@Component
export default class AISearchWindow extends Vue {
  public messages: {text: string, isUser: Boolean, timestamp: string}[] = []
  private userInput: string = ''
  public lastInput: string = ''
  private Conditions: any = searchConditions.children
  public code: string = ''

  public scrollToBottom () {
    this.$nextTick(() => {
      const container = this.$el.querySelector('.chat-messages')
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    })
  }

  public sendMessage () {
    const userMessage = this.userInput
    if (userMessage) {
      const currentTime = new Date()
      const timestamp = currentTime.getHours().toString().padStart(2, '0') + ':' + currentTime.getMinutes().toString().padStart(2, '0')

      this.messages.push({
        text: userMessage,
        isUser: true,
        timestamp: timestamp
      })
      this.lastInput = userMessage
      this.userInput = ''
      this.scrollToBottom()
    }
  }

  public setCode (code: string) {
    this.code = code
  }

  public isPythonCode (text: string): boolean {
    return text.trim().includes('import')
  }

  public async executePythonCode (code: string) {
    this.$emit('executeCode')
  }

  formatTimestamp (date: Date): string {
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  }

  public addResponseFromAPI (data: any) {
    const currentTime = new Date()
    const timestamp = currentTime.getHours().toString().padStart(2, '0') + ':' + currentTime.getMinutes().toString().padStart(2, '0')

    if (typeof data === 'string') {
      this.messages.push({
        text: data, isUser: false, timestamp
      })
    } else if (Array.isArray(data) && data.length > 0) {
      // eslint-disable-next-line camelcase
      data.forEach((article: { title: string; authors: string;relevance_score: number; related_content: string;summary: string; link: string }, index: number) => {
        let responseMessage = `<span style="font-weight: bold; font-size: larger;">${index + 1}. Article Title:</span> ${article.title}<br>
          <span style="font-weight: bold; font-size: larger;">Authors:</span> ${article.authors}<br>
          <span style="font-weight: bold; font-size: larger;">Relevance Score:</span> ${article.relevance_score}<br>
          <span style="font-weight: bold; font-size: larger;">Related Content:</span> ${article.related_content}<br>
          <span style="font-weight: bold; font-size: larger;">Summary:</span> ${article.summary}<br>
          <span style="font-weight: bold; font-size: larger;">Link:</span> <a href="${article.link}" target="_blank" style="text-decoration: underline; color: #007bff">${article.link}</a>`
        this.messages.push({ text: responseMessage, isUser: false, timestamp })
      })
    } else if (Array.isArray(data) && data.length === 0) {
      this.messages.push({ text: 'No results found.', isUser: false, timestamp })
    }
  }

  public confirmSearch () {
    this.$emit('AISearch')
  }

  public GetIntent (question: string) {
    if (!this.Conditions) return

    let criteria: Criteria = {}
    const words = question.trim().split(/\s+/)

    if (words.includes('axon')) {
      criteria['has_recon_axon'] = true
    }
    if (words.includes('apical')) {
      criteria['has_apical'] = true
    } else if (words.includes('dendrite')) {
      criteria['has_recon_den'] = true
    }
    this.matchConditions(this.Conditions, words, criteria, question.toLowerCase())

    return criteria
  }

  public matchConditions (node: any, words: string[], criteria: any, question: string) {
    if (!node) return

    const excludedConditions = ['has_recon_axon', 'has_recon_den', 'has_apical']
    const containsProjKeyword = words.some(word => word.toLowerCase().includes('projection' || 'project'))

    if (Array.isArray(node)) {
      node.forEach((child) => this.matchConditions(child, words, criteria, question))
    } else {
      if (node.querry_name && !excludedConditions.includes(node.querry_name)) {
        // 如果包含 "proj" 关键词，并且问题中没有提到 "projection"，则跳过处理
        if (node.querry_name.includes('proj') && !containsProjKeyword) {
          return
        }

        const querryNameKeyword = node.querry_name.toLowerCase()
        if (words.some(word => querryNameKeyword.includes(word.toLowerCase()))) {
          const numberRangeRegex = /\[(\d+(\.\d+)?),\s*(\d+(\.\d+)?)\]/
          const match = question.match(numberRangeRegex)
          if (match) {
            const value = [parseFloat(match[1]), parseFloat(match[3])]
            criteria[node.querry_name] = value
          } else if (node.default_min !== undefined && node.default_max !== undefined) {
            criteria[node.querry_name] = [node.default_min, node.default_max]
          } else {
            criteria[node.querry_name] = true
          }
        }

        if (Array.isArray(node.candidates)) {
          words.forEach((word) => {
            node.candidates.forEach((candidate: any) => {
              if (typeof candidate === 'string' && word.toLowerCase() === candidate.toLowerCase()) {
                if (!criteria[node.querry_name]) {
                  criteria[node.querry_name] = []
                }
                if (!criteria[node.querry_name].includes(candidate)) {
                  criteria[node.querry_name].push(candidate)
                }
              } else if (typeof candidate === 'boolean' && words.includes(node.querry_name.toLowerCase())) {
                criteria[node.querry_name] = true
              }
            })
          })
        }

        // 确保没有 None 这样的错误值
        if (Array.isArray(criteria[node.querry_name])) {
          criteria[node.querry_name] = criteria[node.querry_name].filter((value: any) => value !== null)
          if (criteria[node.querry_name].length === 0) {
            delete criteria[node.querry_name]
          }
        }
      }

      const ignoreKeywords = ['axon', 'dendrite', 'apical']
      if (!ignoreKeywords.some(keyword => node.name && node.name.toLowerCase().includes(keyword))) {
        if (node.children) {
          this.matchConditions(node.children, words, criteria, question)
        }
      }
    }
  }
}
</script>

<style scoped>
.chat-window {
  width: 100%;
  max-width: 768px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  background: #ffffff;
  margin: auto;
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  min-height: 300px;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  background: #f7f7f7;
  overflow-y: auto;
}

.message-bubble {
  background: #e1e1e1;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-radius: 20px;
  margin: 4px 0;
  padding: 10px 20px;
  display: inline-block;
  max-width: 70%;
}

.user-message {
  background: #007bff;
  color: white;
  float: right;
  clear: both;
  margin-right: 20px;
}

.system-message {
  background: #e1e1e1;
  color: black;
  float: left;
  clear: both;
  margin-left: 20px;
}

input {
  padding: 12px 20px;
  border-radius: 30px;
  border: 2px solid #007bff;
  margin: 10px 20px;
  width: calc(100% - 40px);
  box-sizing: border-box;
}

.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f0f0f0;
  border-radius: 10px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #bbb;
  border-radius: 10px;
}

.message-timestamp {
  font-size: 0.75em;
  margin-top: 5px;
  color: #999;
  text-align: right;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  margin: 4px;
}

.user-avatar {
  float: right;
}

.system-avatar {
  float: left;
}

.message-container {
  display: flex;
  align-items: flex-start;
  clear: both;
}

.user-message-container {
  justify-content: flex-end;
}

.system-message-container {
  justify-content: flex-start;
}

.execute-code-btn {
  background-color: #007bff;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  right: 10px;
  bottom: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: background-color 0.2s, transform 0.2s;
}

.icon-play {
  fill: white;
  width: 20px;
  height: 20px;
}

.execute-code-btn:hover {
  background-color: #0056b3;
}

.execute-code-btn:active {
  transform: scale(0.9);
}

.message-bubble {
  position: relative;
  padding: 10px 10px 10px 10px;
}

pre, code {
  background-color: #f4f4f4;
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 10px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
<!--<template>-->
<!--  <div class="chat-window">-->
<!--    <div class="chat-messages">-->
<!--      <div-->
<!--        v-for="(message, index) in messages"-->
<!--        :key="index"-->
<!--        class="message-container"-->
<!--        :class="{'user-message-container': message.isUser, 'system-message-container': !message.isUser}"-->
<!--      >-->
<!--        <img-->
<!--          v-if="!message.isUser"-->
<!--          src="../../../public/img/AIPOM.png"-->
<!--          alt="System Avatar"-->
<!--          class="avatar system-avatar"-->
<!--        >-->
<!--        <div-->
<!--          class="message-bubble"-->
<!--          :class="{'user-message': message.isUser, 'system-message': !message.isUser}"-->
<!--        >-->
<!--          <span v-html="message.text" />-->
<!--          <button-->
<!--            v-if="isPythonCode(message.text)"-->
<!--            class="execute-code-btn"-->
<!--            @click="executePythonCode(message.text)"-->
<!--          >-->
<!--            <svg-->
<!--              xmlns="http://www.w3.org/2000/svg"-->
<!--              viewBox="0 0 24 24"-->
<!--              fill="none"-->
<!--              stroke="currentColor"-->
<!--              stroke-width="2"-->
<!--              stroke-linecap="round"-->
<!--              stroke-linejoin="round"-->
<!--              class="icon-play"-->
<!--            >-->
<!--              <polygon points="5 3 19 12 5 21 5 3" />-->
<!--            </svg>-->
<!--          </button>-->
<!--          <div class="message-timestamp">-->
<!--            {{ message.timestamp }}-->
<!--          </div> &lt;!&ndash; 时间戳 &ndash;&gt;-->
<!--        </div>-->
<!--        <img-->
<!--          v-if="message.isUser"-->
<!--          src="../../../public/img/User.png"-->
<!--          alt="User Avatar"-->
<!--          class="avatar user-avatar"-->
<!--        >-->
<!--      </div>-->
<!--    </div>-->
<!--    <input-->
<!--      v-model="userInput"-->
<!--      placeholder="Type a message..."-->
<!--      class="input-box"-->
<!--      @keyup.enter="$emit('AISearch')"-->
<!--    >-->
<!--  </div>-->
<!--</template>-->

<!--<script lang="ts">-->

<!--import { Component, Vue } from 'vue-property-decorator'-->
<!--import searchConditions from './search_conditions.json'-->
<!--@Component-->

<!--export default class AISearchWindow extends Vue {-->
<!--  public messages: {text: string, isUser: Boolean, timestamp: string}[] = []-->
<!--  private userInput: string = ''-->
<!--  public lastInput: string = ''-->
<!--  private Conditions: any[] = searchConditions.children-->
<!--  public code:string = ''-->

<!--  public scrollToBottom () {-->
<!--    this.$nextTick(() => {-->
<!--      const container = this.$el.querySelector('.chat-messages')-->
<!--      if (container) { // 检查 container 是否为 null-->
<!--        container.scrollTop = container.scrollHeight-->
<!--      }-->
<!--    })-->
<!--  }-->

<!--  public sendMessage () {-->
<!--    const userMessage = this.userInput-->
<!--    if (userMessage) {-->
<!--      const currentTime = new Date() // 获取当前时间-->
<!--      // 格式化时间为 HH:MM 格式-->
<!--      const timestamp = currentTime.getHours().toString().padStart(2, '0') + ':' + currentTime.getMinutes().toString().padStart(2, '0')-->

<!--      this.messages.push({-->
<!--        text: userMessage,-->
<!--        isUser: true,-->
<!--        timestamp: timestamp // 添加时间戳属性-->
<!--      })-->
<!--      this.lastInput = userMessage-->
<!--      this.userInput = ''-->
<!--      // this.addResponseFromAPI(userMessage)-->
<!--      this.scrollToBottom()-->
<!--    }-->
<!--  }-->
<!--  public setCode (code: string) {-->
<!--    this.code = code-->
<!--  }-->

<!--  public isPythonCode (text: string): boolean {-->
<!--    return text.trim().includes('import')-->
<!--  }-->

<!--  public async executePythonCode (code: string) {-->
<!--    this.$emit('executeCode')-->
<!--  }-->

<!--  formatTimestamp (date: Date): string {-->
<!--    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`-->
<!--  }-->

<!--  // public addResponseFromAPI (Response: string) {-->
<!--  //   // Simulate a response from an API (replace with your actual API call)-->
<!--  //   if (Response !== this.lastInput) {-->
<!--  //     const responseMessage = 'SEU-Allen: ' + Response-->
<!--  //     const currentTime = new Date() // 获取当前时间-->
<!--  //     // 格式化时间为 HH:MM 格式-->
<!--  //     const timestamp = currentTime.getHours().toString().padStart(2, '0') + ':' + currentTime.getMinutes().toString().padStart(2, '0')-->
<!--  //     this.messages.push({ text: responseMessage, isUser: false, timestamp: timestamp })-->
<!--  //   }-->
<!--  // }-->

<!--  public addResponseFromAPI (data: any) {-->
<!--    // 获取当前时间戳-->
<!--    const currentTime = new Date() // 获取当前时间-->
<!--    //     // 格式化时间为 HH:MM 格式-->
<!--    const timestamp = currentTime.getHours().toString().padStart(2, '0') + ':' + currentTime.getMinutes().toString().padStart(2, '0')-->

<!--    // 如果传入的是字符串（原有需求）-->
<!--    if (typeof data === 'string') {-->
<!--      this.messages.push({-->
<!--        text: data, isUser: false, timestamp-->
<!--      })-->
<!--      // eslint-disable-next-line brace-style-->
<!--    }-->
<!--    // 如果传入的是对象数组（新需求）-->
<!--    else if (Array.isArray(data) && data.length > 0) {-->
<!--      data.forEach((article: { title: string; summary: string; link: string }, index: number) => {-->
<!--        let responseMessage = `<span style="font-weight: bold; font-size: larger;">${index + 1}. Article Title:</span> ${article.title}<br>-->
<!--  <span style="font-weight: bold; font-size: larger;">Summary:</span> ${article.summary}<br>-->
<!--  <span style="font-weight: bold; font-size: larger;">Link:</span> <a href="${article.link}" target="_blank" style="text-decoration: underline; color: #007bff">${article.link}</a>`-->
<!--        this.messages.push({ text: responseMessage, isUser: false, timestamp })-->
<!--      })-->
<!--      // eslint-disable-next-line brace-style-->
<!--    }-->
<!--    // 如果数组为空，表示没有搜索到结果-->
<!--    else if (Array.isArray(data) && data.length === 0) {-->
<!--      this.messages.push({ text: 'No results found.', isUser: false, timestamp })-->
<!--    }-->
<!--  }-->
<!--  public confirmSearch () {-->
<!--    this.$emit('AISearch')-->
<!--  }-->

<!--  public GetIntent (question: string) {-->
<!--    if (!this.Conditions) return-->

<!--    let criteria: any = {}-->
<!--    const words = question.trim().split(/\s+/)-->

<!--    // 遍历 JSON 文件并匹配条件-->
<!--    this.matchConditions(this.Conditions, words, criteria, question.toLowerCase())-->

<!--    return criteria-->
<!--  }-->

<!--  public matchConditions (node: any, words: string[], criteria: any, question: string) {-->
<!--    if (!node) return-->

<!--    if (Array.isArray(node)) {-->
<!--      node.forEach((child) => this.matchConditions(child, words, criteria, question))-->
<!--    } else {-->
<!--      if (node.querry_name) {-->
<!--        // 检查是否匹配querry_name（包含关系，不区分大小写）-->
<!--        const querryNameKeyword = node.querry_name.toLowerCase()-->
<!--        if (words.some(word => querryNameKeyword.includes(word.toLowerCase()))) {-->
<!--          // 检查数值型条件-->
<!--          const numberRangeRegex = /\[(\d+(\.\d+)?),\s*(\d+(\.\d+)?)\]/-->
<!--          const match = question.match(numberRangeRegex)-->
<!--          if (match) {-->
<!--            const value = [parseFloat(match[1]), parseFloat(match[3])]-->
<!--            criteria[node.querry_name] = value-->
<!--          } else if (node.default) {-->
<!--            criteria[node.querry_name] = node.default-->
<!--          } else {-->
<!--            criteria[node.querry_name] = true-->
<!--          }-->
<!--        }-->

<!--        // 检查candidates列表中的每个候选词-->
<!--        if (Array.isArray(node.candidates)) {-->
<!--          words.forEach((word) => {-->
<!--            node.candidates.forEach((candidate: any) => {-->
<!--              if (typeof candidate === 'string' && word.toLowerCase() === candidate.toLowerCase()) {-->
<!--                if (!criteria[node.querry_name]) {-->
<!--                  criteria[node.querry_name] = []-->
<!--                }-->
<!--                if (!criteria[node.querry_name].includes(candidate)) {-->
<!--                  criteria[node.querry_name].push(candidate)-->
<!--                }-->
<!--              }-->
<!--            })-->
<!--          })-->
<!--        }-->
<!--      }-->
<!--      if (node.children) {-->
<!--        this.matchConditions(node.children, words, criteria, question)-->
<!--      }-->
<!--    }-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.chat-window {-->
<!--  width: 100%; /* 聊天窗口宽度自适应父元素 */-->
<!--  max-width: 768px; /* 控制最大宽度 */-->
<!--  border-radius: 16px; /* 圆角边框 */-->
<!--  overflow: hidden; /* 防止子元素溢出边框 */-->
<!--  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); /* 更轻的阴影，增加立体感 */-->
<!--  background: #ffffff; /* 纯白背景 */-->
<!--  margin: auto; /* 居中显示 */-->
<!--  display: flex;-->
<!--  flex-direction: column; /* 垂直布局 */-->
<!--  max-height: 90vh; /* 最大高度不超过视口的90% */-->
<!--  min-height: 300px; /* 最小高度 */-->
<!--  overflow: hidden; /* 内容溢出时隐藏 */-->
<!--}-->

<!--.chat-messages {-->
<!--  flex: 1; /* 让消息列表填充所有可用空间 */-->
<!--  padding: 20px; /* 增加内部间距 */-->
<!--  background: #f7f7f7; /* 淡灰色背景 */-->
<!--  overflow-y: auto; /* 自动显示滚动条 */-->
<!--}-->

<!--.message-bubble {-->
<!--  background: #e1e1e1; /* 统一气泡背景色 */-->
<!--  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); /* 轻微阴影 */-->
<!--  border-radius: 20px; /* 圆角 */-->
<!--  margin: 4px 0; /* 消息间距 */-->
<!--  padding: 10px 20px; /* 内边距 */-->
<!--  display: inline-block; /* 保证气泡根据内容扩展 */-->
<!--  max-width: 70%; /* 控制气泡宽度 */-->
<!--}-->

<!--.user-message {-->
<!--  background: #007bff; /* 用户消息颜色 */-->
<!--  color: white; /* 用户消息文字颜色 */-->
<!--  float: right; /* 靠右浮动 */-->
<!--  clear: both; /* 避免相邻元素的浮动 */-->
<!--  margin-right: 20px; /* 与窗口边缘的间距 */-->
<!--}-->

<!--.system-message {-->
<!--  background: #e1e1e1; /* 系统消息颜色 */-->
<!--  color: black; /* 系统消息文字颜色 */-->
<!--  float: left; /* 靠左浮动 */-->
<!--  clear: both; /* 避免相邻元素的浮动 */-->
<!--  margin-left: 20px; /* 与窗口边缘的间距 */-->
<!--}-->

<!--input {-->
<!--  padding: 12px 20px; /* 输入框内边距 */-->
<!--  border-radius: 30px; /* 圆角边框 */-->
<!--  border: 2px solid #007bff; /* 边框颜色与用户消息气泡一致 */-->
<!--  margin: 10px 20px; /* 边距 */-->
<!--  width: calc(100% - 40px); /* 输入框宽度 */-->
<!--  box-sizing: border-box; /* 边框盒模型 */-->
<!--}-->

<!--/* 自适应滚动条样式 */-->
<!--.chat-messages::-webkit-scrollbar {-->
<!--  width: 8px;-->
<!--}-->

<!--.chat-messages::-webkit-scrollbar-track {-->
<!--  background: #f0f0f0;-->
<!--  border-radius: 10px; /* 圆角滚动条 */-->
<!--}-->

<!--.chat-messages::-webkit-scrollbar-thumb {-->
<!--  background: #bbb;-->
<!--  border-radius: 10px;-->
<!--}-->
<!--/* 时间戳样式 */-->
<!--.message-timestamp {-->
<!--  font-size: 0.75em;-->
<!--  margin-top: 5px;-->
<!--  color: #999;-->
<!--  text-align: right;-->
<!--}-->
<!--.avatar {-->
<!--    width: 40px; /* 设置头像宽度 */-->
<!--    height: 40px; /* 设置头像高度 */-->
<!--    border-radius: 50%; /* 圆形头像 */-->
<!--    object-fit: cover; /* 保持图片比例 */-->
<!--    margin: 4px; /* 头像与气泡间隔 */-->
<!--}-->

<!--.user-avatar {-->
<!--    float: right; /* 用户头像靠右 */-->
<!--}-->

<!--.system-avatar {-->
<!--    float: left; /* 系统头像靠左 */-->
<!--}-->

<!--.message-container {-->
<!--    display: flex;-->
<!--    align-items: flex-start; /* 对齐到底部 */-->
<!--    clear: both; /* 清除浮动 */-->
<!--}-->

<!--.user-message-container {-->
<!--    justify-content: flex-end; /* 用户气泡靠右 */-->
<!--}-->

<!--.system-message-container {-->
<!--    justify-content: flex-start; /* 系统气泡靠左 */-->
<!--}-->

<!--.execute-code-btn {-->
<!--    background-color: #007bff; /* Primary color */-->
<!--    border: none; /* No border */-->
<!--    border-radius: 50%; /* Circle shape */-->
<!--    width: 30px; /* Diameter of the button */-->
<!--    height: 30px; /* Diameter of the button */-->
<!--    cursor: pointer;-->
<!--    display: flex;-->
<!--    justify-content: center;-->
<!--    align-items: center;-->
<!--    right: 10px;-->
<!--    bottom: 10px;-->
<!--    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); /* Subtle shadow for depth */-->
<!--    transition: background-color 0.2s, transform 0.2s; /* Smooth transitions for feedback */-->
<!--}-->

<!--.icon-play {-->
<!--    fill: white; /* Icon color contrast */-->
<!--    width: 20px; /* Icon size */-->
<!--    height: 20px; /* Icon size */-->
<!--}-->

<!--.execute-code-btn:hover {-->
<!--    background-color: #0056b3; /* Darker shade on hover */-->
<!--}-->

<!--.execute-code-btn:active {-->
<!--    transform: scale(0.9); /* Slightly shrink the button when clicked */-->
<!--}-->

<!--.message-bubble {-->
<!--    position: relative; /* Needed for absolute positioning of the button */-->
<!--    padding: 10px 10px 10px 10px ; /* Adjust padding to give space for the button */-->
<!--}-->

<!--pre, code {-->
<!--  background-color: #f4f4f4; /* 浅灰色背景，突出显示代码区域 */-->
<!--  border: 1px solid #ddd; /* 边框 */-->
<!--  border-radius: 5px; /* 圆角边框 */-->
<!--  padding: 10px; /* 内边距 */-->
<!--  overflow: auto; /* 超长代码滚动 */-->
<!--  white-space: pre-wrap; /* 保持空白符 */-->
<!--  word-break: break-all; /* 单词断行 */-->
<!--}-->
<!--</style>-->
