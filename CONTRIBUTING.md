# 新生贡献指南

欢迎参与 Live2D 专注助手项目。本次招新有两条互斥的提交路线：认领一个 GitHub Issue，或在 `contrib/` 中完成一个独立的 Python 小项目。完成后都通过 Pull Request（简称 PR）提交代码。

我们不要求你入门时就熟悉完整的工程流程，也不要求你运行自动化测试。我们更关注你能否读懂任务、主动查资料、完成一个真实功能，并清楚说明自己的思路。

## 1. 开始之前

请先完成以下准备：

1. 注册并登录 GitHub。
2. 在“Issue 认领”和“Free-play 自由发挥”中选择一条路线；一份 PR 只对应其中一种路线。
3. 按照 [Python 环境配置指南](docs/python-environment-guide.md)安装 Python 并启动一次项目。
4. 不确定需求时，在 Issue 下或 PR 中提问，不要依靠猜测大范围改代码。

### 路线一：Issue 认领

1. 阅读准备认领的 Issue，包括允许修改的文件和验收标准。
2. 在原 Issue 下评论 `姓名：你的名字，已认领`，让维护者知道你正在参与。
3. 按 Issue 写明的范围完成实现，并在 PR 中填写 `Closes #编号`。

### Issue 认领规则

- 项目贡献截止时间为 **2026 年 9 月 27 日 12:00（北京时间，中午十二点）**，请在此时间前成功提交 PR；截止时间以 GitHub 上显示的 PR 创建时间为准。
- 一位同学可以根据自己的时间和能力认领多个 Issue，但应为每个 Issue 分别创建分支和 PR。
- 多位同学可以同时认领同一个 Issue。这不是“先到先得”，重复认领不会使其他人的提交失效。
- 同题提交会分别 Review。我们关注每个人的实现思路、问题解决过程和表达能力，不以谁最先提交作为唯一标准。
- 如果认领后确定无法继续，建议在原 Issue 下说明情况，方便维护者了解进度；这不会影响你参与其他 Issue。

认领评论示例：

```text
姓名：张三，已认领
```

### 路线二：Free-play 自由发挥

在仓库的 `contrib/你的真实姓名/` 目录中，使用 Python 完成一个独立、有明确使用价值或趣味性的项目。例如文字游戏、待办清单、数据小工具或命令行互动程序。

- 先阅读 [contrib 目录规范](contrib/README.md)，再创建自己的目录；例如姓名为“张三”时使用 `contrib/张三/`。
- 每个自由发挥项目必须有自己的 `README.md`，说明功能、运行方式、结构、手动验证、已知不足，以及参考资料和 AI 使用情况。
- 拒绝玩具代码：只有几行加减乘除、只 `print` 固定文案或无法进行实际操作的程序不符合要求。项目至少应包含完整的输入、处理、输出流程，以及循环/条件分支或有意义的数据处理。
- 可以借鉴搜索结果或 AI，但不得直接复制自己无法解释的完整项目。借鉴核心思路或代码时，必须在项目 README 中给出链接，并说明自己理解和改动的内容。
- 自由发挥不需要认领 Issue，也不要在 PR 中填写 `Closes #编号`。

## 2. Fork 并 Clone 项目

不要直接修改协会的原仓库。先在 GitHub 项目页面右上角点击 **Fork**，将项目复制到自己的账号下。

进入你 Fork 后的仓库，点击 **Code**，复制 HTTPS 地址，然后在终端执行：

```bash
git clone https://github.com/你的用户名/live2d-focus-assistant-recruitment-2026.git
cd live2d-focus-assistant-recruitment-2026
```

建议把协会原仓库添加为 `upstream`，方便获取后续更新：

```bash
git remote add upstream https://github.com/你的用户名/live2d-focus-assistant-recruitment-2026.git
git remote -v
```

`origin` 表示你自己的 Fork，`upstream` 表示协会原仓库。

## 3. 创建分支

不要直接在 `main` 分支写代码。假设你认领的是 Issue #12，可以这样创建分支：

```bash
git switch -c feat/issue-12-history-search
```

推荐分支名：

