# 新生贡献指南

欢迎参与 Live2D 专注助手项目。本项目的招新任务以 GitHub Issue 为单位：每位同学凭自己兴趣与能力认领 Issue，独立完成后，通过 Pull Request（简称 PR）提交代码。

我们不要求你入门时就熟悉完整的工程流程，也不要求你运行自动化测试。我们更关注你能否读懂任务、主动查资料、完成一个真实功能，并清楚说明自己的思路。

## 1. 开始之前

请先完成以下准备：

1. 注册并登录 GitHub。
2. 阅读准备认领的 Issue，包括允许修改的文件和验收标准。
3. 在原 Issue 下评论 `姓名：你的名字，已认领`，让维护者知道谁正在参与。
4. 按照 [Python 环境配置指南](docs/python-environment-guide.md)安装 Python 并启动一次项目。
5. 不确定需求时，在 Issue 下提问，不要依靠猜测大范围改代码。

### Issue 认领规则

- 项目贡献截止日期为 **2026 年 9 月 27 日**，请在截止日前提交 PR；具体关闭时间以招新群或维护者通知为准。
- 一位同学可以根据自己的时间和能力认领多个 Issue，但应为每个 Issue 分别创建分支和 PR。
- 多位同学可以同时认领同一个 Issue。这不是“先到先得”，重复认领不会使其他人的提交失效。
- 同题提交会分别 Review。我们关注每个人的实现思路、问题解决过程和表达能力，不以谁最先提交作为唯一标准。
- 如果认领后确定无法继续，建议在原 Issue 下说明情况，方便维护者了解进度；这不会影响你参与其他 Issue。

认领评论示例：

```text
姓名：张三，已认领
```

## 2. Fork 并 Clone 项目

不要直接修改协会的原仓库。先在 GitHub 项目页面右上角点击 **Fork**，将项目复制到自己的账号下。

进入你 Fork 后的仓库，点击 **Code**，复制 HTTPS 地址，然后在终端执行：

```bash
git clone https://github.com/你的用户名/live2d-focus-assistant.git
cd live2d-focus-assistant
```

建议把协会原仓库添加为 `upstream`，方便获取后续更新：

```bash
git remote add upstream https://github.com/协会账号/live2d-focus-assistant.git
git remote -v
```

上面的“协会账号”应替换为招新时公布的实际账号。`origin` 表示你自己的 Fork，`upstream` 表示协会原仓库。

## 3. 为 Issue 创建分支

不要直接在 `main` 分支写代码。假设你认领的是 Issue #12，可以这样创建分支：

```bash
git switch -c feat/issue-12-history-search
```

推荐分支名：

- 新功能：`feat/issue-编号-简短名称`
- 修复问题：`fix/issue-编号-简短名称`

即使认领了多个 Issue，也要坚持一个分支只处理一个 Issue。不要顺手修改页面配色、格式化整个项目或重构无关代码，否则会增加合并难度。

## 4. 编写代码

- 只修改 Issue 允许的文件，遵守现有模块边界和命名风格。
- 优先使用 Python 标准库和项目已有依赖，不随意引入大型第三方库。
- 不提交 `.venv/`、`instance/`、`__pycache__/`、`.pytest_cache/`、编辑器配置或个人数据库。
- 可以查搜索引擎或使用 AI，但不能直接复制自己看不懂的完整代码。
- 若借鉴了核心实现，在 PR 的“参考资料”中贴出链接，并说明你理解和修改了什么。
- 不修改 Shizuku 模型、音频、Live2D 运行库以及与 Issue 无关的前端文件。

原则很简单：一段代码如果你看不懂、改不动、讲不出，就不要提交。

## 5. 手动检查

本次招新不要求新生运行自动化测试，也不会因为你不会使用 `pytest` 扣分。但提交前至少应完成 Issue 中写明的手动验收，并确认：

- 项目能够正常启动；
- 你修改的功能可以实际操作或调用；
- 输入错误时程序不会直接崩溃；
- 原有的开始、暂停、继续、完成和放弃流程仍能使用。

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
4. 在“关联 Issue”中填写 `Closes #编号`。
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
