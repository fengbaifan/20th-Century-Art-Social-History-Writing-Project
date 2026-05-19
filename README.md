# Art Historian Knowledge Base / 艺术史学家知识库

[Bilingual] English follows Chinese / 英文在中文之后

---

## 简介 / Introduction

本项目构建了一个自动化知识库系统，涵盖《艺术史学家词典》中约 2500 位艺术史学家的信息。系统采用 Claude Code + llm-wiki-agent 架构模式。

This project builds an automated knowledge base system for ~2500 art historians from the Dictionary of Art Historians. Built with Claude Code following the llm-wiki-agent architecture pattern.

## 目录结构 / Directory Structure

```
RwaFiles/                     # 源数据 / Source data
├── mid-data/               # 主数据源 (2508 JSON) / Primary source
├── Processing/             # 分离的记录 / Separated records
└── RawFiles/              # 原始文件参考 / Original reference

knowledge-base/               # 知识库 / Knowledge layer
├── index.md              # 索引目录 / Auto-catalog
├── log.md                # 操作日志 / Operation log
└── {shortcode}.md       # 学者页面 / Scholar pages

graph/                       # 关系图 / Relationship layer
├── graph.json             # 节点数据 / Node/edge data
└── graph.html             # 可视化 / Interactive viz

plug-ins/                    # 外部工具 / External tools
└── opencli-local/        # OpenCLI 浏览器自动化

.processing/                 # 处理缓存 / Processing artifacts
├── scripts/              # 执行脚本 / Pipeline scripts
│   ├── ingest.py        # 摄取管道
│   ├── health.py        # 健康检查
│   ├── heal.py          # 自愈修复
│   └── build_graph.py   # 图谱构建
└── enrichment-cache/    # 富化缓存

.claude/                     # Claude Code 配置
├── skills/              # Skills (渐进式披露)
├── commands/            # Slash 命令
└── hooks/              # Git 钩子
```

## 快速开始 / Quick Start

### 1. 查看系统状态 / Check System Status

```bash
# 健康检查 / Health check
python .processing/scripts/health.py

# 查看索引 / View index
cat knowledge-base/index.md
```

### 2. 更新知识库 / Update Knowledge Base

```bash
# 全部更新 / Full update
python .processing/scripts/ingest.py --all --force

# 单个更新 / Single scholar
python .processing/scripts/ingest.py --file abbottj
```

### 3. 修复问题 / Fix Issues

```bash
# 自愈修复 / Self-heal
python .processing/scripts/heal.py

# 构建图谱 / Build graph
python .processing/scripts/build_graph.py --full
```

## 核心功能 / Core Features

| 功能 / Feature | 实现 / Implementation |
|--------------|----------------------|
| 双向链接 / Bidirectional links | `[[wikilinks]]` 语法 |
| 自愈机制 / Self-healing | 自动创建缺失页面 |
| 健康检查 / Health checks | 零 LLM 调用 |
| 图谱可视化 / Graph visualization | vis.js 交互图谱 |
| 增量处理 / Incremental | SHA256 内容缓存 |

## Schema v2 / 数据模式

学者页面包含以下双语字段：

```yaml
---
name: abbottj
title: "Abbott, Jere"
title_zh: "雅培, 杰雷"
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

## 链接计算权重 / Link Computation Weights

| 类型 / Type | 权重 / Weight | 来源 / Source |
|------------|--------------|--------------|
| 机构共享 / Institutional | 0.8 | 同一大学/博物馆 |
| 领域相同 / Subject | 0.7 | 研究方向一致 |
| 时间相近 / Temporal | 0.6 | 出生年±10年 |
| 文本提及 / Textual | 0.4 | 名字出现在概述中 |

阈值: score ≥ 0.5，最多 10 条链接

## Skills / 技能说明

使用 `/kb-ingest`, `/kb-health`, `/kb-heal`, `/kb-graph` 调用对应技能。

详细文档见 `.claude/skills/*/SKILL.md`

## 参与贡献 / Contributing

1. 遵循现有代码结构
2. 更新日志记录到 `.remember/`
3. 运行健康检查确保无错误
4. 提交前测试变更

## 许可证 / License

MIT