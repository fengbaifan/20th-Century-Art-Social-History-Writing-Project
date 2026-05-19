# KB Query — Query the knowledge base

Queries the art historian knowledge base and synthesizes answers.

## Usage

```
/kb-query <question>
```

## Examples

```
/kb-query Who were the key figures in American modernist art history?
/kb-query What institutions did Jere Abbott and Alfred Barr work at together?
/kb-query Show me art historians who studied at Harvard
```

## Workflow

1. **Index Analysis** — Find relevant pages via graph and keyword matching
2. **Graph Expansion** — Include neighboring nodes for context
3. **LLM Synthesis** — Generate answer with [[wikilink]] citations
4. **Save** — Optionally save to `wiki/syntheses/`

## Output Format

```
## Answer

[Synthesized response with citations]

### Sources
- [[scholar-name]] — relevance explanation
```

## Graph Integration

Uses `graph/graph.json` to expand context:
- Direct links (explicit relationships)
- Inferred links (semantic relationships, confidence >= 0.7)
- Community detection (same academic circles)
