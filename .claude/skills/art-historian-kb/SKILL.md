---
name: art-historian-kb
description: "Art Historian Knowledge Base Pipeline — Orchestrates conversion of JSON records into enriched Markdown with bidirectional links. Use when working with art_historians_json data, building knowledge bases, or enriching biographical records. Triggers on JSON file changes or manual command."
---

# Art Historian Knowledge Base — Pipeline Orchestrator

This skill orchestrates the full pipeline for building an art historian knowledge base by delegating to specialized skills.

## Pipeline Stages

```
parse → enrich → link → write
```

| Stage | Skill | Purpose |
|-------|-------|---------|
| Enrich | `art-historian-kb-enricher` | OpenCLI Wikipedia/Wikidata enrichment |
| Link | `art-historian-kb-linker` | Bidirectional link computation |
| Write | `art-historian-kb-writer` | Markdown generation |

## Data Locations

| Type | Path |
|------|------|
| Source JSON | `01-RwaFiles/art_historians_json/` |
| Output MD | `knowledge-base/` |
| Cache | `.processing/` |

## Usage

### Process Single Scholar

```
Use art-historian-kb-enricher to enrich the record
Use art-historian-kb-linker to compute links
Use art-historian-kb-writer to generate Markdown
```

### Process All Scholars

Run in sequence:
1. `art-historian-kb-enricher` — Enrich all records
2. `art-historian-kb-linker` — Compute all links
3. `art-historian-kb-writer` — Generate all Markdown

### Incremental Processing

Only process records that have changed since last run.

## State Files

| File | Purpose |
|------|---------|
| `.processing/state.json` | Overall pipeline state |
| `.processing/enrichment-cache/` | Cached enrichment results |
| `.processing/link-graph.json` | Pre-computed link relationships |

## Exit States

- `0` — Success
- `1` — Partial failure (some files skipped)
- `2` — Full failure (check logs)
