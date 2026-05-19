---
name: kb-health
description: 健康检查 / Health check. 用于验证学者页面、检查断链或验证 frontmatter。触发词: "health", "检查", "/kb-health"
---

# KB-Health / 健康检查

零 LLM 调用的结构完整性检查。

Zero-LLM structural integrity checks for the knowledge base.

## 使用 / Usage

```bash
python .processing/scripts/health.py
```

## 检查项 / Checks

| 检查 / Check | 说明 / Description |
|------------|------------------|
| 空文件 / Empty Files | 零字节或空 Markdown 文件 |
| Frontmatter | 缺少必需字段 (name, title, birth) |
| 断链 / Broken Links | 缺失 `[[wikilinks]]` 目标 |
| 索引同步 / Index Sync | 页面与 index.md 不一致 |

## 输出格式 / Output

```
[INFO] Health Report
[ERROR] FILE | ISSUE
[WARN] FILE | ISSUE
```

## 退出码 / Exit Codes

| 代码 | 含义 |
|------|------|
| 0 | 无错误 |
| 1 | 有错误（不影响运行）|

## 性能 / Performance

~2-5 秒检查 2500+ 页面，无 LLM 调用。