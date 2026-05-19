---
name: art-historian-kb-enricher
description: "Enriches art historian JSON records with Wikipedia and Wikidata data via OpenCLI browser automation. Use when adding biographical data from web sources to existing scholar records."
---

# Art Historian Enricher — Web Data Extraction

Extracts additional biographical data from Wikipedia and Wikidata using OpenCLI browser automation.

## Enrichment Sources

1. **Wikipedia** — Full biography, images, infobox data
2. **Wikidata** — Structured data, related figures, external links

## Why Browser Over API?

- **Forced extraction**: Bypasses Wikipedia API rate limits
- **Complete data**: Gets full biography, images, infobox
- **More sources**: Can scrape academic pages, museum sites
- **Self-repair**: Uses `opencli-autofix` skill if DOM changes

---

## Workflow

### Step 1: Check Cache

```bash
CACHE=".processing/enrichment-cache/{shortcode}.json"
if [ -f "$CACHE" ]; then
    cat "$CACHE"
    exit 0
fi
```

### Step 2: Construct URL

From JSON fields:
- `Full Name` → `Title` formatted for Wikipedia URL
- Example: "Alfred H. Barr, Jr." → "Alfred_H._Barr_Jr."

```bash
NAME=$(echo "$FULL_NAME" | sed 's/,.*//' | tr ' ' '_' | tr -d '.')
WIKI_URL="https://en.wikipedia.org/wiki/$NAME"
```

### Step 3: Fetch via OpenCLI Browser

```bash
# Open Wikipedia page
opencli browser open "$WIKI_URL"
opencli browser state

# Extract biography content
opencli browser extract --selector ".mw-parser-output"

# Get infobox data
opencli browser extract --selector ".infobox"
```

### Step 4: Extract Data Points

Extract these fields if available:
- `biography` — Full biography text
- `image` — Main image URL
- `born` — Birth date/place
- `died` — Death date/place
- `fields` — Fields of study
- `institutions` — Affiliations
- `publications` — Notable works
- `externalLinks` — External URLs

### Step 5: Cache Result

```bash
mkdir -p .processing/enrichment-cache
cat > ".processing/enrichment-cache/{shortcode}.json" << 'EOF'
{
  "shortcode": "{shortcode}",
  "enriched_at": "{timestamp}",
  "sources": {
    "wikipedia": "{url}",
    "wikidata": "{url}"
  },
  "data": {
    ...
  }
}
EOF
```

---

## Rate Limiting

- **2-second delay** between requests
- **3 retry attempts** with exponential backoff
- **Skip if persistent failure** — don't block pipeline

---

## Error Handling

| Error | Response |
|-------|----------|
| Page not found | Try search, then skip |
| Timeout | Retry 3x with backoff |
| DOM changed | Trigger `opencli-autofix` skill |
| Rate limited | Wait 30s, retry |

---

## Integration

This skill is loaded by `art-historian-kb` orchestrator. Direct usage:

```bash
# Enrich single record
./enrich.sh --file 01-RwaFiles/art_historians_json/abbottj.json

# Enrich with force (skip cache)
./enrich.sh --file abbottj.json --force
```

---

## Output Schema

```json
{
  "shortcode": "abbottj",
  "enriched_at": "2026-05-18T12:00:00Z",
  "sources": {
    "wikipedia": "https://en.wikipedia.org/wiki/Jere_Abbott",
    "wikidata": null
  },
  "data": {
    "biography": "Americanist art historian...",
    "image": "https://upload.wikimedia.org/...",
    "born": "1897, Dexter, Maine",
    "died": "1982, Dexter, Maine",
    "institutions": ["Museum of Modern Art", "Smith College"],
    "publications": ["Lautrec-Redon (1931)"],
    "externalLinks": ["https://asteria.fivecolleges.edu/..."]
  },
  "status": "success"
}
```
