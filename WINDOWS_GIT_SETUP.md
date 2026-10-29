# Windows 搭建 Git 和 VS Code 协作教程

本教程适用于 Windows 10/11，目标是完成以下工作：

- 安装 Git
- 在 VS Code 中使用 Git
- 配置提交用户名和邮箱
- 克隆 GitHub 项目
- 使用独立分支开发，避免影响 `main` 主分支
- 提交、推送并创建 Pull Request
- 处理常见问题

本文默认项目托管在 GitHub，示例仓库地址为：

```text
https://github.com/gumengduanyi/Medical-and-health.git
```

命令中的 `用户名`、`邮箱`、`分支名称` 和 `项目目录` 都需要替换成你自己的值。除非特别说明，下面的命令都在项目根目录执行。

## 开始前准备

开始之前请确认：

- Windows 10 或 Windows 11 已联网
- 已拥有 GitHub 账号
- 已获得目标仓库的访问权限
- 已安装 Visual Studio Code
- 知道项目要保存在哪个目录，例如 `D:\Projects`

如果只是查看公开代码，只需要仓库地址；如果要推送代码，必须是仓库所有者、协作者，或者把代码推送到自己的仓库后再提交 Pull Request。

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

其他安装页面通常保持默认即可。下面几个选项比较重要：

- **Choosing the default editor**：选择 `Visual Studio Code`，不建议新手选择 Vim
- **Adjusting the name of the initial branch**：如果出现该选项，建议填写 `main`
- **PATH 环境变量**：选择 `Git from the command line and also from 3rd-party software`
- **HTTPS 传输后端**：保持默认的 `Use the OpenSSL library`
- **换行符转换**：Windows 用户通常选择 `Checkout Windows-style, commit Unix-style line endings`
- **终端模拟器**：Git Bash 可以选择默认的 `Use MinTTY`
- **凭据管理器**：保留 `Git Credential Manager`

Git Credential Manager 会在第一次访问 GitHub 时打开浏览器登录，并安全保存凭据。不要把 GitHub 密码写进远程地址、脚本或项目文件中。

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

同时检查 Git Bash、PowerShell 和 VS Code 是否都能找到 Git：

Git Bash：

```bash
which git
git --version
```

PowerShell：

```powershell
Get-Command git
git --version
```

如果 Git Bash 可以使用、PowerShell 不可以，通常是终端尚未重启或 PATH 没有刷新。关闭所有 VS Code 窗口后重新打开，再检查一次。

## 三、配置 VS Code

### 1. 安装推荐扩展

在 VS Code 左侧打开扩展面板，搜索并安装：

- `GitHub Pull Requests and Issues`
- `Git Graph`（可选，用于查看提交图）
- 项目所需的语言扩展，例如 Python、Vue、ESLint 等

VS Code 自带 Git 集成，不需要另外安装 Git 插件。扩展安装完成后，重新打开项目目录。

### 2. 设置默认终端

按下：

```text
Ctrl + Shift + P
```

搜索并选择：

```text
Terminal: Select Default Profile
```

可以选择：

- Git Bash：命令示例与 Linux/macOS 一致
- PowerShell：适合 Windows 原生命令

本文主要使用 Git Bash 命令。如果使用 PowerShell，`git` 命令仍然可用，但删除文件、设置环境变量等命令的写法可能不同。

## 四、配置 Git 提交身份

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

检查当前项目实际使用的身份：

```bash
git config user.name
git config user.email
```

检查配置来源，排查全局配置和项目配置互相覆盖的问题：

```bash
git config --list --show-origin
```

如果希望提交显示在 GitHub 账号下，提交邮箱必须是 GitHub 账号已经验证的邮箱，或者使用 GitHub 提供的 `users.noreply.github.com` 隐私邮箱。

## 五、在 VS Code 中打开项目

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

打开后，在 VS Code 终端执行：

```bash
pwd
git status
git remote -v
```

你应该看到：

- 当前目录是项目根目录
- `git status` 能正常执行
- `origin` 指向正确的 GitHub 仓库

