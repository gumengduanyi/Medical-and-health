# Windows 搭建 Git 和 VS Code 协作教程

本教程适用于 Windows 10/11，目标是完成以下工作：

- 安装 Git
- 在 VS Code 中使用 Git
- 配置提交用户名和邮箱
- 克隆 GitHub 项目
- 使用独立分支开发，避免影响 `main` 主分支
- 提交、推送并创建 Pull Request
- 处理常见问题

## 一、安装 Git for Windows

### 1. 下载 Git

打开 Git 官方网站：

<https://git-scm.com/download/win>

下载 Windows 版本并运行安装程序。

### 2. 安装选项

安装过程中大部分选项保持默认即可。建议确认以下选项：

- 选择 Git 默认编辑器时，可以选择 `Visual Studio Code`
- 选择 PATH 配置时，保持默认的 `Git from the command line and also from 3rd-party software`
- 选择换行符时，Windows 用户保持默认即可
- 安装 Git Bash 和 Git Credential Manager

安装完成后，点击 Windows 开始菜单，打开：

```text
Git Bash
```

或者在 VS Code 中打开终端。

## 二、检查 Git 是否安装成功

在 Git Bash 或 VS Code 终端执行：

```bash
git --version
```

如果看到类似下面的结果，说明安装成功：

```text
git version 2.x.x.windows.x
```

如果提示找不到 `git` 命令，请关闭并重新打开 VS Code。仍然无法使用时，重新安装 Git，并确认安装时选择了加入 PATH 的选项。

## 三、配置 Git 提交身份

Git 每次提交都需要记录提交者姓名和邮箱。第一次使用 Git 时必须配置，否则 VS Code 可能提示：

```text
请确保已在 Git 中配置你的 "user.name" 和 "user.email"
```

### 1. 配置全局身份

在 VS Code 终端执行，将示例内容替换成自己的信息：

```bash
git config --global user.name "你的姓名或 GitHub 用户名"
git config --global user.email "你的邮箱"
```

例如：

```bash
git config --global user.name "caoguoxing"
git config --global user.email "你的GitHub邮箱@example.com"
```

建议邮箱使用 GitHub 账号中已验证的邮箱。也可以使用 GitHub 提供的隐私邮箱，格式类似：

```text
12345678+用户名@users.noreply.github.com
```

### 2. 检查配置

```bash
git config --global user.name
git config --global user.email
```

查看全部 Git 配置：

```bash
git config --global --list
```

如果只想为当前项目设置身份，不影响其他项目，可以在项目目录中执行：

```bash
git config user.name "项目提交者姓名"
git config user.email "项目提交邮箱"
```

## 四、在 VS Code 中打开项目

### 方式一：直接克隆项目

在 VS Code 中按下：

```text
Ctrl + Shift + P
```

输入并选择：

```text
Git: Clone
```

输入仓库地址：

```text
https://github.com/gumengduanyi/Medical-and-health.git
```

选择项目保存位置，克隆完成后点击 **Open** 打开项目。

### 方式二：使用终端克隆

```bash
git clone https://github.com/gumengduanyi/Medical-and-health.git
cd Medical-and-health
code .
```

如果 `code` 命令不可用，可以在 VS Code 中选择：

```text
文件 → 打开文件夹
```

然后选择项目目录。

## 五、登录 GitHub

在 VS Code 左下角点击账户图标，选择登录 GitHub。

也可以在第一次推送时按照提示登录浏览器。Git for Windows 通常会使用 Git Credential Manager 保存登录凭据，不需要每次重复输入密码。

注意：GitHub 已经不支持使用账号密码直接进行 Git 推送。使用 HTTPS 时，应通过浏览器登录、Git Credential Manager 或 Personal Access Token 完成认证。

## 六、使用分支协作，避免影响 main

多人协作时，不要直接在 `main` 分支开发。每个人都创建自己的功能分支。

### 1. 开始开发前同步 main

```bash
git switch main
git pull origin main
```

如果 Git 版本较旧，也可以使用：

```bash
git checkout main
git pull origin main
```

### 2. 创建自己的分支

```bash
git switch -c feature/功能名称
```

例如：

```bash
git switch -c feature/medicine-page
```

旧版 Git 写法：

```bash
git checkout -b feature/medicine-page
```

在 VS Code 左下角看到 `feature/medicine-page`，说明当前已经在自己的分支上。

### 3. 确认当前分支

```bash
git branch --show-current
git status
```

如果显示的是 `main`，先切换到自己的功能分支再修改代码。

## 七、提交自己的修改

