---
name: kb-graph
description: 图谱构建 / Graph builder. 用于构建关系图谱、可视化学者网络或提取社区聚类。触发词: "graph", "图谱", "/kb-graph"
---

# KB-Graph / 知识图谱构建

从学者关系构建知识图谱并可视化。

Builds knowledge graph from scholar relationships with visualization.

## 使用 / Usage

```bash
# 完整构建（含社区检测）
python .processing/scripts/build_graph.py --full

# 仅提取显式链接
python .processing/scripts/build_graph.py --extract

# 交互式可视化
open graph/graph.html
```

## 图谱构建（3 阶段）/ Construction (3 Passes)

### Pass 1: EXTRACTED 边
从所有学者页面提取显式 `[[wikilinks]]`：
- 源 → 目标关系
- 边类型: "explicit"
- 置信度: 1.0

### Pass 2: INFERRED 边
LLM 推断的语义关系：
- 共享方法论
- 艺术影响
- 学术传承
- 仅置信度 ≥ 0.7 的边

### Pass 3: 社区检测
Louvain 算法聚类：
- 识别图谱中的社区
- 分组相关学者
- 生成含节点/边数据的 `graph.json`

## 输出文件 / Output Files

| 文件 | 内容 |
|------|------|
| `graph/graph.json` | D3.js 节点/边数据 |
| `graph/graph.html` | 交互式可视化 |
| `graph/communities.json` | 检测到的社区 |

## 可视化功能 / Visualization Features

- 力导向布局 / Force-directed layout
- 缩放平移 / Zoom and pan
- 节点悬停详情 / Node hover details
- 社区颜色编码 / Community color coding
- 链接强度可视化 / Link strength visualization