如果 `git status` 提示 `not a git repository`，说明你打开的不是仓库根目录，或者还没有执行克隆操作。

## 六、登录 GitHub

在 VS Code 左下角点击账户图标，选择登录 GitHub。

也可以在第一次推送时按照提示登录浏览器。Git for Windows 通常会使用 Git Credential Manager 保存登录凭据，不需要每次重复输入密码。

注意：GitHub 已经不支持使用账号密码直接进行 Git 推送。使用 HTTPS 时，应通过浏览器登录、Git Credential Manager 或 Personal Access Token 完成认证。

### 推荐方式：HTTPS + Git Credential Manager

查看当前远程地址：

```bash
git remote -v
```

HTTPS 地址一般类似：

```text
https://github.com/用户名/仓库名.git
```

第一次执行 `git push` 时，Git Credential Manager 通常会打开浏览器。登录正确的 GitHub 账号后，回到终端等待命令完成。GitHub 不再支持直接输入账号密码作为 Git 密码，不要反复尝试使用账号密码推送。

### 可选方式：SSH

如果经常使用 GitHub，可以配置 SSH。配置一次后，后续推送通常不需要反复网页登录。

生成 SSH 密钥：

```bash
ssh-keygen -t ed25519 -C "你的GitHub邮箱"
```

一路按 Enter 可以使用默认路径。如果设置了密码短语，请妥善保存，不能把私钥发给别人。

启动 ssh-agent 并添加密钥：

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

查看公钥：

```bash
cat ~/.ssh/id_ed25519.pub
```

复制完整内容，进入 GitHub：

```text
头像 → Settings → SSH and GPG keys → New SSH key
```

粘贴公钥并保存，然后测试连接：

```bash
ssh -T git@github.com
```

看到类似 `Hi 用户名! You've successfully authenticated` 的提示，说明 SSH 配置成功。

SSH 远程地址格式：

```text
git@github.com:用户名/仓库名.git
```

把当前项目从 HTTPS 切换到 SSH：

```bash
git remote set-url origin git@github.com:用户名/仓库名.git
git remote -v
```

## 七、使用分支协作，避免影响 main

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

### 分支命名建议

常用格式：

```text
feature/功能名称
fix/问题名称
docs/文档名称
refactor/重构名称
chore/配置名称
```

例如：

```bash
git switch -c feature/notification-panel
```

查看本地和远程分支：

```bash
git branch
git branch -r
git branch -a
```

删除已经合并的本地分支：

```bash
git branch -d feature/medicine-page
```

只有确认分支内容已经合并或不再需要时，才使用强制删除：

```bash
git branch -D feature/medicine-page
```

## 八、提交自己的修改

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

### 推荐的提交前检查

```bash
git status
git diff --stat
git diff
```

确认没有把以下内容加入提交：

- 密码、Token、私钥
- `.env` 等本地配置
- `.venv`、`node_modules` 等依赖目录
- 临时日志、缓存、数据库文件
- 与本次功能无关的大型文件

查看已经暂存的内容：

```bash
git diff --cached
```

如果误把文件加入暂存区，可以取消暂存，但不会删除文件：

```bash
git restore --staged 文件路径
```

只提交指定文件：

```bash
git add frontend/pages/index/index.vue
git add backend/app/services/rag_service.py
git commit -m "feat: improve health assistant notifications"
```

提交信息建议使用统一格式：

```text
feat: 新增功能
fix: 修复问题
docs: 更新文档
refactor: 重构代码
test: 增加测试
chore: 调整构建或配置
```

查看最近提交：

```bash
git log --oneline --decorate -10
```

## 九、推送自己的分支

第一次推送时执行：

```bash
git push -u origin feature/medicine-page
```

之后再次推送只需要：

```bash
git push
```

推送后，GitHub 上会出现你的分支。这个操作不会修改 `main`。

推送前再次确认当前分支：

```bash
git branch --show-current
git status
```

如果当前分支不是自己的功能分支，不要直接执行推送，先切换到正确分支。

查看远程分支最新状态：

