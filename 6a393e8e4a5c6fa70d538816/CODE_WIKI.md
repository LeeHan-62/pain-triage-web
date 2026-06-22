# 疼痛智能分诊微信小程序 — Code Wiki

> 面向社区门诊、全科诊室和预检分诊场景的微信小程序原型。患者可自助填写疼痛信息，系统自动生成结构化摘要、疼痛部位/性质分类、风险分级与分诊推荐，并将结果保存在本地模拟档案中，同时提供后台统计视图。

---

## 1. 项目概览

### 1.1 项目定位
- **产品名称**：疼痛智能问诊与分诊小程序（原型）
- **目标用户**：社区门诊护士 / 全科医师 / 就诊患者
- **核心价值**：降低预检分诊人力成本；为胸痛、急腹症等高风险症状提供早期预警；为全科门诊形成结构化疼痛诊疗数据。
- **技术栈**：微信原生小程序（WXML / WXSS / JavaScript / CommonJS）
- **数据存储**：`wx.setStorageSync` / `wx.getStorageSync`（本地缓存，原型阶段）
- **AI 能力占位**：`utils/triage.js` 以本地规则模拟 FastChat（多轮问诊与字段抽取）和 MONAI（多任务分类与风险分级）输出。

### 1.2 已实现功能清单
| 模块 | 功能 | 说明 |
| --- | --- | --- |
| 患者自助问诊 | 位置、性质、时长、诱因、伴随症状采集 | 支持 picker 选择 + 自由文本 + 语音识别示例占位 |
| AI 分类占位 | 疼痛部位 / 性质 / 风险等级自动输出 | 基于关键词规则在本地模拟 AI 模型 |
| 风险分级 | Ⅰ/Ⅱ/Ⅲ/Ⅳ 四级分级 | 匹配急诊抢救 / 优先诊室 / 专科队列 / 常规随访 |
| 分诊结果页 | 风险卡片、分类网格、结构化摘要、标签 | `pages/result` 展示 triage 输出 |
| 健康档案 | 历史问诊记录列表 | 保存到 `wx.setStorageSync('painRecords', [...])` |
| 后台统计 | 累计记录、高危筛查、等级/部位/性质分布 | 前端聚合生成简易条形占比视图 |

