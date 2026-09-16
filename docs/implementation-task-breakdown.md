# Live2D 专注助手：实现任务拆分与验收合同

## 0. 总目标与交付背景

你正在参与搭建一个**招新面试项目基座**。项目交付后会先以完整、稳定、可运行的作品形式展示；只有完整版本验收后，维护者才会从真实功能中整理 Issue，供新生以 PR 的形式完成。当前阶段**不允许故意留 Bug、半成品或伪功能**。

产品是“Live2D 专注助手”，唯一核心流程为：

```text
输入一件要做的事 → 开始 25 分钟专注 → 倒计时结束 → 用户确认完成 → 角色庆祝并保存记录
```

后端必须以 Python 为主；Live2D 仅是完成反馈层，不能影响任务、计时、存档等核心流程。

正式应用位于当前仓库根目录。不得把缓存、虚拟环境、本地数据库或其他模型包提交进仓库。

## 1. 固定技术与角色资源

- Python：3.11+；Flask；SQLite；`pytest`。
- 前端：原生 HTML、CSS、JavaScript；不得引入 React、Vue、TypeScript、构建脚手架。
- Live2D 模型：固定使用 `static/models/shizuku/shizuku.model.json`。
- 选择理由：该模型具有 `idle`、`tap_body`、`pinch_in`、`pinch_out`、`shake`、`flick_head` 动作组，以及表情、物理、姿势、点击区域和配套音频；比仅有模型文件的资源更完整。
- 运行库必须是公开、文档齐全且兼容 Cubism 2 `.moc` 的浏览器端依赖。不得复制粘贴第三方完整项目源码；若使用依赖、示例或文档，必须在应用 README 的“参考与素材”中列链接、版本和自己的改动说明。

## 2. 所有执行者必须遵守的合同

每个执行者收到任务后，必须在最终回复中按以下格式交付：

```text
完成内容：
改动文件：
验证命令及结果：
未完成项：无 / 具体说明
参考资料与依赖：无 / 链接、版本、用途
```

通用约束：

- 只修改任务卡列出的“允许修改”文件；若确有必要新增文件，必须放在任务卡指定目录并说明原因。
- 不得删除、重写或格式化其他人的文件；不得使用 `git reset`、`git checkout --` 等破坏性命令。
- 不得加入 API Key、Token、账号信息、在线大模型调用、遥测、广告或远程数据收集。
- 不得为了通过验收而硬编码接口响应、跳过输入校验或吞掉异常。
- 代码必须有清晰英文命名、必要的中文注释；每个 Python 函数只负责一件事。
- 所有用户可见的文案使用中文；所有时间使用本地时区 ISO 8601 格式。
- 未安装的依赖必须写入 `requirements.txt`；禁止依赖全局环境“碰巧存在”的包。
- 先运行已有测试；本任务完成后运行本卡规定的验证。测试失败时不得宣称完成。

## 3. 执行顺序

任务必须按依赖顺序合并。T01–T04 是 Python 核心；T05–T07 是界面；T08–T09 是 Live2D 与整体验收。

| 任务 | 依赖 | 交付物 |
| --- | --- | --- |
| T01 | 无 | 可启动 Flask 骨架与依赖声明 |
| T02 | T01 | SQLite 连接、建表、仓储层 |
| T03 | T02 | 专注会话业务规则及单元测试 |
| T04 | T03 | REST API 及 API 测试 |
| T05 | T04 | 页面骨架与样式 |
| T06 | T04、T05 | 前端 API 客户端与计时状态机 |
| T07 | T06 | 历史记录渲染与无障碍/失败提示 |
| T08 | T07 | Shizuku 资源、Live2D 适配器与静态降级 |
| T09 | T04、T06、T07、T08 | 联调、README、完整验收 |

为了降低低成本模型修改同一文件时发生覆盖的风险，默认按 T01 → T09 串行合并。只有在使用独立 Git 分支并由维护者负责解决冲突时，才考虑并行。

## 4. 发给执行模型的统一开场提示

分配任务时，必须把下面这段提示与对应任务卡**一起发送**，不要只发任务编号：

