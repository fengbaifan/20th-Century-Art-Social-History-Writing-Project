#!/usr/bin/env python3
"""
Heal — Self-healing for knowledge base
Automatically creates missing pages and fixes broken links
"""

import re
import sys
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent.parent
KB_DIR = PROJECT_ROOT / "knowledge-base"


def log_info(msg):
    print(f"\033[94m[INFO]\033[0m {msg}")


def log_success(msg):
    print(f"\033[92m[SUCCESS]\033[0m {msg}")


def log_warn(msg):
    print(f"\033[93m[WARN]\033[0m {msg}")


def get_all_pages():
    """Get all existing page names."""
    pages = set()
    if not KB_DIR.exists():
        return pages

    for md_file in KB_DIR.glob("*.md"):
        if md_file.name in ["index.md", "log.md", "overview.md"]:
            continue
        content = md_file.read_text(encoding='utf-8')
        match = re.search(r'^name:\s*(.+?)\s*$', content, re.MULTILINE)
        if match:
            pages.add(match.group(1).strip())
    return pages


def get_all_wikilinks():
    """Get all wikilinks used across the knowledge base."""
    links = {}
    if not KB_DIR.exists():
        return links

    for md_file in KB_DIR.glob("*.md"):
        if md_file.name in ["index.md", "log.md", "overview.md"]:
            continue
        content = md_file.read_text(encoding='utf-8')
        wikilinks = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)
        for link in wikilinks:
            link = link.strip()
            if link not in ['index', 'log', 'overview']:
                if link not in links:
                    links[link] = []
                links[link].append(str(md_file.relative_to(PROJECT_ROOT)))
    return links


def create_stub_page(shortcode, referenced_by):
    """Create a stub page for a missing entity."""
    log_info(f"Creating stub: {shortcode}")

    content = f"""---
full_name: "{shortcode}"
title_zh: "待补充"
birth: null
death: null
country: null
subjects:
  []
enriched: false
links: 0
sources:
  - auto-generated
---

# {shortcode}

*This page was auto-generated as a stub because it was referenced but not found.*

## Sources

Referenced by:
{chr(10).join(f"- [[{src}]]" for src in referenced_by[:5])}

## Notes

This stub should be expanded with actual biographical information.
Please add content or delete if not needed.

---

*Auto-generated: {datetime.now(timezone.utc).isoformat()}*
"""

    output_file = KB_DIR / f"{shortcode}.md"
    output_file.write_text(content, encoding='utf-8')
    return True


def fix_broken_link(source_file, broken_link, new_target):
    """Fix a broken wikilink in a file."""
    content = source_file.read_text(encoding='utf-8')

    # Replace [[broken]] with [[new]] or [[new|display]]
    pattern = rf'\[\[{re.escape(broken_link)}(\|[^\]]+)?\]\]'
    replacement = f'[[{new_target}]]'
    new_content = re.sub(pattern, replacement, content)

    source_file.write_text(new_content, encoding='utf-8')
    log_info(f"Fixed link in {source_file.name}: [[{broken_link}]] -> [[{new_target}]]")


def main():
    log_info("=" * 60)
    log_info("Knowledge Base Self-Healing")
    log_info("=" * 60)

    if not KB_DIR.exists():
        log_warn("knowledge-base/ directory not found")
        return 0

    pages = get_all_pages()
    log_info(f"Found {len(pages)} existing pages")

    links = get_all_wikilinks()
    log_info(f"Found {len(links)} unique wikilinks")

    # Find broken links (links to non-existent pages)
    broken = {}
    for link, sources in links.items():
        if link not in pages:
            broken[link] = sources

    if not broken:
        log_success("No broken links found!")
        return 0

    log_info(f"Found {len(broken)} broken links")

    created = 0
    fixed = 0

    for broken_link, sources in broken.items():
        # Try to find a similar page name
        similar = None
        for page in pages:
            if broken_link.lower() in page.lower() or page.lower() in broken_link.lower():
                similar = page
                break

        if similar:
            # Fix link to similar page
            for source in sources:
                source_file = PROJECT_ROOT / source
                fix_broken_link(source_file, broken_link, similar)
                fixed += 1
        else:
            # Create stub page
            if create_stub_page(broken_link, sources):
                created += 1

    log_info("=" * 60)
    log_success(f"Healing complete:")
    log_success(f"  - Created {created} stub pages")
    log_success(f"  - Fixed {fixed} broken links")

    return 0


if __name__ == "__main__":
    sys.exit(main())