### 1.3 运行环境要求
- 微信开发者工具 ≥ 1.06
- 小程序基础库版本 ≥ `3.7.0`（见 [project.config.json](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/project.config.json#L12)）
- AppID：默认使用测试号 `touristappid`，正式发布需替换为你自己的小程序 AppID

---

## 2. 目录结构与职责

```
project-root/
├── app.js                 # 小程序入口：初始化全局数据、首次启动时初始化 painRecords
├── app.json               # 全局配置：注册页面、窗口样式、TabBar、sitemap
├── app.wxss               # 全局样式：卡片、标题、按钮、标签等基础类
├── sitemap.json           # 微信搜索收录规则（默认全部 allow）
├── project.config.json    # 开发者工具项目配置（编译类型、基础库、AppID）
├── README.md              # 项目说明文档
├── utils/
│   └── triage.js          # 疼痛分类与风险分级核心逻辑（本地规则）
└── pages/
    ├── home/              # 系统首页（流程说明 + 风险等级图例 + 进入问诊入口）
    ├── consult/           # 患者自助疼痛问诊表单
    ├── result/            # AI 分诊结果展示
    ├── records/           # 疼痛健康档案（OpenEMR 联动模拟）
    └── stats/             # 后台统计（等级 / 部位 / 性质分布）
```

每个页面目录遵循微信小程序标准结构，由 4 个同名文件构成：
- `*.js`：页面逻辑（数据、事件、生命周期）
- `*.wxml`：页面结构（组件标签 + 数据绑定）
- `*.wxss`：页面样式（卡片、排版、交互元素）
- `*.json`：页面配置（导航标题等）

---

## 3. 架构设计

### 3.1 总体流程

```
用户进入首页
    │
    ▼
[pages/home] → 点击「开始疼痛问诊」 → wx.navigateTo 跳转到 consult
    │
    ▼
[pages/consult] 采集以下字段并提交：
    patientName / location / nature / duration
    factor / symptoms(多选) / description（文字或语音示例）
    │
    ▼ 调用 utils/triage.triage(form)
    │
    ▼
[utils/triage] 执行：
    inferPart()       → 疼痛部位分类（模拟 MONAI）
    inferNature()     → 疼痛性质分类（模拟 MONAI）
    classifyRisk()    → 风险等级（Ⅰ-Ⅳ级，模拟 MONAI）
    buildSummary()    → 结构化摘要（模拟 FastChat 文本整理）
    │
    ▼
{ result 对象 }
    │
    ├── 写入 wx.setStorageSync('latestTriageResult', result)  → 供 result 页读取
    └── 追加到 wx.setStorageSync('painRecords', [result, ...]) → 供 records/stats 读取
    │
    ▼
[pages/result] 展示：
    风险卡片（按 risk.color 着色）
    分类网格（part / nature / department）
    结构化 summary 文本
    医生端标签
    │
    ▼
用户可跳转到 records 查看档案，或到 stats 查看统计聚合
```

### 3.2 分层划分

| 层 | 对应文件 | 职责 |
| --- | --- | --- |
| 视图层（View） | `pages/*/wxml` + `pages/*/wxss` | 渲染 UI，响应式卡片布局，风险等级色彩系统 |
| 交互层（Controller） | `pages/*/js` | 页面 data、事件处理、表单校验、页面跳转、存储读写 |
| 业务逻辑层（Service） | `utils/triage.js` | 分诊算法、风险分级、摘要生成 |
| 数据层（Storage） | `wx.setStorageSync` | 本地 KV 存储 `painRecords` 与 `latestTriageResult` |
| 全局配置 | `app.js` / `app.json` / `app.wxss` | 注册页面、TabBar、全局样式、启动初始化 |

### 3.3 数据流设计
- **关键存储 key**：
  - `painRecords`：数组，保存全部历史问诊记录（最新在前）
  - `latestTriageResult`：单个对象，保存最近一次问诊结果（供 `result` 页读取展示）
- **写入时机**：在 [pages/consult/consult.js](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/consult/consult.js#L52-L71) 的 `submit()` 完成
- **读取时机**：
  - `result.onLoad()` 读取 `latestTriageResult`
  - `records.onShow()` 读取 `painRecords`
  - `stats.onShow()` 读取 `painRecords` 并聚合统计

---

## 4. 全局入口与配置

### 4.1 [app.js](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/app.js#L1-L12)

```js
App({
  globalData: {
    appName: '疼痛智能分诊小程序'
  },
  onLaunch() {
    const records = wx.getStorageSync('painRecords')
    if (!records) {
      wx.setStorageSync('painRecords', [])
    }
  }
})
```

**核心说明**：
- `globalData.appName`：全局应用名称，便于后续在页面中统一引用。
- `onLaunch()`：小程序冷启动时执行一次，负责检查 `painRecords` 是否存在；若不存在则初始化为空数组，避免后续页面读取到 `undefined`。

### 4.2 [app.json](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/app.json#L1-L37)

- `pages`：按顺序注册 5 个页面，首项为启动页 `pages/home/home`
- `window`：导航栏蓝色主题 `#1f6feb`，背景色 `#f4f7fb`
- `tabBar`：底部 Tab 包含三个入口
  - 问诊 → `pages/home/home`
  - 档案 → `pages/records/records`
  - 统计 → `pages/stats/stats`
- `sitemapLocation`：指向 [sitemap.json](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/sitemap.json)

### 4.3 [app.wxss](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/app.wxss#L1-L67)

定义了全局视觉规范，各页面复用以下基础类：
| 类名 | 用途 |
| --- | --- |
| `.page` | 页面容器，内边距 32rpx |
| `.card` | 白色圆角卡片，带柔和蓝色阴影 |
| `.title` / `.subtitle` / `.section-title` | 排版层级 |
| `.primary-btn` | 主按钮（蓝底白字，胶囊） |
| `.ghost-btn` | 次按钮（淡蓝底蓝字，胶囊） |
| `.tag` | 医生端标签样式 |
| `.muted` | 次级文字灰阶色 |

---

## 5. 核心业务模块：`utils/triage.js`

文件路径：[utils/triage.js](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/utils/triage.js#L1-L117)

### 5.1 对外暴露

```js
module.exports = {
  triage
}
```

### 5.2 数据结构

**输入 `form`（问诊表单）**：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `patientName` | string | 患者姓名（可为空） |
| `location` | string | 疼痛位置（picker 选中项） |
| `nature` | string | 疼痛性质（picker 选中项） |
| `duration` | string | 持续时间（突发几小时 / 持续数日 / 慢性反复发作） |
| `factor` | string | 诱发或缓解因素 |
| `symptoms` | string[] | 伴随症状（复选框多选） |
| `description` | string | 自由文本描述（语音转文字示例） |

**输出 `result`（分诊结果）**：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | number | `Date.now()`，用于列表 wx:key |
| `createdAt` | string | `new Date().toLocaleString()` |
| `patientName` | string | 患者姓名 |
| `part` | string | 疼痛部位（如「胸痛」「下腹痛」） |
| `nature` | string | 疼痛性质（如「撕裂痛」「钝痛」） |
| `risk` | object | 风险对象 `{ level, label, color, action, queue }` |
| `department` | string | 推荐分诊去向（= `risk.queue`） |
| `summary` | string | 中文结构化摘要 |
| `raw` | object | 原始表单副本，便于后续追溯 |

### 5.3 关键函数说明

#### `inferPart(form) → string`
- 位置：[utils/triage.js#L27-L31](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/utils/triage.js#L27-L31)
- 职责：根据 `location + description` 命中 `locationMap` 关键词，推断疼痛部位分类（模拟 MONAI 部位分类输出）。
- 兜底：未命中时返回「全身多发痛」。

#### `inferNature(form) → string`
- 位置：[utils/triage.js#L33-L38](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/utils/triage.js#L33-L38)
- 职责：若用户已显式选择 `nature` 则直接返回；否则从 `description` 中匹配性质关键词（如「撕裂」「绞痛」）。
- 兜底：未匹配时默认「钝痛」。

#### `hasAny(form, words) → boolean`
- 位置：[utils/triage.js#L40-L43](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/utils/triage.js#L40-L43)
- 职责：在 `description + symptoms + factor + duration` 的拼接文本中检查是否存在任一关键词，辅助风险分级。

#### `classifyRisk(part, nature, form) → object`
- 位置：[utils/triage.js#L45-L91](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/utils/triage.js#L45-L91)
- 职责：按优先级输出四级风险结果之一。

| 优先级 | 典型触发条件 | 输出等级 | 颜色 | 推荐去向 |
| --- | --- | --- | --- | --- |
| 1（最高） | 胸痛+撕裂/压榨/大汗/胸闷；腹痛+刀割/剧烈/呕血；腰背痛+突发/剧烈/撕裂 | Ⅰ级（极高危） | `#d93025` 红 | 急诊抢救区 |
| 2 | 头痛+持续/剧烈/呕吐；腹痛+压痛/发热；下肢肿痛 | Ⅱ级（高危） | `#f97316` 橙 | 优先诊室（10 分钟内） |
| 3 | 含「急性 / 扭伤 / 新发 / 一过性」关键词 | Ⅲ级（普通急症） | `#2563eb` 蓝 | 当日专科优先队列 |
| 4（兜底） | 其它情况 | Ⅳ级（慢性慢病） | `#16a34a` 绿 | 常规排队 + 慢病随访 |

> 注意：函数通过**自上而下**的 `if-return` 结构实现优先级匹配，新增规则时请保持高风险前置。

#### `buildSummary(form, part, nature, risk) → string`
- 位置：[utils/triage.js#L93-L96](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/utils/triage.js#L93-L96)
- 职责：将问诊要点模板化成结构化中文摘要，供医生端快速浏览。

#### `triage(form) → result`
- 位置：[utils/triage.js#L98-L113](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/utils/triage.js#L98-L113)
- 职责：整个模块的对外主函数，串联部位推断 → 性质推断 → 风险分级 → 摘要构建 → 生成最终结果对象。

### 5.4 关键字典（映射表）

- `locationMap`：[utils/triage.js#L1-L12](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/utils/triage.js#L1-L12) — 将部位关键词（头、颈肩、胸、上腹、下腹、腰背、关节、肌肉、会阴、全身）映射为分类标签。
- `departmentMap`：[utils/triage.js#L14-L25](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/utils/triage.js#L14-L25) — 将分类标签映射到推荐科室（神经内科、骨科、急诊、消化内科、泌尿外科、妇科、全科等）。

---

## 6. 页面模块详解

### 6.1 首页 [pages/home](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/home)

| 文件 | 作用 |
| --- | --- |
| [home.js](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/home/home.js) | 仅实现 `startConsult()`：调用 `wx.navigateTo` 跳转到 consult 页 |
| [home.wxml](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/home/home.wxml) | 渐变色 Hero 卡片 + 核心流程列表 + 四级风险等级图例 |
| [home.wxss](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/home/home.wxss) | Hero 渐变、流程条目分隔线、风险色点（red/orange/blue/green） |
| [home.json](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/home/home.json) | 设置 `navigationBarTitleText: "疼痛智能分诊"` |

### 6.2 问诊页 [pages/consult](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/consult)

**文件关系与职责**：

- [consult.js](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/consult/consult.js)：
  - 顶部 `const { triage } = require('../../utils/triage')` 引入分诊算法。
  - `data` 中维护 5 个 picker 候选列表（locations / natures / durations / factors / symptoms）与表单对象 `form`。
  - `onInput(e)`：文本输入类字段的统一处理，通过 `data-field` 动态绑定到 `form.${field}`。
  - `onPickerChange(e)`：picker 选择项的统一处理，通过 `data-list` 从候选数组中取值。
  - `onSymptomsChange(e)`：伴随症状复选框值处理，直接赋值到 `form.symptoms`。
  - `useVoiceMock()`：语音识别示例占位，将一段典型的胸痛主诉预填入 `description`，并使用 `wx.showToast` 反馈。
  - `submit()`：
    1. 校验：必须填写 `location` 或 `description` 之一，否则提示用户。
    2. 调用 `triage(this.data.form)` 得到 `result`。
    3. 写入 `latestTriageResult`（供 result 页读取）。
    4. 追加到 `painRecords`（供档案与统计读取）。
    5. `wx.navigateTo` 跳转到 result 页。

- [consult.wxml](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/consult/consult.wxml)：
  - 四个独立卡片分组：基本信息、AI 引导式问诊、伴随症状、语音/文字描述。
  - 使用 `<picker mode="selector">`、`<checkbox-group>`、`<textarea>` 组件。
  - 底部「提交并生成分诊结果」按钮触发 `submit`。

- [consult.wxss](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/consult/consult.wxss)：
  - `.input / .picker / .textarea` 共用统一的浅灰蓝边框与圆角样式。
  - `.field / .label / .check-item` 控制表单标签与复选框布局。

### 6.3 结果页 [pages/result](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/result)

- [result.js](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/result/result.js)：
  - `onLoad()` 从 `wx.getStorageSync('latestTriageResult')` 读取最新结果。
  - `backHome()` / `goRecords()` 分别使用 `wx.switchTab` 返回首页或进入档案页（均为 TabBar 页面）。

- [result.wxml](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/result/result.wxml)：
  - 风险卡片：左侧彩条使用 `result.risk.color` 动态着色。
  - 分类网格：展示 `part / nature / department` 三项。
  - 结构化摘要：展示 `result.summary`。
  - 医生端标签：以 `.tag` 展示 `part / nature / risk.level / department`。
  - `wx:else` 分支处理「暂无结果」的空状态。

- [result.wxss](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/result/result.wxss)：
  - `.risk-card` 12rpx 左侧彩条；`.risk-level` 加粗大字号；`.result-grid` 单列网格布局。

### 6.4 档案页 [pages/records](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/records)

- [records.js](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/records/records.js)：
  - `onShow()` 每次显示 Tab 时从 `wx.getStorageSync('painRecords')` 读取，保证统计与档案的实时性。
  - `clearRecords()`：使用 `wx.showModal` 二次确认后清空本地模拟档案。

- [records.wxml](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/records/records.wxml)：
  - 顶部卡片说明：当前为 OpenEMR 联动模拟；正式部署可改为接口写入。
  - 列表项以卡片呈现：患者姓名 + 时间、风险等级（带颜色）、结构化摘要、标签组。
  - 若 `records.length === 0` 显示「暂无档案记录」空状态。

### 6.5 统计页 [pages/stats](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/stats)

- [stats.js](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/stats/stats.js)：
  - `countBy(records, getter)`：通用计数聚合工具，使用 `reduce` 生成 `{ key: count }` 映射。
  - `toList(map)`：将计数映射转为 `[{ name, count }]` 列表，便于 WXML 循环渲染。
  - `onShow()`：
    1. 读取 `painRecords`
    2. 分别统计 `risk.level + risk.label`、`part`、`nature` 三维分布
    3. 额外过滤出 Ⅰ级 与 Ⅱ级 患者数量为 `highRiskCount`
    4. 通过 `setData` 注入视图

- [stats.wxml](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/stats/stats.wxml)：
  - 深色顶部卡片展示累计问诊记录数字。
  - 三个分布小节（风险等级 / 部位占比 / 性质分布），均使用三列 grid 形式的条带：`label | 进度条 | 数量`。
  - 进度条宽度：`item.count * 100 / total`，由 WXML 内联 style 动态计算。

- [stats.wxss](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/stats/stats.wxss)：
  - `.bar-row`：`150rpx | 1fr | 48rpx` 的三列栅格。
  - `.bar-fill / .part / .nature`：三维分布分别用蓝 / 绿 / 橙色区分。

---

## 7. 依赖关系图

```
                  ┌──────────┐
                  │ app.json │  注册全部页面 + TabBar + sitemap
                  └────┬─────┘
                       │ 配置驱动
                       ▼
           ┌─────────────────────────┐
           │ app.js (App 全局入口)    │
           │ onLaunch → 初始化 painRecords │
           └──┬──────────┬───────────┘
              │ 全局样式  │ 全局实例
              ▼           ▼
        [app.wxss]   [wx.* 存储 API]
                         │
 ┌───────────────────────┼────────────────────────┐
 │  pages/home            │                        │
 │  pages/consult  ──────┼── require → utils/triage
 │  pages/result   ←─────┘                        │
 │  pages/records  ──────┐                        │
 │  pages/stats    ←─────┘                        │
 └─────────────────────────────────────────────────┘
                         │
                         ▼
                  [本地缓存]
                  - latestTriageResult (单次结果)
                  - painRecords (历史列表)
```

### 7.1 模块间耦合要点

| 依赖 | 耦合方式 |
| --- | --- |
| `pages/consult` → `utils/triage` | `require('../../utils/triage')` 导入 `triage` 函数 |
| `pages/consult` → `pages/result` | `wx.navigateTo`，数据通过 `wx.setStorageSync('latestTriageResult', …)` 传递 |
| `pages/result/records/stats` → 存储 | 所有下游页面均通过 `wx.getStorageSync` 读取数据 |
| `app.js` → 存储 | 首次启动初始化 `painRecords` 默认值 `[]` |

---

## 8. 关键数据契约与流程接口

### 8.1 表单 → 分诊：`triage(form)`

- **输入校验**：由 `consult.submit()` 保证 `location` 或 `description` 至少一项非空。
- **输出保证**：`result.risk` 始终返回完整对象（不会为 `undefined` 或 `null`），因此 `result.wxml` 可直接使用 `result.risk.color` 等字段。

### 8.2 写入存储的契约

```js
// consult.submit() 中写入
wx.setStorageSync('latestTriageResult', result)     // 单个对象
wx.setStorageSync('painRecords', [result, ...old])   // 数组，unshift 新增

// result/records/stats 中读取
wx.getStorageSync('latestTriageResult')  // 可能为 undefined（从未问诊）
wx.getStorageSync('painRecords') || []   // 一定是数组
```

### 8.3 页面跳转接口

| 源页面 | 目标页面 | API | 理由 |
| --- | --- | --- | --- |
| `home` | `consult` | `wx.navigateTo` | consult 非 TabBar，且需要返回首页 |
| `consult` | `result` | `wx.navigateTo` | result 非 TabBar，可返回继续编辑 |
| `result` | `home` / `records` | `wx.switchTab` | 目标均为 TabBar 页面 |
| Tab 切换（home/records/stats） | — | 框架自动 `onShow` | 每次进入 Tab 触发数据刷新 |

---

## 9. 样式与视觉规范

### 9.1 色彩系统
| 用途 | 色值 | 出现位置 |
| --- | --- | --- |
| 品牌主色 | `#1f6feb` | 导航栏、主按钮、标准进度条、复选框 |
| 次蓝（ghost / tag 背景） | `#eef5ff` | ghost 按钮、标签背景 |
| 高风险红 | `#d93025` | Ⅰ级 风险 |
| 高风险橙 | `#f97316` | Ⅱ级 风险、性质分布进度条 |
| 低风险蓝 | `#2563eb` | Ⅲ级 风险 |
| 低风险绿 | `#16a34a` | Ⅳ级 风险、部位分布进度条 |
| 文本主色 | `#17233d` | 主要文本 |
| 文本灰阶 | `#334155 / #64748b` | 次级与占位文本 |
| 卡片背景 | `#ffffff` | 各 `.card` |
| 页面背景 | `#f4f7fb` | 全局页面底色 |

### 9.2 响应式单位
- 全部尺寸使用 `rpx`（750rpx = 屏幕宽度），保证在不同机型上按比例自适应。
- 字体大小范围 `24rpx`（标签备注）— `72rpx`（统计大数）。

### 9.3 布局模式
- 卡片式纵向堆叠（每个 `.card` 为独立模块）
- `grid-template-columns` 用于分类与统计条带的三列布局
- `display: flex` 用于首页 hero 与 风险条目的简单对齐

---

## 10. 项目运行与开发指南

### 10.1 运行步骤
1. 下载并安装 **微信开发者工具**。
2. 选择「导入项目」→ 项目目录选择当前仓库根目录。
3. AppID 选择「测试号」，或填写你自己的小程序 AppID（修改 [project.config.json](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/project.config.json#L13) 的 `appid` 字段）。
4. 基础库版本 ≥ 3.7.0（在工具右上角「详情 → 本地设置 → 调试基础库」中确认）。
5. 编译运行，点击首页「开始疼痛问诊」→ 填写或使用「填入语音识别示例」→ 提交，即可看到完整流程。

### 10.2 本地数据清理
- 「档案」Tab 内提供「清空本地模拟档案」按钮，使用 `wx.showModal` 二次确认。
- 或在微信开发者工具 → 调试器 → Storage 面板手动清除 `painRecords` / `latestTriageResult`。

### 10.3 常见开发改动点
- **新增风险规则**：编辑 `utils/triage.js` 的 `classifyRisk()`，在合适优先级添加新的 `if-return` 分支。
- **新增疼痛部位**：同时更新 `locationMap`（问诊关键词命中）和 `departmentMap`（分诊去向）。
- **调整 UI 风格**：修改 `app.wxss` 中的 `.card / .primary-btn / .tag` 等基础类即可全站统一。
- **接入真实语音**：替换 `useVoiceMock()` 的实现，调用微信 `wx.getRecorderManager` 或后端 ASR 接口。

---

## 11. 后续接入与升级建议

当前原型使用本地存储 + 规则引擎完成所有功能。迁移到生产环境时，建议按以下路径演进：

| 方向 | 说明 | 改造重点 |
| --- | --- | --- |
| **FastChat 接入** | 负责多轮问诊引导、语音文本整理、结构化字段抽取 | 将 `consult.js` 的自由文本与 picker 选择改为与后端对话接口交互，最终由后端生成统一 `form` |
| **MONAI 接入** | 负责多任务分类：部位、性质、风险等级 | 替换 `utils/triage.js` 中的本地规则为 `wx.request` 调用 MONAI 服务；保留 `triage(form)` 签名，内部改为异步实现（async/await 或 Promise） |
| **OpenEMR 接入** | 将结果写入患者健康档案，并支持慢病随访提醒 | 在 `consult.submit()` 写入本地同时，调用 OpenEMR 接口；失败时可采用「离线排队 + 网络恢复回传」策略 |
| **服务端统计** | 门诊大数据量统计由后端按月聚合，前端仅负责展示 | 将 `stats.js` 的 `countBy/toList` 改为后端接口返回 `total / riskList / partList / natureList / highRiskCount` 结构 |
| **权限与安全** | 正式小程序需配置合法域名、登录态与患者身份核验 | 加入 `wx.login` + 业务后端登录态，避免明文存储敏感信息 |

---

## 12. 文件索引（快速定位）

| 类别 | 关键文件 |
| --- | --- |
| 入口与配置 | [app.js](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/app.js) · [app.json](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/app.json) · [app.wxss](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/app.wxss) · [project.config.json](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/project.config.json) |
| 核心算法 | [utils/triage.js](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/utils/triage.js) |
| 首页 | [home.js](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/home/home.js) · [home.wxml](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/home/home.wxml) |
| 问诊页 | [consult.js](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/consult/consult.js) · [consult.wxml](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/consult/consult.wxml) |
| 结果页 | [result.js](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/result/result.js) · [result.wxml](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/result/result.wxml) |
| 档案页 | [records.js](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/records/records.js) · [records.wxml](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/records/records.wxml) |
| 统计页 | [stats.js](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/stats/stats.js) · [stats.wxml](file:///C:/Users/%E5%8D%8E%E4%B8%BA/AppData/Roaming/TRAE%20SOLO%20CN/ModularData/ai-agent/work-mode-projects/6a393e8e4a5c6fa70d538816/pages/stats/stats.wxml) |

---

*本 Code Wiki 基于当前仓库的完整代码阅读生成，可随项目演进持续维护更新。*