```text
你正在实现“Live2D 专注助手”，这是数学建模协会技术组用于招新面试的完整项目基座。维护者会先完成并验收整个项目，后续再从真实功能中整理适合新生认领的 GitHub Issue。因此你本次必须提交可运行、可测试的完整实现，禁止故意留 Bug、TODO、空函数、假按钮、硬编码假数据或仅用于演示的伪实现。

产品唯一主流程是：输入一件事 → 开始 25 分钟专注 → 倒计时 → 用户确认完成 → Live2D 角色庆祝并保存记录。项目以 Python/Flask/SQLite 为核心，原生 HTML/CSS/JavaScript 提供页面；Live2D 只是反馈层，失效时核心流程仍必须可用。不得加入登录、AI 对话、云同步、积分商城等范围外功能。

请先阅读 docs/live2d-focus-assistant-architecture.md 和 docs/implementation-task-breakdown.md 中的通用合同，再只执行分配给你的任务卡。只修改任务卡允许的文件，保留其他人的改动；完成后实际运行验收命令，并按“完成内容、改动文件、验证命令及结果、未完成项、参考资料与依赖”格式回复。若前置依赖不存在或验收不通过，停止修改并准确报告，不得自行重构其他模块来绕过问题。
```

---

## T01：项目骨架与可启动 Flask 应用

**目的**：建立所有后续任务共用的、最小而明确的 Python 应用入口。

**允许修改**：

```text
app.py
requirements.txt
src/__init__.py
src/config.py
templates/.gitkeep
static/.gitkeep
tests/.gitkeep
.gitignore
```

**实现要求**：

- 实现 `create_app(test_config=None)` 应用工厂；测试配置能覆盖数据库路径。
- `GET /health` 返回 JSON：`{"status": "ok"}`，HTTP 200。
- 默认数据库路径为 `instance/focus.db`，`instance/` 不提交 Git。
- `requirements.txt` 至少固定 Flask 与 pytest 的兼容版本范围。
- 不能在导入 `app` 时自动启动服务；只允许 `python app.py` 启动开发服务器。

**验收命令**：

```powershell
cd live2d-focus-assistant
python -m pip install -r requirements.txt
python -c "from app import create_app; c=create_app({'TESTING': True, 'DATABASE': ':memory:'}).test_client(); r=c.get('/health'); assert r.status_code == 200 and r.get_json() == {'status': 'ok'}"
```

**完成标准**：命令退出码为 0；目录结构存在；没有业务逻辑、数据库逻辑或 Live2D 代码混入本任务。

---

## T02：SQLite 初始化与仓储层

**目的**：提供可测试的数据持久化，不让路由直接书写 SQL。

**依赖**：T01 已验收。

**允许修改**：

```text
src/db.py
src/repositories.py
src/schema.sql
app.py
tests/test_repositories.py
```

**实现要求**：

- `focus_sessions` 包含：`id`、`task_text`、`duration_seconds`、`remaining_seconds`、`started_at`、`last_started_at`、`finished_at`、`status`。
- `status` 仅允许 `active`、`paused`、`completed`、`abandoned`；数据库保证同一时刻最多一条 `active` 或 `paused` 记录（可使用部分唯一索引）。
- 所有 SQL 使用参数化查询；返回值统一为字典，不直接向上泄漏 SQLite Row。
- 仓储层仅处理存取，不计算时间、不判断业务状态是否合法。
- 应用启动/测试应用创建时可重复初始化数据库，且不会删除已有记录。

**验收标准**：

- `pytest -q tests/test_repositories.py` 全绿；
- 测试覆盖：创建记录、按 ID 查询、查询当前记录、更新记录、最近完成记录排序；
- 两条 `active/paused` 记录不能同时插入。

---

## T03：专注会话业务服务

**目的**：把任务校验、时间结算和状态流转写成纯 Python 业务规则，成为新生后续阅读的核心代码。

**依赖**：T02 已验收。

**允许修改**：

```text
src/services.py
src/errors.py
tests/test_services.py
```

**实现要求**：

- 提供 `create_session`、`pause_session`、`resume_session`、`complete_session`、`abandon_session`、`get_active_session`、`list_completed_sessions`。
- 任务文本必须 `strip()` 后为 1–80 个字符；固定时长 `1500` 秒。
- 服务接受可注入的 `now()`，测试中不得依赖真实等待。
- 暂停：以 `last_started_at` 结算 `remaining_seconds`，置为 `paused`；剩余时间不得小于 0。
- 恢复：仅允许暂停记录，写入新的 `last_started_at` 并置为 `active`。
- 完成：仅允许活动或暂停记录；写入 `finished_at` 和 `completed`。完成后不得重复完成。
- 当活动计时已归零，查询结果应提供 `timer_finished: true`；是否“确认完成”仍由用户动作决定。
- 用专门异常区分参数错误、资源不存在和状态冲突。

