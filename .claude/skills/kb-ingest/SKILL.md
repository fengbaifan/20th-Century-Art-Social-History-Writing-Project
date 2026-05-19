---
name: kb-ingest
description: 双语摄取管道 / Bilingual ingestion pipeline. 用于处理 JSON 记录生成 Markdown 页面、批量导入或更新学者条目。触发词: "ingest", "处理", "/kb-ingest"
---

# KB-Ingest / 知识库摄取管道

将 JSON 记录转换为双语富化 Markdown 页面。

Converts JSON records from `RwaFiles/mid-data/` into bilingual Markdown with frontmatter and wikilinks.

## 使用 / Usage

```bash
# 单个处理 / Single scholar (使用 JSON 文件名)
python .processing/scripts/ingest.py --file karl_abraham

# 批量处理 / All scholars
python .processing/scripts/ingest.py --all

# 强制重处理 / Force reprocess
python .processing/scripts/ingest.py --all --force

# 继续处理（忽略错误）/ Continue on error
python .processing/scripts/ingest.py --all --continue-on-error
```

## 管道阶段 / Pipeline Stages

1. **Parse** — 加载 JSON / Load JSON from `RwaFiles/mid-data/`
2. **Enrich** — 检查缓存，必要时获取 Wikipedia
3. **Link** — 计算双向链接
4. **Write** — 生成双语 Markdown
5. **Log** — 追加到 `knowledge-base/log.md`

## 数据源 / Source Data

| 字段 / Field | 说明 / Description |
|-------------|-------------------|
| Full Name | 学者全名 |
| Birth/Death Year | 出生/死亡年 |
| Country | 国家 |
| Subject Area | 研究领域 |
| Overview | 概述 |
| Bibliography | 参考文献 |
| Archives | 档案 |

## 输出 / Output

```
knowledge-base/
├── {shortcode}.md  # 学者页面 / Scholar page
├── index.md        # 索引目录 / Catalog
└── log.md          # 操作日志 / Operation log
```

## Schema v2 字段 / Fields

```yaml
---
full_name: "Jere Abbott"
title_zh: "杰雷·阿博特"
birth: 1897
death: 1982
country: United States
country_zh: 美国
subjects:
  - American (North American)
  - 美国（北美）
institutions:
  - name: Harvard University
    name_zh: 哈佛大学
---
```

**注意**: 页面标识使用文件名（如 `jere_abbott.md`），不从 frontmatter 提取。

## 链接计算权重 / Link Weights

| 类型 / Type | 权重 / Weight | 说明 / Description |
|------------|--------------|-------------------|
| Institutional | 0.8 | 共享机构 |
| Subject | 0.7 | 相同领域 |
| Temporal | 0.6 | 时间±10年 |
| Textual | 0.4 | 文本提及 |

阈值: score ≥ 0.5，最多 10 条链接