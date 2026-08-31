# GitHub 网页上传更新步骤

本文档只说明如何通过 GitHub 网页上传项目更改，并使用新分支和 Pull Request，避免直接合并到 `main` 主分支。

## 一、打开仓库

在浏览器中打开项目仓库：

```text
https://github.com/gumengduanyi/Medical-and-health
```

确认进入的是正确仓库，不要上传到其他项目。

## 二、新建更新分支

为了避免直接修改 `main`，上传前先创建一个新分支。

1. 在仓库页面左上角找到分支按钮，通常显示为 `main`。
2. 点击分支按钮。
3. 在输入框中输入新的分支名。

示例：

```text
docs/update-readme
feature/upload-page
fix/backend-api
```

4. 点击 `Create branch: 分支名 from main`。
5. 确认页面左上角显示的分支已经不是 `main`，而是刚创建的新分支。

注意：如果当前仍然显示 `main`，不要上传文件，否则会直接提交到主分支。

## 三、上传修改后的文件

1. 确认当前分支是自己的新分支。
2. 点击仓库页面右上方的 `Add file`。
3. 选择 `Upload files`。
4. 将本地修改过的文件拖到上传区域。
5. 等待文件上传完成。

如果只修改了一个文件，只上传这个文件即可。例如：

```text
backend/app.py
```

如果修改了前端页面，只上传对应页面文件即可。例如：

```text
frontend/pages/upload/upload.vue
frontend/pages/result/result.vue
```

不要每次都上传整个项目，除非你确认所有文件都需要更新。

## 四、填写提交说明

上传页面底部会出现提交信息输入框。

建议写清楚这次修改内容，例如：

```text
fix: update backend upload api
```

或：

```text
docs: update upload guide
```

不建议写：

```text
更新
修改
111
final
```

## 五、提交到当前分支

在提交前再次确认提交目标是自己的新分支。

页面底部应显示类似：

```text
Commit directly to the docs/update-readme branch
```

确认不是下面这种：

```text
Commit directly to the main branch
```

确认无误后，点击：

```text
Commit changes
```

这一步只是把文件提交到你的新分支，不会直接合并到 `main`。

## 六、创建 Pull Request

提交完成后，GitHub 通常会出现 `Compare & pull request` 按钮。

1. 点击 `Compare & pull request`。
2. 填写 PR 标题。
3. 在描述中说明本次修改了什么。
4. 点击 `Create pull request`。

PR 标题示例：

```text
docs: update upload guide
```

PR 描述示例：

```text
本次修改：
- 更新 GitHub 网页上传步骤
- 补充新分支和 PR 流程

注意事项：
- 本次修改没有直接提交到 main
- 需要确认后再合并
```

## 七、确认后再合并

创建 PR 后，文件还没有进入 `main`。

需要组员或项目负责人检查后，再点击：

```text
Merge pull request
Confirm merge
```

只有完成这一步，更新才会合并到 `main` 主分支。

## 八、网页上传注意事项

- 上传前一定确认当前分支不是 `main`。
- 每次只上传本次修改相关的文件。
- 不要上传 `node_modules/`。
- 不要上传 `.DS_Store`。
- 不要上传 `__pycache__/`。
- 不要上传 `.venv/`。
- 不要上传 `frontend/unpackage/debug/`。
- 不要上传 `backend/uploads/` 中的测试图片。
- 不要把密码、Token、API Key 或个人账号信息上传到仓库。
- 如果 GitHub 提示文件冲突，不要随便覆盖，先和组员确认。

## 九、最推荐的网页协作流程

```text
1. 打开 GitHub 仓库
2. 从 main 新建自己的分支
3. 在新分支上传修改后的文件
4. 填写提交说明并 Commit changes
5. 创建 Pull Request
6. 等组员确认
7. 再合并到 main
```

记住：想避免直接合并，就不要在 `main` 分支上传。先建分支，再上传，再开 Pull Request。
