#!/usr/bin/env python3
"""
Art Historian Knowledge Base Pipeline
Orchestrates: parse → enrich → link → write
"""

import json
import os
import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

# Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
SOURCE_DIR = PROJECT_ROOT / "01-RwaFiles" / "art_historians_json"
OUTPUT_DIR = PROJECT_ROOT / "knowledge-base"
PROCESSING_DIR = PROJECT_ROOT / ".processing"
CACHE_DIR = PROCESSING_DIR / "enrichment-cache"


def log_info(msg: str):
    print(f"{BLUE}[INFO]{NC} {msg}")


def log_success(msg: str):
    print(f"{GREEN}[SUCCESS]{NC} {msg}")


def log_warn(msg: str):
    print(f"{YELLOW}[WARN]{NC} {msg}")


def log_error(msg: str):
    print(f"{RED}[ERROR]{NC} {msg}")


def stage_parse():
    print(f"{BLUE}[1/4]{NC} Parse")


def stage_enrich():
    print(f"{BLUE}[2/4]{NC} Enrich")


def stage_link():
    print(f"{BLUE}[3/4]{NC} Link")


def stage_write():
    print(f"{BLUE}[4/4]{NC} Write")


def init_dirs():
    """Initialize required directories."""
    for d in [OUTPUT_DIR, PROCESSING_DIR, CACHE_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def load_json(filepath: Path) -> Dict[str, Any]:
    """Load and parse JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath: Path, data: Dict[str, Any]):
    """Save data as JSON."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_record(shortcode: str) -> Dict[str, Any]:
    """Parse JSON record."""
    json_file = SOURCE_DIR / f"{shortcode}.json"

    if not json_file.exists():
        log_error(f"JSON file not found: {json_file}")
        raise FileNotFoundError(f"Source file not found: {json_file}")

    try:
        data = load_json(json_file)
        log_success(f"Parsed: {shortcode}")
        return data
    except json.JSONDecodeError as e:
        log_error(f"Invalid JSON in {json_file}: {e}")
        raise


def enrich_record(shortcode: str, json_data: Dict[str, Any], force: bool = False) -> Dict[str, Any]:
    """Enrich record via OpenCLI (simplified - actual implementation uses browser)."""
    cache_file = CACHE_DIR / f"{shortcode}.json"

    # Check cache
    if cache_file.exists() and not force:
        log_success(f"Using cached enrichment: {shortcode}")
        return load_json(cache_file)

    # Extract name
    name = json_data.get('Full Name') or json_data.get('Title', '')
    if not name:
        log_warn(f"No name found for: {shortcode}")
        return {}

    # Format for Wikipedia
    wiki_name = name.split(',')[0].strip().replace(' ', '_').rstrip('_')
    wiki_url = f"https://en.wikipedia.org/wiki/{wiki_name}"

    # Create enrichment result
    enrichment = {
        "shortcode": shortcode,
        "enriched_at": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "wikipedia": wiki_url
        },
        "data": {}
    }

    # Save cache
    save_json(cache_file, enrichment)

    log_success(f"Enriched: {shortcode}")
    return enrichment


