# Skills 项目规范

这个仓库维护可复用的 CLI coding agent skills。每个 skill 独立放在一个目录中，包含 `SKILL.md` 和必要的支撑文档、脚本。

## SKILL.md 行数约束

**硬限制：SKILL.md 不得超过 500 行。**
**推荐：保持在 300 行以内。**

超出时的处理方式：

- 详细协议、工作流步骤、扩展规则 → 移入 `references/` 目录，在 SKILL.md 中用一行链接引用。
- 文档模板 → 移入 `assets/templates/`。
- 脚本逻辑 → 移入 `scripts/`。
- SKILL.md 只保留激活条件、核心规则、命令入口和对外部文件的引用，不承载完整流程细节。

创建或修改 SKILL.md 后，确认行数：

```sh
wc -l <skill-dir>/SKILL.md
```

## SKILL.md 必须保留的内容

以下内容必须直接写在 SKILL.md 中，不得以「瘦身」为由移到 `references/` 或其他文件：

- **激活条件**：触发词、opt-in 规则、activation guard。
- **核心行为规则**：命令遵从约束、安全边界、不可绕过的强制规则（如 document-first、phase gate、command compliance）。
- **命令入口定义**：用户可用的所有命令及其简要说明。
- **模式与分支**：one-shot vs persistent、workflow 类型等直接影响行为走向的选择规则。

判断标准：如果某条规则在每次 skill 激活时都需要生效，它就属于 SKILL.md 的内容。只有「详细步骤」「扩展协议」「文档模板」才适合移到 `references/`。

## 目录结构约定

```text
<skill-name>/
├── SKILL.md          ← 入口（≤500 行，推荐 ≤300 行）
├── references/       ← 详细工作流、协议、边界规则
├── assets/templates/ ← 文档模板
└── scripts/          ← 辅助脚本
```
