# Help Output

When `/spec -h` or `/spec-mode -h` is triggered, output exactly this block and stop:

```text
spec-mode 命令速查
══════════════════════════════════════════════════════

工作流
  /spec <需求描述或文件路径>            一次性规格工作流（需求→设计→任务）
  /spec-mode <需求描述或文件路径>       同 /spec
  /spec --persist <需求>               启动持久会话模式
  /spec-continue [spec名或目录]         从已配置 spec 根目录恢复或切换当前会话
  /spec-status                          显示当前会话状态
  /spec-end                             结束当前会话（不删除文档）

Obsidian / 根目录配置
  /spec --set-vault <vault路径>         设置 Obsidian vault（spec 存入 vault/spec-in/<os>-<user>/specs）
  /spec --set-root <目录>               直接设置 spec 文档根目录（完全自定义路径）
  /spec --detect-vault                  检测已安装的 Obsidian vault
  /spec --vault-status                  显示当前 vault / spec root 配置

帮助
  /spec -h                              显示本帮助

文档根目录解析顺序（高→低优先级）
  1. /spec --root 参数
  2. SPEC_MODE_ROOT 环境变量
  3. ~/.config/spec-mode/config.json → obsidianRoot（首次检测时自动写入，或手动 --set-vault/--set-root）
  4. 自动检测 Obsidian vault → <vault>/spec-in/<os>-<user>/specs（同时写入 config.json）
  5. <当前项目>/specs
  6. ~/new project/specs（兜底）

/spec-continue 限制
  只扫描 ~/.config/spec-mode/config.json 中记录的 spec 根目录。
  不扫描当前项目 specs 或 ~/new project/specs 兜底目录。
  加载后只显示当前状态并等待用户输入，不直接开始任务或验收验证。

spec 文档结构
  <root>/<需求名>/requirements.md          需求与验收标准
  <root>/<需求名>/bugfix.md                缺陷规格（替代 requirements.md）
  <root>/<需求名>/design.md                技术设计
  <root>/<需求名>/tasks.md                 任务列表与执行状态
  <root>/<需求名>/acceptance-checklist.md  验收操作清单
  <root>/.active-spec-mode.json            跨会话活跃指针

持久会话状态行格式
  ─── spec-mode ─── spec: <slug> | session: <id> | phase: <phase> | /spec-end 退出
```