**验收标准**：

- `pytest -q tests/test_services.py` 全绿；
- 至少覆盖：空文本、超长文本、已有会话冲突、暂停结算、恢复、归零、不允许重复完成、不允许操作不存在记录；
- 测试中通过注入时间验证 1500 秒逻辑，不出现 `sleep()`。

---

## T04：REST API 与 API 测试

**目的**：把已验证的 Python 服务以稳定接口提供给网页端。

**依赖**：T03 已验收。

**允许修改**：

```text
src/routes.py
app.py
tests/test_api.py
```

**实现要求**：

- 实现以下接口：
  - `GET /api/sessions/active`
  - `POST /api/sessions`
  - `POST /api/sessions/<id>/pause`
  - `POST /api/sessions/<id>/resume`
  - `POST /api/sessions/<id>/complete`
  - `POST /api/sessions/<id>/abandon`
  - `GET /api/sessions?limit=10`
- JSON 请求必须验证 `Content-Type` 与字段类型；创建接口仅接受 `task_text`。
- 成功返回 JSON；参数错误为 400，不存在为 404，状态冲突为 409；错误格式固定为 `{"error": "..."}`。
- `limit` 默认 10，范围 1–50；非法值返回 400。
- 路由不含 SQL、计时计算或 Live2D 逻辑。

**验收标准**：

- `pytest -q tests/test_api.py` 全绿；
- 覆盖每条路由的成功路径；覆盖空请求、错误 Content-Type、非法 ID、重复创建与重复完成；
- `pytest -q` 全绿。

---

## T05：单页界面骨架与视觉状态容器

**目的**：先交付无需 Live2D 也可读、可操作的界面结构，保证角色层可独立替换。

**依赖**：T04 已验收。

**允许修改**：

```text
templates/index.html
static/css/app.css
app.py
```

**实现要求**：

- `GET /` 渲染页面；标题为“专注一下”。
- 页面包含：角色区域（含静态降级卡片）、状态文案、任务输入、开始按钮、倒计时、暂停/继续按钮、完成按钮、放弃按钮、最近完成记录列表。
- 所有交互控件有唯一 `id`；初始状态只显示输入和开始按钮，其他按钮可由 JS 管理。
- 不用内联 CSS、内联 JavaScript、外部字体或 CDN；移动端宽度 360px 时不横向溢出。
- 使用语义化标签和 `<label for>`；状态文案使用 `aria-live="polite"`。

**验收标准**：

- 浏览器打开 `/` 不报错，所有上述元素均存在；
- 禁用 JavaScript 后页面仍能读出项目目的和“角色加载失败时不影响专注流程”的提示；
- 不实现计时、API 调用和模型加载。

---

## T06：前端 API 客户端与计时状态机

**目的**：把页面与 Python API 接通，完成专注主流程；不得把业务逻辑复制到前端。

**依赖**：T04、T05 已验收。

**允许修改**：

```text
static/js/api.js
static/js/timer.js
static/js/app.js
templates/index.html
```

**实现要求**：

- `api.js` 是唯一使用 `fetch` 的文件；每个 API 请求均处理非 2xx 响应并转换为可读中文错误。
- `timer.js` 是唯一创建 `setInterval` 的文件；提供可测试的纯函数计算剩余秒数和格式化 `MM:SS`，不得出现多个并行计时器。
- 页面加载先查询活动记录；活动任务按 `last_started_at` 和 `remaining_seconds` 恢复，暂停任务不递减。
- 到 `00:00` 时停止计时、进入 `ready_to_complete`，显示“确认完成”；禁止显示负数或自动调用完成接口。
- 创建、暂停、恢复、完成、放弃均必须调用对应后端接口；页面只在接口成功后切换状态。
- 页面状态只能为 `idle`、`running`、`paused`、`ready_to_complete`、`completed`。

**验收标准**：

- 使用浏览器手工验证：创建 → 暂停 → 刷新 → 继续 → 到零 → 完成，状态正确；
- 同时检查开发者工具：不存在重复计时器、未处理 Promise rejection 或 4xx/5xx 静默失败；
- 任务为空时不发送创建请求；
- 不在本任务引入 Live2D 代码。

---

## T07：完成记录与前端错误可见性

**目的**：完成闭环中的“我确实做完了”的历史反馈，并让所有失败有出口。

**依赖**：T06 已验收。

**允许修改**：

