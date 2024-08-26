# vuecli4-template

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Run your unit tests
```
npm run test:unit
```

### Run your end-to-end tests
```
npm run test:e2e
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

### 在原来的基础上添加的功能列表
#### javascript 🚀
- 通用的请求代码 `src/request`, 
1. 可以设置通用的 request options  
2. 可以对返回的数据重新适配  
3. 自动显示或者隐藏 loading, 自动显示成功或者失败的提示  
4. 可以设置超时
5. 可以取消请求
6. 调用接口检测到没有登录的时候会自动提示跳转到登录页面
- 添加 utility, 包含 `getRandomNumber, getRandomColor, radToDeg, degToRad, sleep, queryStringBuilder, wait` 等
#### styles 🏞️
- 引入了 Element UI
- 添加全局通用的样式, reset scrollbar animations 等
#### config ⚙️
- 添加一个全局配置文件(config.json), 可以设置 API 路径、QQ 登录相关参数等
- 添加 proxy table 配置解决测试环境 API 请求跨域问题, 包括 websocket 的代理配置
#### 登录验证 🔑
- 添加登录验证, 路由切换的时候判断如果没有登录会重定向到登录页面以及退出登录
- 添加 QQ 登录支持
- 添加电子邮箱登录功能以及相关的表单
- 添加登录方式选择组件, 支持 QQ、WeChat、email
- 添加电子邮件注册页面和表单组件
#### CustomError(CustomException)
- 添加了 API 报错 error(code !== 0), APIError
#### 安全性相关 🚨
- 请求添加 token 验证, 防止 XSRF 攻击(似乎通过 cookie sameSite 属性就可以避免了, 但古董浏览器可能不支持)
#### i18n 🌍
- 可以保存用户的语言设置, 没有设置的话读取系统语言设置
- 可以把语言设置在路由上面, 例如 `http://sange.com/en/home`
- 语言文件异步按需加载
- 添加了一个语言切换组件
#### 主题切换 🎨
- 可以保存用户的主题设置, 没有设置的话读取系统主题
- 主题文件异步按需加载
- 添加了一个语言切换组件
#### SEO 🔍
- 添加 prerender-spa-plugin 配置, 可以对路由页面预渲染处理
#### 页面布局 🧩
- 添加 Nav 导航菜单组件, 可以切换路由, 导航菜单使用 json 配置, 展开收起有动画效果
- 添加 header bar 组件, 有语言切换、主题切换、消息查看和推送、退出登录功能
- 添加首页布局, 顶部工具条、导航菜单、内容区域
- 添加面包屑, 自动根据当前的路由更新
#### 路由切换 🗺
- 添加几个页面的路由切换, 设置了 fade 切换效果
- 添加 404 页面
#### 浏览器兼容性 🧭
- 检测到 IE 浏览器(判断 UA 是否包含 Trident)的时候提示升级浏览器(chrome firefox)
- 非苹果设备自动添加滚动条样式
#### filters ⏳
- 保留 N 位小数 `fixNumber`
- 转换为百分比显示 `toPercent`
- 数字添加千分位分隔符 `addThousandDelimiter`
- 截断文字并添加省略号 `toEllipsisText`
#### 消息推送配置 ✉️
- 使用 socket.io 建立长连接, 消息实时推送
- 添加了一个消息查看组件, 可以查看最近消息
- 支持命名空间, 不同的页面设置不同的命名空间
#### 所有页面的初始化配置脚本 `pageInitSetup.ts`
- 根据当前的设备决定是否添加滚动条样式
#### 通用组件 🛠
- CaptchaInput.vue

验证码组件, 输入过程中实时检测是否正确, 支持 `v-model`, 调用方式: 
```html
<CaptchaInput v-model="captcha" captcha-image-url="/api/captcha" :captcha-checker="checkCaptcha" />
```
- VerticalLineSplitList.vue

竖线分割的列表显示组件, 支持 `v-model`, 调用方式: 
```html
<VerticalLineSplitList v-model="lang" :data="data" @item-change="itemChangeHandler" />
```
#### 其他说明
- 多个页面的设置, 可以在相应的文件夹(例如 router store)创建文件, 跟之前一个页面一个文件夹的方式不一样
