# Art Historian Knowledge Base / 艺术史学家知识库

## 概览 / Overview

Automated knowledge base for ~2500 art historians from the Dictionary of Art Historians.
Built with Claude Code + llm-wiki-agent architecture.

本知识库系统用于管理艺术史学家信息，采用 Claude Code 构建，支持双语页面和自动关系推理。

**Skills 入口**: `/kb-ingest`, `/kb-health`, `/kb-heal`, `/kb-graph`

---

## 目录结构 / Directory Structure

```
RwaFiles/                     # 源数据 (immutable)
├── mid-data/               # 主数据源 (2508 JSON)
├── Processing/             # 分离的记录
└── RawFiles/              # 原始文件参考

knowledge-base/               # 知识库
├── index.md              # 索引 (双语)
├── log.md                # 操作日志
└── {shortcode}.md       # 学者页面 (双语)

graph/                       # 关系图
├── graph.json             # 节点/边数据
└── graph.html             # 可视化

plug-ins/                    # 外部工具
└── opencli-local/        # OpenCLI 浏览器自动化

.processing/                 # 处理 artifacts
├── scripts/              # 脚本
└── enrichment-cache/    # 富化缓存

.claude/                     # Claude Code 配置
├── skills/              # Skills (详情见各 SKILL.md)
├── commands/            # Slash 命令
└── hooks/              # Git hooks
```

---

## 快速命令 / Quick Commands

```bash
# 健康检查 / Health
python .processing/scripts/health.py

# 更新知识库 / Update KB
python .processing/scripts/ingest.py --all --force
python .processing/scripts/ingest.py --file abbottj

# 自愈修复 / Self-heal
python .processing/scripts/heal.py

# 构建图谱 / Build graph
python .processing/scripts/build_graph.py --full
```

---

## 核心功能 / Core Features

| 功能 / Feature | 实现 / Implementation |
|--------------|----------------------|
| 双向链接 / Bidirectional links | `[[wikilinks]]` 语法 |
| 自愈机制 / Self-healing | `heal.py` 自动创建缺失页面 |
| 健康检查 / Health checks | `health.py` (零 LLM) |
| 图谱可视化 / Graph | `graph.html` (vis.js) |
| 增量处理 / Incremental | SHA256 内容缓存 |

---

## Schema v2 / 数据模式

每个学者页面包含：
- **全名**: `full_name` (格式: "Karl Abraham")
- **中译**: `title_zh` (如 "卡尔·亚伯拉罕")
- **双语字段**: `country_zh`, `institutions.name_zh`
- **著作清单**: 个人著作 (需 Wikipedia 富化)
- **相关研究**: 参考文献列表

**Frontmatter 示例**:
```yaml
---
full_name: "Karl Abraham"
title_zh: "卡尔·亚伯拉罕"
birth: 1877
death: 1925
country: Germany
country_zh: 德国
---
```

**页面标识**: 使用文件名作为短码（如 `abraham_karl.md`），不从 frontmatter 提取。

---

## 短码命名规则 / Shortcode Naming Convention

**重要**: 短码基于 Title 字段，采用 "Lastname_Firstname" 格式。

| Title 字段 | 短码格式 | 示例 |
|------------|---------|------|
| "Abell, Walter" | lastname_firstname | `abell_walter.md` |
| "Abraham, Karl" | lastname_firstname | `abraham_karl.md` |
| "Eastlake, Charles L." | lastname_firstname | `eastlake_charles_l.md` |
| "Dinsmoor, William B., Jr." | lastname_firstname | `dinsmoor_william_b_jr.md` |

**禁止**: 不要使用 URL 缩写格式（如 `abrahamk`, `abellw`）

**单名处理**: "Filarete" 等单名直接使用原名作为短码

---

## 链接计算 / Link Computation

权重分配：

| 类型 / Type | 权重 / Weight | 来源 / Source |
|------------|--------------|--------------|
| 机构共享 / Institutional | 0.8 | 同一大学/博物馆 |
| 领域相同 / Subject | 0.7 | 研究方向一致 |
| 时间相近 / Temporal | 0.6 | 出生年±10年 |
| 文本提及 / Textual | 0.4 | 名字出现在概述 |

阈值: score ≥ 0.5，最多 10 条

详见 `.claude/skills/kb-ingest/SKILL.md`

---

## Skills / 技能

| Skill | 用途 / Purpose | 详情 / Details |
|-------|---------------|----------------|
| `kb-ingest` | 双语摄取管道 | `.claude/skills/kb-ingest/SKILL.md` |
| `kb-health` | 结构完整性检查 | `.claude/skills/kb-health/SKILL.md` |
| `kb-heal` | 断链自愈修复 | `.claude/skills/kb-heal/SKILL.md` |
| `kb-graph` | 知识图谱构建 | `.claude/skills/kb-graph/SKILL.md` |

---

## 进度 / Progress

- [x] 架构设计 (llm-wiki-agent)
- [x] 核心脚本 (ingest, health, heal, build_graph)
- [x] 知识库结构 (index.md, log.md)
- [x] Skills 创建
- [x] Schema v2: 双语字段
- [x] 测试完成 (2494 pages)
- [x] plug-ins/ 外部工具目录
- [ ] 实时更新监控
- [ ] Wikipedia 富化
- [ ] 构建首个图谱

---

## 参考 / References

- 详细架构: `README.md`
- 操作日志: `knowledge-base/log.md`
- Skills 详情: `.claude/skills/*/SKILL.md`
- 用户反馈: `.remember/user-feedback-*.md`