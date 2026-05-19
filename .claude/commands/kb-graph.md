# KB Graph — Build knowledge graph

Builds the relationship graph from the knowledge base.

## Usage

```
/kb-graph [options]
```

## Options

- `--full` — Full rebuild (ignore cache)
- `--incremental` — Only process changed files
- `--visualize` — Generate interactive HTML visualization

## Workflow

### Pass 1: Deterministic Extraction
- Extract all `[[wikilinks]]` from markdown files
- Build EXTRACTED edges (explicit relationships)

### Pass 2: LLM Inference
- Analyze pairs of related scholars
- Infer INFERRED edges with confidence scores
- Only include edges with confidence >= 0.7

### Pass 3: Community Detection
- Apply Louvain algorithm for community detection
- Identify academic circles, movements, institutions

## Output

### `graph/graph.json`
```json
{
  "nodes": [
    {"id": "abbottj", "type": "entity", "community": 1}
  ],
  "edges": [
    {"source": "abbottj", "target": "barrjh", "type": "EXTRACTED", "weight": 1.0},
    {"source": "abbottj", "target": "smith-college", "type": "INFERRED", "confidence": 0.85}
  ]
}
```

### `graph/graph.html`
- Interactive vis.js visualization
- Color-coded by type and community
- Click to navigate

## Edge Types

| Type | Source | Confidence |
|------|--------|------------|
| EXTRACTED | Explicit [[wikilinks]] | 1.0 |
| INFERRED | LLM semantic analysis | 0.0-1.0 |
| AMBIGUOUS | Low-confidence inference | < 0.7 (not written) |
