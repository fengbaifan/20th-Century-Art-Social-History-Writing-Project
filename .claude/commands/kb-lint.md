# KB Lint — Quality checks on knowledge base

Runs semantic quality checks on the knowledge base using LLM analysis.

## Usage

```
/kb-lint [options]
```

## Options

- `--fix` — Automatically fix issues where possible
- `--category <name>` — Run only specific checks

## Check Categories

### Structural (Free - no LLM)
- Empty files
- Missing frontmatter
- Index synchronization
- Broken wikilinks

### Semantic (Uses LLM)
- Orphan pages (no inbound links)
- Contradictions between sources
- Stub pages (too short, no content)
- Missing context (unexplained claims)

### Content Quality
- Factual consistency
- Citation completeness
- Link density

## Output

```
## Lint Report

### Issues Found
| Severity | File | Issue | Fix |
|----------|------|-------|-----|
| ERROR | abbottj.md | Broken link [[barrjh]] | Create or rename |
| WARN | smith-college.md | Stub page (< 100 words) | Expand content |

### Summary
- 2 errors
- 5 warnings
- 1 suggestion
```

## Integration

Run after `/kb-ingest` to verify quality before committing.