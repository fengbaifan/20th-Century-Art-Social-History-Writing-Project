---
name: kb-heal
description: 自愈修复 / Self-healing. 用于修复断链、创建缺失页面或自动修复链接路径。触发词: "heal", "修复", "/kb-heal"
---

# KB-Heal / 自愈修复

自动修复断链并创建缺失学者页面。

Auto-repair broken links and create missing scholar stubs.

## 使用 / Usage

```bash
python .processing/scripts/heal.py
```

## 修复动作 / Healing Actions

### 1. 存根创建 / Stub Creation
对于指向不存在页面的 `[[wikilinks]]`：
- 在 `knowledge-base/` 创建最小存根页面
- 包含 frontmatter: `name`, `title`, `birth: null`
- 标记 `enriched: false` 待后续富化

### 2. 链接路径修复 / Link Path Fixes
修复格式错误的链接如 `[[knowledge-base\file.md]]`：
- 从路径提取 shortcode
- 重写为干净的 `[[shortcode]]` 格式

### 3. 相似页面检测 / Similar Page Detection
对于可能是拼写错误的断链：
- 提供相似的现有页面名建议
- 不自动应用（需确认）

## 输出格式 / Output

```
[INFO] Found X broken links
[INFO] Creating stub: shortcode
[INFO] Fixed link: file.md -> shortcode
[SUCCESS] Healing complete:
  - Created N stub pages
  - Fixed M broken links
```

## 安全 / Safety

- 永不删除现有内容
- 仅创建新存根文件
- 保留所有现有页面