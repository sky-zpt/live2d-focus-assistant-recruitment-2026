# Live2D 专注助手

一个只做一件事的专注网页：写下一项任务，自定义 1–120 分钟专注时长，倒计时结束后由用户确认完成；完成记录会保存到本地，Shizuku 角色会给予可见的完成反馈。

它是软件学院数学建模协会技术组的招新面试项目基座。考生以 GitHub Issue 为单位，在不改变核心专注体验的前提下完善指定的 Python 功能。

## 功能与边界

- 创建一项 1–80 字的专注任务，可设置 1–120 分钟专注时长（默认 25 分钟）；
- 暂停、刷新恢复、继续、完成或放弃当前任务；
- 保存并展示最近 10 条完成记录；
- 使用 Live2D Shizuku 角色表达空闲、专注和完成状态；
- 角色运行库、模型资源或 WebGL 不可用时，自动降级到静态角色卡片，专注主流程不受影响。

项目明确**不包含**登录、多用户、云同步、排行榜、积分商城、语音功能、AI 大模型或外部 API 调用。所有数据默认只保存在运行机器的 SQLite 文件中。

## 环境与安装

第一次配置 Python 的同学请阅读[零基础 Python 环境配置指南](docs/python-environment-guide.md)。准备认领 Issue 和提交 PR 的同学请先阅读[新生贡献指南](CONTRIBUTING.md)。

需要 Python 3.11 或更高版本。Windows 上推荐使用 Python Launcher：

```powershell
cd live2d-focus-assistant
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

本机若 `python --version` 低于 3.11，请使用 `py -3.11` 替代下文的 `python`。

## 启动与测试

```powershell
python app.py
```

浏览器打开 <http://127.0.0.1:5000>。

运行全部自动化测试：

```powershell
python -m pytest -q
```

## 使用流程

1. 在输入框写下一件要做的事，点击“开始专注”。
2. 专注期间可暂停；刷新页面后会从服务端记录恢复当前状态和剩余时间。
3. 倒计时到 `00:00` 后，点击“完成任务”确认完成；系统不会自动把任务标记为完成。
4. 页面显示角色庆祝反馈，并将记录写入“最近完成”。

## 项目结构

```text
repository-root/
├─ app.py                    # Flask 应用工厂、首页与健康检查
├─ src/
│  ├─ db.py                  # SQLite 生命周期与建表
│  ├─ repositories.py        # 仅负责数据存取
│  ├─ services.py            # Python 业务规则、时间结算、状态流转
│  ├─ analytics.py           # 专注记录统计入口
│  ├─ import_export.py       # 专注记录备份与恢复入口
│  ├─ cleanup_service.py     # 开放会话清理入口
│  ├─ cli.py                 # 本地命令行入口
│  ├─ routes.py              # REST API
│  └─ schema.sql             # 数据表和开放会话唯一索引
├─ static/
│  ├─ js/                    # API 客户端、计时器、记录与 Live2D 适配器
│  ├─ css/app.css            # 单页样式与降级显示
│  ├─ models/shizuku/        # Shizuku 模型资源
│  └─ vendor/live2d-widget/ # 固定版本的本地浏览器运行库
├─ templates/index.html
├─ tests/
└─ instance/focus.db         # 运行时创建；不会提交 Git
```

## 架构摘要

浏览器负责显示倒计时；Flask 在开始、暂停、恢复和完成这些状态变化点保存数据。SQLite 中只保存任务、剩余秒数和时间戳，因而刷新页面后可重新计算剩余时间。

`src/services.py` 是业务规则的唯一入口：负责任务校验、开放会话冲突、暂停结算和状态合法性。路由不直接写 SQL，仓储层不计算时间。`static/js/live2d-adapter.js` 将模型动作细节封装在单一模块中，页面主流程只调用 `init()` 和 `setState()`。

## 参考、素材与许可证

- Live2D 浏览器运行库：[`live2d-widget` 3.1.4](https://www.npmjs.com/package/live2d-widget)，来源项目 [xiazeyu/live2d-widget.js](https://github.com/xiazeyu/live2d-widget.js)，GPL-2.0。本项目固定保存所需的 `L2Dwidget.min.js` 与动态加载分包到 `static/vendor/live2d-widget/`，并由 `live2d-adapter.js` 负责本地模型路径、容器位置和失败降级处理。
- 模型素材：上游 [xiazeyu/live2d-widget-models](https://github.com/xiazeyu/live2d-widget-models) 的 Shizuku 包。项目只保留运行所需资源于 `static/models/shizuku/`，未修改二进制模型文件。
- 当前根仓库及上述运行库均涉及 GPL-2.0。若将本项目对外发布、二次分发或替换模型，必须先核对上游许可证、模型作者的单独授权要求，并按适用许可证履行义务。

### Shizuku 形象使用说明

本项目中的 Shizuku 仅作为非商业的学习、技术演示和社团招新项目素材使用。Shizuku 的角色形象、Live2D 模型、贴图、动作及音频并非本项目原创；本项目也不代表模型作者、Live2D Inc. 或相关权利方对本项目的认可或合作。

上游 `live2d-widget-model-shizuku` 包的元数据声明为 GPL-2.0，但软件包许可证不必然等同于角色形象的商用授权。由于上游仓库没有同时提供可核验的角色作者信息和独立商用条款，请勿据此将 Shizuku 用于商业宣传、付费产品、品牌代言或其他可能使人误认为官方授权的场景。公开部署、再分发或商业使用前，使用者应自行确认并取得模型、角色形象、音频以及 Live2D 运行技术所需的全部授权。

本项目对 Shizuku 模型文件本身未作修改，仅通过 `static/js/live2d-adapter.js` 调用其已有动作、表情和音频。若用于正式发布，建议替换为自制模型或授权范围明确的模型；替换时应将资源放入 `static/models/`，并同步修改适配器中的模型路径与动作映射，同时保留新素材要求的署名和许可证文件。

本项目没有接入大模型、第三方账号或远程数据服务；没有 API Key、Token 或用户数据上传逻辑。
