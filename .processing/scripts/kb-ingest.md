# KB Ingest — Process source documents into knowledge base

Ingests art historian records from `01-RwaFiles/art_historians_json/` into the knowledge base.

## Usage

```
/kb-ingest [options]
```

## Options

- `--all` — Process all JSON records
- `--file <shortcode>` — Process single record (e.g., `abbottj`)
- `--force` — Force reprocess even if up to date

## Workflow

1. **Parse** — Read JSON from `01-RwaFiles/art_historians_json/`
2. **Enrich** — Fetch from Wikipedia/Wikidata via OpenCLI (if not cached)
3. **Link** — Compute relationships with other scholars
4. **Write** — Generate Markdown to `knowledge-base/`
5. **Index** — Update `knowledge-base/index.md`
6. **Log** — Append entry to `knowledge-base/log.md`

## Running Directly

```bash
python tools/ingest.py --all
python tools/ingest.py --file abbottj
```

## Output

- `knowledge-base/{shortcode}.md` — Individual scholar page
- `knowledge-base/index.md` — Updated catalog
- `knowledge-base/log.md` — Chronological record

## Self-Healing

After ingest, run `python tools/heal.py` to:
- Create missing entity pages for mentioned scholars
- Fix broken wikilinks
- Generate stub pages for orphan references
