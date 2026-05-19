---
name: kb-opencli-verify
description: 使用 OpenCLI 浏览器自动化验证知识库输出 / Verify KB outputs using OpenCLI browser automation
trigger: verify, opencli, 验证, 自动化验证
---

# KB-OpenCLI-Verify / OpenCLI 自动化验证

使用 OpenCLI 浏览器自动化对知识库进行全面验证。

Comprehensive knowledge base verification using OpenCLI browser automation.

## 使用 / Usage

```bash
# 完整验证
python .processing/scripts/verify_opencli.py --all

# 仅验证 Wikipedia 链接
python .processing/scripts/verify_opencli.py --wikipedia

# 验证图谱可视化
python .processing/scripts/verify_opencli.py --graph

# 验证单个页面
python .processing/scripts/verify_opencli.py --file abraham_karl
```

## 验证项目 / Verification Items

### 1. Wikipedia 富化验证
- 检查学者页面的 Wikipedia 链接是否有效
- 验证 Wikipedia API 返回的数据完整性
- 对比富化前后的内容变化

### 2. 图谱可视化验证
- 打开 graph.html 验证渲染
- 检查节点数量是否与知识库同步
- 截图存档验证结果

### 3. 外部链接验证
- 检查双向链接 [[wikilinks]] 有效性
- 验证外部 URL 可访问性

### 4. 批量质量检查
- 运行 health.py 结构检查
- 检查 frontmatter 完整性
- 验证中英双语字段

## OpenCLI 集成 / OpenCLI Integration

```bash
# 检查 OpenCLI 状态
opencli doctor

# 列出可用命令
opencli list

# 验证 Wikipedia 页面
opencli google-scholar search "Karl Abraham" --format json
```

## 输出 / Output

```
[INFO] KB OpenCLI Verification
[INFO] ================================
[INFO] 1. Health Check...
[INFO] 2. Wikipedia Enrichment...
[INFO] 3. Graph Visualization...
[INFO] 4. External Links...
[SUCCESS] Verification complete: X issues found
```

## 安全特性 / Safety

- 只读操作，不修改任何文件
- 截图存档便于人工复核
- 详细日志便于调试
