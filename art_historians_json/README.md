# 艺术史学家词典数据集（JSON格式）

## 概述

本文件夹包含从 `Dictionary_Art_Historians.csv` 转换而来的 **20世纪艺术史学家词典** 数据集，以JSON格式存储。

## 文件说明

### 数据文件（*.json）
- **数量**: 2507 个条目文件
- **命名规则**: 使用每位艺术史学家的URL标识符命名（如 `abbottj.json`, `abellw.json` 等）
- **数据结构**: 每个文件包含该艺术史学家的完整信息，包括：
  - 基本信息（姓名、性别、国籍）
  - 生卒年份和地点
  - 研究领域
  - 职业履历
  - 机构
  - 简介概述
  - 参考文献
  - 来源档案
  - 贡献者
  - 最后修改日期

### 索引文件（index.json）
- **用途**: 提供所有条目的快速索引
- **内容**: 包含文件名、姓名、标题、URL、生卒年份、国籍、性别、研究领域和简介摘要
- **格式**: JSON数组，便于程序化查询和搜索

## 使用方法

### 查找特定艺术家
1. 打开 `index.json` 文件
2. 搜索艺术家的姓名或研究领域
3. 使用找到的文件名直接打开对应的 JSON 文件

### 程序化访问
```python
import json
import os

# 读取索引
with open('index.json', 'r', encoding='utf-8') as f:
    index = json.load(f)

# 查找特定艺术家
for entry in index:
    if 'Picasso' in entry.get('overview', ''):
        print(f"Found: {entry['filename']}")

# 读取单个艺术家文件
with open('abbottj.json', 'r', encoding='utf-8') as f:
    artist_data = json.load(f)
    print(artist_data['Full Name'])
```

## 数据来源

- **原始文件**: Dictionary_Art_Historians.csv
- **来源**: 20世纪艺术史社会学写作项目
- **记录数**: 2507 条

## 字段说明

| 字段 | 说明 |
|------|------|
| WordPress Unique ID | WordPress系统唯一标识符 |
| Drupal Unique ID | Drupal系统唯一标识符 |
| URL | 网页URL路径 |
| Directory | 目录分组标识 |
| Title | 标题 |
| Full Name | 完整姓名 |
| Other Names | 其他姓名 |
| Birth/Death Year | 生卒年份 |
| Place Born/Died | 生卒地点 |
| Home Country | 所属国家 |
| Gender | 性别 |
| Subject Area | 研究领域 |
| Career | 职业 |
| Institution | 所属机构 |
| Overview | 简介 |
| Selected Bibliography | 精选书目 |
| Sources | 来源 |
| Archives | 档案 |
| Contributors | 贡献者 |
| Notes | 备注 |
| Date Last Modified | 最后修改日期 |

## 生成日期

2026-05-17

## 相关文件

- **转换脚本**: `convert_csv_to_json.py` - 用于将CSV转换为JSON格式
- **索引脚本**: `create_index.py` - 用于生成索引文件
- **清理脚本**: `cleanup_and_index.py` - 用于清理和重建索引

## 许可证

请参阅项目主目录的许可证文件。
