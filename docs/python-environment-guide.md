# Python 环境配置指南

这份指南帮助第一次接触 Python 的同学在自己的电脑上运行 Live2D 专注助手。项目要求 Python 3.11 或更高版本，推荐使用 Python 3.11。

## 1. 先认识三个工具

- **终端**：输入命令的窗口。Windows 可使用 PowerShell，macOS 可使用“终端”。
- **Python**：运行项目后端代码的程序。
- **虚拟环境**：项目专用的 Python 小环境，避免不同项目的依赖互相影响。

终端中的命令需要逐行执行。命令前面的目录路径不用手动输入。

## 2. Windows 安装 Python

1. 打开 [Python 官方下载页面](https://www.python.org/downloads/)。
2. 下载并安装 Python 3.11。
3. 安装界面中勾选 **Add python.exe to PATH**。
4. 安装完成后关闭并重新打开 PowerShell。

检查安装：

```powershell
py -3.11 --version
```

看到类似 `Python 3.11.x` 即表示安装成功。如果系统提示找不到 `py`，尝试：

```powershell
python --version
```

如果打开了 Microsoft Store 或显示的版本低于 3.11，请重新使用 Python 官网安装包安装，并确认勾选 PATH 选项。

## 3. macOS 或 Linux 安装 Python

先执行：

```bash
python3 --version
```

版本为 3.11 或更高即可。macOS 可从 Python 官网安装；Linux 请使用自己发行版的软件包管理器。以下步骤中的 `py -3.11` 在 macOS/Linux 上应替换为 `python3`。

## 4. 下载项目

建议先按[贡献指南](../CONTRIBUTING.md) Fork 项目，再 Clone 自己的仓库：

```bash
git clone https://github.com/double-god/live2d-focus-assistant-recruitment-2026.git
cd live2d-focus-assistant-recruitment-2026
```

如果提示找不到 `git`，请先安装 [Git](https://git-scm.com/downloads)。也可以使用 GitHub Desktop 完成 Clone，再在项目目录打开终端。

## 5. 创建虚拟环境

Windows PowerShell：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 提示“禁止运行脚本”，只为当前窗口临时放开限制：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

macOS/Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

激活成功后，终端命令行前通常会出现 `(.venv)`。每次新开终端准备运行项目时，都需要重新激活虚拟环境。

退出虚拟环境可执行：

```bash
deactivate
```

## 6. 安装项目依赖

确认终端前有 `(.venv)`，然后执行：

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

这里安装的是 Flask 和项目开发所需的 Python 包。不要双击运行 `requirements.txt`。

若下载速度慢，可以先耐心等待或更换网络。遇到错误时，请保留完整报错，不要只截图最后一行。

## 7. 启动项目

在项目根目录执行：

```bash
python app.py
```

看到以下地址表示启动成功：

```text
http://127.0.0.1:5000
```

用浏览器打开该地址。不要直接双击 `templates/index.html`，否则 Python 接口、专注记录和 Live2D 资源可能无法正常工作。

停止服务时，回到终端按 `Ctrl+C`。

## 8. 如何确认自己位于正确目录

Windows：

```powershell
Get-Location
Get-ChildItem
```

macOS/Linux：

```bash
pwd
ls
```

正确目录中应能看到 `app.py`、`requirements.txt`、`src`、`static` 和 `templates`。如果提示找不到 `app.py` 或 `requirements.txt`，通常是终端当前目录不对，请先使用 `cd` 进入项目目录。

## 9. 常见问题

### `python` 或 `py` 不是命令

Python 没有正确安装，或安装后没有重新打开终端。Windows 请重新运行安装程序并勾选 PATH。

### 无法激活 `.venv`

确认已经在项目根目录创建虚拟环境。Windows PowerShell 可使用本指南提供的临时执行策略命令；不要为了一个项目永久关闭系统脚本保护。

### `No module named flask`

通常是没有激活虚拟环境，或没有执行依赖安装：

```bash
python -m pip install -r requirements.txt
```

### 端口 5000 已被占用

先检查是否已经在另一个终端启动过项目，并在旧终端按 `Ctrl+C`。仍无法解决时，可临时运行：

```bash
python -m flask --app app run --port 5001
```

然后打开 `http://127.0.0.1:5001`。

### 页面出现但 Live2D 角色没有显示

先刷新页面，并确认是通过 `http://127.0.0.1:5000` 打开。角色无法加载时，专注功能仍应可以使用。提交问题时请附浏览器版本、终端输出和浏览器开发者工具 Console 中的报错。

## 10. 求助时应该提供什么

不要只说“运行不了”。请提供：

- 操作系统和 Python 版本；
- 当前执行的完整命令；
- 从第一行开始的完整报错文本；
- 你已经尝试过的方法；
- 问题发生前最后一次成功的操作。

学会保存、阅读和检索报错信息，也是本次招新希望考察的重要能力。