```text
static/js/history.js
static/js/app.js
static/css/app.css
templates/index.html
```

**实现要求**：

- 页面初次加载和成功完成后调用完成记录接口，展示最近 10 条；
- 每条记录至少显示任务、完成时间和本次设定时长；禁止使用 `innerHTML` 直接拼接用户输入；
- 无完成记录时显示“还没有完成记录，开始第一件事吧”；
- API 或模型层失败时，在 `aria-live` 状态区域给出可读提示，不得只在控制台输出；
- 历史记录区域使用列表语义，窄屏自动换行。

**验收标准**：

- 完成一条任务后无需刷新即可出现在首位；刷新后仍存在；
- 包含 `<script>`、`<img>` 等字符的任务文本只能按纯文本显示；
- 人为断开 API 后，用户能看见中文错误提示，按钮不会卡死。

---

## T08：Shizuku Live2D 适配与静态降级

**目的**：让完成反馈“活起来”，同时将旧模型运行时风险隔离在一个前端模块内。

**依赖**：T07 已验收。

**允许修改**：

```text
static/js/live2d-adapter.js
static/js/app.js
static/models/shizuku/**
static/vendor/**
templates/index.html
static/css/app.css
```

**实现要求**：

- 从当前仓库的 Shizuku 包复制运行所需资源；模型配置中引用的 `.moc`、贴图、`physics`、`pose`、`exp`、`mtn` 与需要的声音文件路径必须完整保留或正确改写。
- `live2d-adapter.js` 对外只暴露 `init(container)` 和 `setState('idle' | 'focus' | 'celebrate')`；页面业务代码不得读取模型动作文件名。
- 在 `app.js` 中仅完成状态事件到 `setState` 的连接：页面初始化为 `idle`，开始/继续为 `focus`，确认完成为 `celebrate`，暂停/放弃回到 `idle`。
- 动作映射必须至少覆盖：`idle` 使用 `idle`；`focus` 可用 `idle` 或轻量非庆祝动作；`celebrate` 优先使用 `tap_body`、`shake` 或可用表情/动作。模型没有某动作时安全回退 `idle`。
- 初始化失败、网络资源 404 或运行库不兼容时，隐藏画布，显示静态角色卡片与“角色暂时休息中，专注记录不会受影响”；不得阻断任何按钮或计时逻辑。
- 第三方运行库不得从不固定的 CDN 动态加载；其版本、许可证与来源必须在 README 的“参考与素材”列出。
- 不得直接改动 `static/models/shizuku/` 里的模型二进制资源。

**验收标准**：

- 正常环境：页面能显示 Shizuku，开始专注和完成任务时存在肉眼可见的不同反馈；
- 将运行库路径临时改错后：页面无未捕获异常、静态降级卡片出现、T06 全流程仍可完成；
- 浏览器 Network 中模型配置引用资源无 404；
- 在最终回复中列出运行库精确版本、许可证和参考链接。

---

## T09：联调、文档与发布前验收

**目的**：把各模块收束成一个新人能下载、运行、理解和演示的完整项目基座。

**依赖**：T04、T06、T07、T08 已验收。

**允许修改**：

```text
README.md
requirements.txt
tests/**
.gitignore
```

若联调发现明确缺陷，只能在获得维护者确认后修改对应模块文件；必须在最终说明中写出原因和精确改动。

**实现要求**：

- README 必须包括：项目介绍、功能边界、Python 版本、安装命令、启动命令、测试命令、目录说明、一次完整使用流程、架构摘要、参考与素材、许可证注意事项。
- README 必须明确：项目不使用大模型或外部 API；用户数据默认保存在本机 SQLite；Live2D 不可用时核心流程仍可使用。
- 补充缺失但合理的集成测试；不为凑覆盖率添加无意义测试。
- `.gitignore` 覆盖数据库、虚拟环境、Python 缓存、测试缓存；不能忽略源代码、测试和 README。

**发布前验收清单**：

```powershell
cd live2d-focus-assistant
python -m pip install -r requirements.txt
pytest -q
python app.py
```

人工验收：

1. 打开首页，创建合法任务；
2. 暂停、刷新、恢复，确认时间正确；
3. 到零后确认完成，确认角色反馈与记录保存；
4. 刷新页面，确认历史还在；
5. 断开/禁用 Live2D 运行库，重复第 1–4 步，确认核心功能不受影响；
6. 读 README 后，在干净环境可复现运行。

全部通过才可标记为“项目完整版本完成”。
