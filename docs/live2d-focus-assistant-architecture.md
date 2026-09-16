# Live2D 专注助手：设计架构文档

## 1. 项目定位

这是一个单任务、单轮专注的网页助手：用户写下一件现在要完成的事，自定义 1–120 分钟专注时长（默认 25 分钟）；结束后主动确认完成，角色用 Live2D 动作和文案给予反馈，同时保存本次记录。

核心闭环只有一条：

```text
输入任务 → 开始专注 → 倒计时 → 确认完成 → 角色庆祝 + 保存记录
```

项目的价值在于让用户获得即时、可见的完成反馈。Live2D 是反馈层，不承担任务、计时和存档等核心逻辑；即使角色资源加载失败，专注流程也必须可用。

## 2. 完整版范围

### 必做功能

- 输入一条非空任务，创建本次专注记录；
- 默认 25 分钟倒计时，可自定义 1–120 分钟，并支持暂停与继续；
- 倒计时结束后显示“可以确认完成”，不自动记为完成；
- 用户点击“完成任务”后，保存完成时间与时长；
- 页面展示最近的完成记录；刷新页面后记录仍存在；
- Live2D 角色具有 `idle`（空闲）、`focus`（专注）、`celebrate`（完成）三种可感知状态；
- 模型加载失败时显示静态占位角色与相同的反馈文案。

### 明确不做

- 登录、多用户、排行榜、等级/金币/商城；
- AI 大模型聊天、语音识别、云端同步；
- 多任务并行、番茄钟复杂配置、任务分类和数据报表；
- 为招新刻意植入缺陷或拆分 Issue（完整版本验收后再进行）。

## 3. 技术选型

| 层级 | 方案 | 作用 |
| --- | --- | --- |
| 后端 | Python 3.11+、Flask | 提供任务记录 API、参数校验和 SQLite 持久化 |
| 数据库 | SQLite | 本地单用户记录，零额外部署依赖 |
| 前端 | 原生 HTML、CSS、JavaScript | 交互、倒计时、页面状态渲染 |
| 角色渲染 | 与 Cubism 2 `.moc` 兼容的浏览器运行库 | 读取本仓库已有模型资源并播放动作 |
| 测试 | `pytest`、Flask test client | 覆盖后端规则与 API |

选择 Flask 和原生前端是为了让代码结构直观：新生能分别读懂 Python 数据流、浏览器状态和接口调用，不引入 React/Vue 等额外学习负担。

## 4. 总体架构

```text
浏览器
├─ 页面交互与倒计时（JavaScript）
├─ Live2D 适配器（动作、降级显示）
└─ REST 请求
       │
       ▼
Flask 应用
├─ 路由 / 参数校验
├─ 专注记录服务（业务规则）
└─ SQLite 仓储层
       │
       ▼
focus.db
```

前端负责“每秒显示剩余时间”，后端不保存每一秒的变化。后端在开始与暂停等状态切换点保存剩余秒数和最后一次开始时间；刷新页面时，前端据此恢复时钟。这样既能支持暂停，也不会因浏览器计时漂移而失真。

## 5. 数据模型

表：`focus_sessions`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | INTEGER | 主键 |
| `task_text` | TEXT | 去除首尾空格后的任务，1–80 个字符 |
| `duration_seconds` | INTEGER | 用户设置的时长，默认 `1500` 秒，范围 60–7200 秒 |
| `remaining_seconds` | INTEGER | 最近一次暂停时或创建时的剩余秒数 |
| `started_at` | TEXT | ISO 8601 开始时间 |
| `last_started_at` | TEXT / NULL | 当前一段计时的开始时间；暂停后为空 |
| `finished_at` | TEXT / NULL | 用户确认完成的时间 |
| `status` | TEXT | `active`、`paused`、`completed`、`abandoned` |

约束：同一时刻最多一条 `active` 或 `paused` 记录；暂停时后端以 `last_started_at` 计算并写入 `remaining_seconds`；恢复时将 `last_started_at` 更新为当前时间；已完成记录不能再次完成或修改。

