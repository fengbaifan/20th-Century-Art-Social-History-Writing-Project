---
name: user-feedback-2026-05-18
title: "User Feedback: System Architecture Review 2026-05-18"
date: 2026-05-18
type: feedback
---

# User Feedback: System Architecture Review

## Source Data Structure (Final - 2026-05-18)
- `RwaFiles/mid-data/` - Primary JSON source (2508 files) ← 主要数据源
- `RwaFiles/Processing/` - Separated JSON records
- `RwaFiles/RawFiles/` - Original files (reference)

## Final File Structure (2026-05-18)
```
/
├── RwaFiles/               # Source data
├── knowledge-base/         # Scholar pages (2494)
├── graph/                  # Visualization
├── plug-ins/              # External tools (NEW)
│   └── opencli-local/    # OpenCLI browser automation
├── .processing/            # Processing artifacts
│   ├── scripts/           # Pipeline executors
│   │   ├── ingest.py
│   │   ├── health.py
│   │   ├── heal.py
│   │   └── build_graph.py
│   └── enrichment-cache/  # Wikipedia cache
├── .claude/              # Claude Code config
│   ├── skills/          # KB skills
│   ├── commands/        # Slash commands
│   └── hooks/          # Git hooks
└── .remember/          # User feedback & improvements
```

## Schema v2 Requirements (from user)
1. Bilingual fields (Chinese/English) ✅
2. Personal bibliography (scholar's own books)
3. Related research list (from Wikipedia)

## System Improvements Log

### 2026-05-18 Session
- [x] Fixed O(n²) all_records caching → now cached in .processing/all_records.json
- [x] Improved bibliography parsing
- [x] Deduplicated institutions (INSTITUTION_ALIASES)
- [x] Added --continue-on-error flag
- [x] Corrected source path to RwaFiles/mid-data
- [x] Moved hooks/ to .claude/
- [x] Updated CLAUDE.md architecture
- [x] Moved tools/ to .processing/scripts/
- [x] Fixed PROJECT_ROOT path calculation
- [x] Updated all skill files with new paths
- [x] Health check: 0 errors
- [x] Healing: Fixed 3 broken links
- [x] Cleaned redundant folders: .processing/.processing, empty graph/, knowledge-base/
- [x] Removed old skill empty references/scripts directories
- [x] Created plug-ins/ for opencli-local

## Field Audit & Fixes (2026-05-18)

### Bug Found: Subject Duplication
**Problem**: `ingest.py` subjects processing was adding duplicate entries when `translate()` returned the same string (no translation available).

**Root Cause** (ingest.py:352-353):
```python
subjects_seen.add(translate(s))   # If no translation, adds same string
subjects.append(translate(s))     # Creates duplicate!
```

**Fix Applied**:
```python
translated = translate(s)
if translated and translated != s:  # Only add if translation exists and differs
    subjects_seen.add(translated)
    subjects.append(translated)
```

### Translations Added
Added ~100+ subject term translations to TRANSLATIONS dict.

## Schema v2 Final (2026-05-18)

### Frontmatter 格式 (Final)
```yaml
---
full_name: "Karl Abraham"
title_zh: "卡尔·亚伯拉罕"  # 需通过 enrich 添加中文翻译
birth: 1877
death: 1925
country: Germany
country_zh: 德国
---
```

### 页面标识规则
- 使用**文件名**作为短码（如 `abraham_karl.md`）
- 不从 frontmatter 提取 `name` 字段
- 健康检查和图谱构建都使用文件名

### 短码格式
Title "Last, First" → `lastname_firstname_full`
- "Abell, Walter" → `abell_walter.md`
- "Abraham, Karl" → `abraham_karl.md`
- "Eastlake, Charles L." → `eastlake_charles_l.md`
- "Eastlake, Charles Lock, Sir" → `eastlake_charles_lock_sir.md` (唯一!)

### 已更新文件
- [x] ingest.py - frontmatter 格式
- [x] health.py - 使用 filename 作为标识
- [x] heal.py - 存根页格式
- [x] build_graph.py - 使用 full_name/title_zh
- [x] CLAUDE.md - 文档更新
- [x] kb-ingest SKILL.md - 文档更新

### 测试验证
```bash
✅ abraham_karl.md - full_name + title_zh 格式正确
```

### 待完成
- [ ] 全量重新摄入所有 2508 个学者
- [ ] Wikipedia enrichment via OpenCLI + LLM
- [ ] 添加中文姓名翻译到 TRANSLATIONS

## System Preferences

### Script Avoidance Preference
User wants to minimize script writing. Prefer:
- Using LLM reasoning to handle tasks
- Invoking existing skills
- Batch operations via efficient commands

### Real-time Update System (Pending)
- System should auto-update when source data changes
- Need change monitoring skills in .claude/skills/
- Watch RwaFiles/mid-data/ for file changes
- Trigger ingest pipeline on changes
- Log all changes to .remember/

## Pending Tasks
- [ ] Complete wikilinks update (batch replace old → new shortcodes)
- [ ] Run full batch re-ingest with --force
- [ ] Health check verification (target: 0 errors)
- [ ] Wikipedia enrichment for Chinese names and personal bibliography
- [ ] Build first graph
- [ ] Real-time update system with change monitoring skills

## Real-time Update System (User Requirement)
- System should auto-update when source data changes
- Need change monitoring skills in .claude/skills/
- Watch RwaFiles/mid-data/ for file changes
- Trigger ingest pipeline on changes
- Log all changes to .remember/

## Documentation (2026-05-18 Update)
- [x] Created README.md (bilingual, 136 lines)
- [x] Updated CLAUDE.md (progressive disclosure, 136 lines)
- [x] Updated all SKILL.md files (bilingual, all under 100 lines)

### Line Counts
| File | Lines |
|------|-------|
| CLAUDE.md | 136 |
| README.md | 136 |
| kb-ingest | 85 |
| kb-health | 43 |
| kb-heal | 50 |
| kb-graph | 59 |

## Memory System
User wants all feedback and improvements logged to .remember/ folder.
Each session should create a dated file in .remember/