def compute_links(shortcode: str, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compute links for a scholar (simplified)."""
    # Full implementation in compute-links.sh
    return []


def write_markdown(shortcode: str, json_data: Dict[str, Any],
                   enrichment: Dict[str, Any] = None, links: List = None):
    """Write Markdown output."""

    # Extract fields
    full_name = json_data.get('Full Name') or json_data.get('Title', 'Unknown')
    birth = json_data.get('Birth Year', '')
    death = json_data.get('Death Year', '')
    country = json_data.get('Home Country', '')
    subject_area = json_data.get('Subject Area', '')
    overview = strip_html(json_data.get('Overview', ''))
    bibliography = strip_html(json_data.get('Selected Bibliography', ''))
    archives = strip_html(json_data.get('Archives', ''))
    url = json_data.get('URL', '')

    # Parse subjects
    subjects = []
    if subject_area:
        for s in subject_area.split('|'):
            s = s.strip().strip('"')
            if s:
                subjects.append(f"  - {s}")

    # Format subjects block
    subjects_block = '\n'.join(subjects) if subjects else "  []"

    # Build frontmatter
    frontmatter = f"""---
name: {shortcode}
title: "{full_name.replace('"', '\\"')}"
birth: {birth if birth else 'null'}
death: {death if death else 'null'}
country: {country if country else 'null'}
subjects:
{subjects_block}
enriched: {'true' if enrichment else 'false'}
sources:
  - {url if url else 'local'}
links: []
---

# {full_name}

**{birth if birth else '?'}**–**{death if death else '?'}** | {country if country else 'Unknown'}

## Biography

{overview if overview else 'No biography available.'}

## Selected Bibliography

{bibliography if bibliography else 'No bibliography available.'}

## Archives

{archives if archives else 'No archive information available.'}

---

*Generated: {datetime.utcnow().isoformat()}Z | Source: {shortcode}.json*
"""

    # Write output
    output_file = OUTPUT_DIR / f"{shortcode}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(frontmatter)

    log_success(f"Wrote: {output_file}")


def process_single(shortcode: str, force: bool = False,
                   skip_enrich: bool = False, skip_links: bool = False):
    """Process a single scholar."""

    log_info(f"Processing scholar: {shortcode}")

    # Check if needs processing
    json_file = SOURCE_DIR / f"{shortcode}.json"
    output_file = OUTPUT_DIR / f"{shortcode}.md"

    if not force and output_file.exists() and json_file.exists():
        json_mtime = json_file.stat().st_mtime
        output_mtime = output_file.stat().st_mtime
        if json_mtime <= output_mtime:
            log_info(f"Skipping (already up to date): {shortcode}")
            return

    # Stage 1: Parse
    stage_parse()
    json_data = parse_record(shortcode)

    # Stage 2: Enrich
    enrichment = None
    if not skip_enrich:
        stage_enrich()
        enrichment = enrich_record(shortcode, json_data, force)

    # Stage 3: Link
    scholar_links = []
    if not skip_links:
        stage_link()
        scholar_links = compute_links(shortcode, json_data)

    # Stage 4: Write
    stage_write()
    write_markdown(shortcode, json_data, enrichment, scholar_links)

    log_success(f"Completed: {shortcode}")


def process_all(force: bool = False, skip_enrich: bool = False, skip_links: bool = False):
    """Process all scholars."""

    if not SOURCE_DIR.exists():
        log_error(f"Source directory not found: {SOURCE_DIR}")
        return

    files = list(SOURCE_DIR.glob("*.json"))
    if not files:
        log_warn(f"No JSON files found in {SOURCE_DIR}")
        return

    log_info(f"Processing {len(files)} scholars from {SOURCE_DIR}")

    count = 0
    for json_file in files:
        shortcode = json_file.stem
        try:
            process_single(shortcode, force, skip_enrich, skip_links)
            count += 1
        except Exception as e:
            log_error(f"Failed to process {shortcode}: {e}")

    log_success(f"Processed {count} scholars")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Art Historian Knowledge Base Pipeline')
    parser.add_argument('--file', help='Process single scholar by shortcode')
    parser.add_argument('--all', action='store_true', help='Process all scholars')
    parser.add_argument('--force', action='store_true', help='Force rebuild (ignore cache)')
    parser.add_argument('--skip-enrich', action='store_true', help='Skip enrichment stage')
    parser.add_argument('--skip-links', action='store_true', help='Skip link computation')

    args = parser.parse_args()

    # Initialize
    init_dirs()

    # Run
    if args.file:
        process_single(args.file, args.force, args.skip_enrich, args.skip_links)
    elif args.all:
        process_all(args.force, args.skip_enrich, args.skip_links)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
