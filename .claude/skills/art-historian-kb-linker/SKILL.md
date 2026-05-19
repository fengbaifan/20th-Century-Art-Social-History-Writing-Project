---
name: art-historian-kb-linker
description: "Computes bidirectional links between art historians based on institutional, temporal, subject, and bibliographic relationships. Generates link graph for knowledge base cross-references."
---

# Art Historian Linker — Relationship Computation

Computes bidirectional links between art historians based on multiple relationship signals.

## Link Types & Weights

| Type | Weight | Source | Example |
|------|--------|--------|---------|
| Institutional | 0.8 | Same affiliation | Harvard, MoMA |
| Temporal | 0.6 | Birth/death ±10 years | Both born 1890s |
| Subject | 0.7 | Same subject area | "American Art" |
| Bibliographic | 0.9 | Same source cited | Both cite Barr 2002 |
| Textual | 0.4 | Name in Overview | "met Alfred Barr" |

---

## Computation Algorithm

### Phase 1: Extract Relationship Signals

For each record, extract:

```bash
# Pseudo-code
for each scholar:
  institutions = parse_institutions(overview + archives)
  time_period = (birth_year - 5, death_year + 5)
  subjects = parse_subjects(subject_area)
  sources = parse_bibliography(sources)
  mentions = extract_name_mentions(overview)
```

### Phase 2: Build Candidate Pairs

```bash
# For each pair of scholars
for each (a, b) in scholars:
  score = 0
  if shared_institution(a, b): score += 0.8
  if temporal_overlap(a, b): score += 0.6
  if shared_subject(a, b): score += 0.7
  if shared_source(a, b): score += 0.9
  if mentions(b, a.name) or mentions(a, b.name): score += 0.4

  if score >= THRESHOLD (0.5):
    add_link(a, b, score)
```

### Phase 3: Deduplicate & Validate

- Remove duplicate links (A→B same as B→A)
- Keep highest score if duplicate
- Validate both scholars exist

---

## Link Graph Storage

```bash
# Store in .processing/link-graph.json
{
  "computed_at": "2026-05-18T12:00:00Z",
  "total_scholars": 2509,
  "total_links": 8420,
  "links": [
    {
      "from": "abbottj",
      "to": "barrjh",
      "type": "institutional",
      "score": 0.9,
      "reason": "Both at Museum of Modern Art"
    },
    ...
  ]
}
```

---

## Incremental Updates

When a single record changes:

1. Remove old links involving that scholar
2. Recompute only those links
3. Merge back into graph

```bash
# Update links for changed scholar
./update-links.sh --scholar abbottj
```

---

## Threshold Tuning

| Threshold | Expected Links | Coverage |
|-----------|----------------|----------|
| 0.3 | High | >90% scholars linked |
| 0.5 | Medium | ~80% scholars linked |
| 0.7 | Low | ~60% scholars linked |

**Default**: 0.5 — balances coverage with quality

---

## Usage

```bash
# Compute all links (full rebuild)
./compute-links.sh --all

# Update single scholar
./compute-links.sh --scholar abbottj

# With force (ignore cache)
./compute-links.sh --all --force
```

---

## Output

Links are stored in `.processing/link-graph.json`.

The `art-historian-kb/writer` skill reads this graph when generating Markdown.

---

## Performance

- **2500 scholars** = ~3M pairs
- **O(n²)** naive, optimize with indexing
- **Target**: <5 minutes for full graph
- **Incremental**: <30 seconds per scholar