- 新功能：`feat/issue-编号-简短名称`
- 修复问题：`fix/issue-编号-简短名称`
- 自由发挥：`feat/contrib-你的真实姓名-简短名称`

即使认领了多个 Issue，也要坚持一个分支只处理一个目标。不要顺手修改页面配色、格式化整个项目或重构无关代码，否则会增加合并难度。

## 4. 编写代码

- Issue 路线只修改 Issue 允许的文件，遵守现有模块边界和命名风格。
- Free-play 路线的项目代码、README 和项目专用依赖说明均应放在自己的 `contrib/你的真实姓名/` 内；不要修改 `src/`、`static/`、`templates/` 或其他同学的目录。
- 优先使用 Python 标准库和项目已有依赖，不随意引入大型第三方库。
- 不提交 `.venv/`、`instance/`、`__pycache__/`、`.pytest_cache/`、编辑器配置或个人数据库。
- 可以查搜索引擎或使用 AI，但不能直接复制自己看不懂的完整代码。
- 若借鉴了核心实现，在 PR 的“参考资料”中贴出链接，并说明你理解和修改了什么。
- 不修改 Shizuku 模型、音频、Live2D 运行库以及与 Issue 无关的前端文件。

原则很简单：一段代码如果你看不懂、改不动、讲不出，就不要提交。

## 5. 手动检查

本次招新不要求新生运行自动化测试，也不会因为你不会使用 `pytest` 扣分。但提交前至少应完成 Issue 中写明的手动验收，或为 Free-play 亲自走通项目 README 中的使用流程，并确认：

- 项目能够正常启动；
- 你修改的功能可以实际操作或调用；
- 输入错误时程序不会直接崩溃；
- Issue 路线中，原有的开始、暂停、继续、完成和放弃流程仍能使用。

请把实际检查过程和结果写进 PR。不要填写没有执行过的检查。

## 6. 提交代码

先查看改动范围：

```bash
git status
git diff
```

确认没有个人文件后提交：

```bash
git add 你修改的文件
git commit -m "feat: 完成历史记录关键词搜索"
git push -u origin feat/issue-12-history-search
```

提交信息推荐使用以下格式：

```text
类型: 简短说明
```

常用类型：

- `feat:` 新增功能，例如 `feat: 增加每日专注汇总`
- `fix:` 修复错误，例如 `fix: 处理空关键词查询`
- `docs:` 只修改说明文档
- `refactor:` 调整代码结构，但不改变功能

对于招新 Issue，绝大多数提交使用 `feat:` 或 `fix:` 即可。说明应写清楚“做了什么”，尽量不要使用 `update`、`改一下`、`最终版` 等模糊文字。

## 7. 提交 Pull Request

推送后，打开你 Fork 的 GitHub 页面，点击 **Compare & pull request**：

1. 确认目标仓库是协会原仓库，目标分支是招新时指定的分支。
2. PR 标题建议写为：`feat: 完成历史记录关键词搜索`。
3. 按 PR 模板逐项填写，不要删除模板问题。
4. Issue 路线在“关联 Issue”中填写 `Closes #编号`；Free-play 路线填写项目目录和项目名称。
5. 提交后等待 Review，根据评审意见继续在原分支修改并 `git push`，不需要重新创建 PR。

请不要自行合并 PR。代码答辩或 Review 完成后，由项目维护者决定是否合并。

## 8. 如何同步原仓库更新

如果开发期间原仓库有更新，可以执行：

```bash
git fetch upstream
git switch main
git merge upstream/main
git push origin main
git switch feat/issue-12-history-search
git merge main
```

如果出现不理解的冲突，不要删除别人的代码来强行解决。保留终端报错信息，在 Issue 或群内说明你执行过的命令并寻求帮助。

## 9. 我们会在答辩中关注什么

- 你如何把 Issue 拆成具体步骤；
- 你是否能说明关键变量、条件分支和数据流；
- 遇到报错时搜索了什么、尝试了什么；
- 为什么选择当前实现，以及它还有哪些不足；

提交成功并不代表必须写出“完美答案”。真实、可运行、能解释的实现比堆砌复杂代码更重要。