在 VS Code 左侧点击 **源代码管理** 图标，检查改动文件。

建议先查看修改内容，再提交：

```bash
git diff
```

确认无误后执行：

```bash
git add .
git commit -m "feat: 完成功能描述"
```

例如：

```bash
git add .
git commit -m "feat: add medicine management page"
```

也可以直接使用 VS Code 源代码管理面板：

1. 检查修改文件
2. 点击文件旁边的 `+` 暂存
3. 填写提交信息
4. 点击 **提交**

## 八、推送自己的分支

第一次推送时执行：

```bash
git push -u origin feature/medicine-page
```

之后再次推送只需要：

```bash
git push
```

推送后，GitHub 上会出现你的分支。这个操作不会修改 `main`。

## 九、通过 Pull Request 合并

推送分支后，在 GitHub 仓库页面点击 **Compare & pull request**，或者进入：

```text
Pull requests → New pull request
```

确认：

```text
base: main
compare: feature/medicine-page
```

填写修改说明并创建 Pull Request。其他成员审核通过后，再合并到 `main`。

推荐使用 **Squash and merge**，可以将一个功能分支的多个小提交合并成一个整洁的提交。

## 十、main 更新后同步自己的分支

其他人合并代码后，你需要把最新的 `main` 同步到自己的分支：

```bash
git switch main
git pull origin main
git switch feature/medicine-page
git merge main
```

如果出现冲突，VS Code 会显示冲突位置。逐个文件处理后执行：

```bash
git add .
git commit -m "merge: sync latest main"
git push
```

如果暂时不想处理冲突，可以中止合并：

```bash
git merge --abort
```

## 十一、推荐的日常协作流程

每次开始工作：

```bash
git switch main
git pull origin main
git switch feature/自己的分支
```

开发完成后：

```bash
git status
git diff
git add .
git commit -m "feat: 描述本次修改"
git push
```

然后在 GitHub 创建 Pull Request，审核完成后合并。

## 十二、常见问题

### 1. 提示没有配置 `user.name` 和 `user.email`

执行：

```bash
git config --global user.name "你的姓名"
git config --global user.email "你的邮箱"
```

然后重新提交：

```bash
git commit -m "feat: 完成功能"
```

### 2. `git pull` 提示分支发生分叉

Git 需要你选择合并方式。普通团队协作可以使用合并方式：

```bash
git pull --no-rebase origin main
```

也可以设置当前项目默认使用合并：

```bash
git config pull.rebase false
```

不要在不了解后果时直接使用强制推送。

### 3. 推送时提示没有权限

检查以下内容：

- 是否登录了正确的 GitHub 账号
- 是否被仓库管理员加入为协作者
- 当前推送的仓库地址是否正确
- 是否正在推送自己的分支，而不是没有权限的远程分支

查看远程地址：

```bash
git remote -v
```

### 4. 不小心在 main 上修改了代码

如果还没有提交，可以先创建新分支，修改会跟随到新分支：

```bash
git switch -c feature/save-my-work
```

然后在新分支提交和推送。

如果已经提交但还没有推送，也可以先创建分支保存提交，再恢复 `main`。操作前建议先联系项目负责人，避免误操作。

### 5. 不想提交本地生成文件

在项目根目录的 `.gitignore` 中加入不应提交的文件，例如：

```gitignore
# Python
.venv/
__pycache__/
*.pyc

# Node / uni-app
node_modules/

# Local database and environment
*.db
.env

# Build output
unpackage/dist/
```

如果文件已经被 Git 跟踪，仅修改 `.gitignore` 不会自动取消跟踪，需要执行：

```bash
git rm --cached 文件名
```

## 十三、最简命令清单

```bash
# 第一次配置
 git config --global user.name "你的姓名"
 git config --global user.email "你的邮箱"

# 克隆项目
 git clone https://github.com/gumengduanyi/Medical-and-health.git
 cd Medical-and-health

# 创建功能分支
 git switch main
 git pull origin main
 git switch -c feature/功能名称

# 提交和推送
 git add .
 git commit -m "feat: 完成功能"
 git push -u origin feature/功能名称
```

## 十四、协作原则

- `main` 只保留可用、经过审核的代码。
- 每个人使用自己的功能分支。
- 不要直接向 `main` 推送代码。
- 不要随意执行 `git push --force`。
- 提交前检查 `git diff` 和 `git status`。
- Pull Request 合并前先完成必要的测试。
- 不要把 `.env`、密码、Token 和本地数据库等敏感或临时文件提交到仓库。