## 6. API 约定

| 方法与路径 | 请求 / 响应 | 行为 |
| --- | --- | --- |
| `GET /api/sessions/active` | 返回当前活动记录或 `null` | 页面初始化时恢复状态 |
| `POST /api/sessions` | `{ "task_text": "复习列表", "duration_minutes": 25 }` | 创建并开始一轮专注 |
| `POST /api/sessions/{id}/pause` | 无需请求体 | 结算当前剩余时长并暂停 |
| `POST /api/sessions/{id}/resume` | 无需请求体 | 继续已暂停的专注 |
| `POST /api/sessions/{id}/complete` | 无需请求体 | 标记完成并返回完成记录 |
| `POST /api/sessions/{id}/abandon` | 无需请求体 | 主动放弃当前轮次 |
| `GET /api/sessions?limit=10` | 返回最近完成记录 | 渲染历史列表 |

错误统一返回 `{ "error": "可读的错误说明" }`；输入错误返回 400，不存在返回 404，状态冲突（如已有进行中的任务）返回 409。

## 7. 前端状态与角色反馈

页面状态只维护以下五种：

| 页面状态 | 用户操作 | UI | 角色反馈 |
| --- | --- | --- | --- |
| `idle` | 输入任务、开始 | 显示输入框与开始按钮 | `idle` 动作 |
| `running` | 暂停 | 倒计时递减 | `focus` 动作或专注文案 |
| `paused` | 继续、放弃 | 倒计时静止 | `idle` 动作 |
| `ready_to_complete` | 确认完成 | 显示完成按钮 | 鼓励文案 |
| `completed` | 开始下一件事 | 显示完成提示与记录 | `celebrate` 动作 |

`Live2DAdapter` 是唯一接触模型运行库的前端模块，对外只暴露 `setState(state)`。业务代码不能直接引用动作文件名。适配器内部为每种状态设置可用动作映射；目标模型缺少某动作时回退到 `idle`，加载失败则展示静态角色卡片。

## 8. 推荐目录

```text
repository-root/
├─ app.py
├─ requirements.txt
├─ instance/                # 本地 SQLite 数据库，不提交 Git
├─ src/
│  ├─ db.py
│  ├─ repositories.py
│  ├─ services.py
│  ├─ analytics.py
│  ├─ import_export.py
│  ├─ cleanup_service.py
│  ├─ cli.py
│  └─ routes.py
├─ static/
│  ├─ css/app.css
│  ├─ js/app.js
│  ├─ js/timer.js
│  ├─ js/live2d-adapter.js
│  └─ models/               # 经授权后选定的一套模型资源
├─ templates/index.html
├─ tests/
│  ├─ test_services.py
│  └─ test_api.py
└─ README.md
```

当前仓库已经是独立应用仓库，只保留 Shizuku 的运行时资源，不再包含上游模型集合与旧 npm 元数据。

## 9. 完整版验收标准

- 新用户可在 3 个操作内开始一轮 25 分钟专注；
- 空白、纯空格或超过 80 字的任务不能创建；
- 活动任务刷新页面后能恢复正确的剩余时间；
- 暂停时剩余时间不减少，继续后正常递减；
- 到零后只能确认完成或放弃，不出现负数；
- 完成后记录持久化，刷新后仍能看到，且不能重复完成；
- Live2D 正常时能在开始和完成两个节点产生可见反馈；资源加载失败时核心流程无阻断；
- API 规则、状态冲突和输入校验具有自动化测试；
- README 包含安装、运行、结构、演示与素材/参考来源说明。

## 10. 后续招新 Issue 的拆分原则

在完整版本稳定后，再从真实功能中拆分独立、可验证、互不阻塞的改进任务。每个 Issue 必须写明：复现或预期行为、相关文件范围、验收方式和推荐知识点；不通过隐藏致命错误来制造任务，也不让新人修改难以理解的二进制模型文件。