```bash
git fetch origin
git branch -vv
```

第一次推送成功后，当前分支会记录上游分支。之后可以直接执行：

```bash
git push
```

## 十、通过 Pull Request 合并

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

Pull Request 描述建议写清楚：

```text
## 修改内容
- 做了什么

## 验证方式
- 执行了哪些测试
- 是否检查了前端页面

## 注意事项
- 是否需要配置环境变量
- 是否存在已知限制
```

合并前确认：

- base 是 `main`
- compare 是自己的功能分支
- 改动文件和提交记录符合预期
- 自动检查和必要测试已经通过
- 没有把 `.env`、密码或本地生成文件推送到仓库

## 十一、main 更新后同步自己的分支

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

### 使用 rebase 同步 main

如果团队约定使用 rebase，可以这样操作：

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git switch feature/medicine-page
git rebase main
```

rebase 过程中发生冲突时，先查看状态：

```bash
git status
```

修改冲突文件、删除冲突标记后：

```bash
git add 冲突文件路径
git rebase --continue
```

不想继续时：

```bash
git rebase --abort
```

rebase 已经推送过的分支后，推送可能需要：

```bash
git push --force-with-lease
```

不要使用不带保护的 `git push --force`，也不要对 `main` 强制推送。

## 十二、推荐的日常协作流程

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

### 开始工作前

```bash
git status
git switch main
git pull --ff-only origin main
git switch feature/自己的分支
git merge main
```

### 开发过程中

小步提交，每个提交只完成一个清晰目的：

```bash
git status
git diff
git add 相关文件
git commit -m "feat: 描述本次修改"
```

### 开发完成后

```bash
git push -u origin feature/自己的分支
```

然后创建 Pull Request，不要直接把功能分支合并到本地 `main` 后再推送，除非团队明确允许这样做。

## 十三、常见问题

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

### 2. `git clone` 提示仓库不存在

检查仓库地址是否拼写正确，并确认仓库是公开的，或者当前 GitHub 账号有访问权限：

```bash
git ls-remote https://github.com/用户名/仓库名.git
```

私有仓库需要先登录 GitHub，或使用有权限的 SSH 密钥。

### 3. `git pull` 提示分支发生分叉

Git 需要你选择合并方式。普通团队协作可以使用合并方式：

```bash
git pull --no-rebase origin main
```

也可以设置当前项目默认使用合并：

```bash
git config pull.rebase false
```

不要在不了解后果时直接使用强制推送。

### 4. 推送时提示没有权限

检查以下内容：

- 是否登录了正确的 GitHub 账号
- 是否被仓库管理员加入为协作者
- 当前推送的仓库地址是否正确
- 是否正在推送自己的分支，而不是没有权限的远程分支

查看远程地址：

```bash
git remote -v
```

### 5. 推送时提示 `non-fast-forward`

说明远程分支已经有你本地没有的提交。先获取远程更新：

```bash
git fetch origin
git log --oneline HEAD..origin/你的分支名
```

确认远程提交后，把远程更新合并到当前分支：

```bash
git pull --rebase origin 你的分支名
git push
```

如果团队不使用 rebase，可以改用：

```bash
git pull --no-rebase origin 你的分支名
git push
```

### 6. 不小心在 main 上修改了代码

如果还没有提交，可以先创建新分支，修改会跟随到新分支：

```bash
git switch -c feature/save-my-work
```

然后在新分支提交和推送。

如果已经提交但还没有推送，也可以先创建分支保存提交，再恢复 `main`。操作前建议先联系项目负责人，避免误操作。

### 7. 不想提交本地生成文件

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

## 十四、最简命令清单

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

## 十五、协作原则

- `main` 只保留可用、经过审核的代码。
- 每个人使用自己的功能分支。
- 不要直接向 `main` 推送代码。
- 不要随意执行 `git push --force`。
- 提交前检查 `git diff` 和 `git status`。
- Pull Request 合并前先完成必要的测试。
- 不要把 `.env`、密码、Token 和本地数据库等敏感或临时文件提交到仓库。
