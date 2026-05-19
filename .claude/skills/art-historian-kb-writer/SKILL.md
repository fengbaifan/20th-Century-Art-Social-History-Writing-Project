---
name: art-historian-kb-writer
description: "Generates Markdown documents from enriched art historian JSON records with YAML frontmatter and bidirectional wiki-style links. Use when converting processed scholar data into final knowledge base output."
---

# Art Historian Writer — Markdown Generation

Generates formatted Markdown documents with YAML frontmatter and bidirectional links.

## Output Location

```
knowledge-base/{shortcode}.md
```

Example: `knowledge-base/abbottj.md`

---

## Document Template

```markdown
---
name: {shortcode}
title: "{Full Name}"
birth: {Birth Year}
death: {Death Year}
country: {Home Country}
institutions:
{INSTITUTIONS}
subjects:
{SUBJECTS}
enriched: {true|false}
sources:
{ENRICHMENT_SOURCES}
links:
{LINKS}
---

# {Full Name}

**{Birth Year}–{Death Year}** | {Home Country}

{OPTIONAL_IMAGE}

## Biography

{OVERVIEW}

## Academic Contributions

{EXTRACTED_FROM_ENRICHMENT}

## Selected Bibliography

{BIBLIOGRAPHY}

## Archives

{ARCHIVES}

## Related Scholars

{LINKED_SCHOLARS}

---

*Generated: {timestamp} | Source: {source_files}*
```

---

## Frontmatter Schema

```yaml
name: abbottj              # shortcode (filename stem)
title: "Abbott, Jere"     # Full name as title
birth: 1897               # Integer or null
death: 1982               # Integer or null
country: United States    # Home country
institutions:            # Array of institution names
  - Museum of Modern Art
  - Smith College
subjects:                # Array of subject areas
  - American Art
  - Modernism
enriched: true           # Whether Wikipedia/Wikidata data added
sources:                 # URLs of enrichment sources
  - https://en.wikipedia.org/wiki/Jere_Abbott
links:                   # Bidirectional links to other scholars
  - barrjh (institutional, 0.9)
  - smith-college (institutional)
```

---

## Link Formatting

### Scholar Links

```markdown
- [[barrjh]] — Colleague at MoMA
- [[smith-college]] — Institutional affiliation
```

### Tag Links

```markdown
- [[american-art]] — Subject area
- [[modernism]] — Subject area
```

---

## Processing Steps

### Step 1: Read Enriched Data

```bash
# Read original JSON
JSON=$(cat 01-RwaFiles/art_historians_json/{shortcode}.json)

# Read enrichment cache (if exists)
ENRICH=$(cat .processing/enrichment-cache/{shortcode}.json 2>/dev/null || echo '{}')

# Read link graph
LINKS=$(grep "^${shortcode}," .processing/link-graph.json || echo '')
```

### Step 2: Parse Fields

```bash
# Extract using jq
FULL_NAME=$(echo "$JSON" | jq -r '.Full Name')
BIRTH=$(echo "$JSON" | jq -r '.Birth Year')
DEATH=$(echo "$JSON" | jq -r '.Death Year')
OVERVIEW=$(echo "$JSON" | jq -r '.Overview' | sed 's/<[^>]*>//g')  # Strip HTML
```

### Step 3: Format Links

```bash
# Convert link graph entries to Markdown
for link in $LINKS; do
    TARGET=$(echo "$link" | cut -d, -f2)
    TYPE=$(echo "$link" | cut -d, -f3)
    echo "- [[$TARGET]] ($TYPE)"
done
```

### Step 4: Write Output

```bash
cat > "knowledge-base/${shortcode}.md" << 'EOF'
---
name: {shortcode}
...
---
# {Full Name}
...
EOF
```

---

## Image Handling

If enrichment provides an image:

```markdown
![{Name}]({image_url})
*{Name}. Source: Wikipedia.*
```

Images are optional — don't block if unavailable.

---

## Batch Writing

```bash
# Write all scholars
./write-all.sh

# Write single scholar
./write.sh --scholar abbottj

# Write with force (overwrite existing)
./write.sh --scholar abbottj --force
```

---

## Verification

After writing, verify:

1. **Frontmatter valid YAML** — `yaml-validate knowledge-base/abbottj.md`
2. **Links resolve** — All `[[shortcode]]` references exist
3. **No HTML remnants** — Strip all `<a>`, `<em>`, etc.
4. **UTF-8 encoding** — Ensure proper character handling

---

## Incremental Mode

Only rewrite if:
- Source JSON changed (compare hash)
- Enrichment data updated
- Link graph changed

```bash
# Check if rewrite needed
if [ "$JSON_HASH" != "$(cat .processing/hash/${shortcode}.json 2>/dev/null)" ]; then
    ./write.sh --scholar "$shortcode"
    echo "$JSON_HASH" > .processing/hash/${shortcode}.json
fi
```
