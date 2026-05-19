#!/usr/bin/env python3
"""
Enrich - Wikipedia enrichment for knowledge base
Uses Playwright to fetch Chinese names from Wikipedia
"""

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

PROJECT_ROOT = Path(__file__).parent.parent.parent
KB_DIR = PROJECT_ROOT / "knowledge-base"


def log_info(msg):
    print(f"\033[94m[INFO]\033[0m {msg}", flush=True)


def log_success(msg):
    print(f"\033[92m[SUCCESS]\033[0m {msg}", flush=True)


def log_warn(msg):
    print(f"\033[93m[WARN]\033[0m {msg}", flush=True)


def has_chinese_chars(text):
    """Check if text contains Chinese characters."""
    return bool(re.search(r'[一-鿿]', text))


def get_scholars_needing_enrichment():
    """Get scholars that need Chinese name enrichment (no real Chinese name)."""
    scholars = []

    for md_file in KB_DIR.glob("*.md"):
        if md_file.name in ["index.md", "log.md", "overview.md"]:
            continue

        content = md_file.read_text(encoding='utf-8')

        # Extract title_zh
        title_zh_match = re.search(r'^title_zh:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
        title_zh = title_zh_match.group(1).strip() if title_zh_match else ""

        # If title_zh is "待补充" or doesn't contain Chinese chars, needs enrichment
        if title_zh == "待补充" or not has_chinese_chars(title_zh):
            full_name_match = re.search(r'^full_name:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
            full_name = full_name_match.group(1).strip() if full_name_match else md_file.stem

            scholars.append({
                "shortcode": md_file.stem,
                "full_name": full_name,
                "file": md_file
            })

    return scholars


def fetch_chinese_name(full_name, playwright):
    """Fetch Chinese name from Chinese Wikipedia using Playwright."""
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        # Try Chinese Wikipedia search
        url = f"https://zh.wikipedia.org/wiki/Special:Search?search={quote(full_name)}"
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=15000)

        current_url = page.url
        title_zh = None

        # If still on search page, look for result
        if "Special:Search" in current_url:
            # Check if there's a direct match in results
            try:
                # Look for search results with exact match
                results = page.locator(".mw-search-result-heading a")
                count = results.count()
                if count > 0:
                    # Click the first result
                    first_href = results.first.get_attribute("href")
                    if first_href:
                        page.goto(f"https://zh.wikipedia.org{first_href}", timeout=30000)
                        page.wait_for_load_state("networkidle", timeout=15000)
            except:
                pass

        # Now extract title from h1
        try:
            h1 = page.locator("h1#firstHeading")
            if h1.count() == 0:
                h1 = page.locator("h1").first
            title_zh = h1.inner_text().strip()
            # Clean up - remove [编辑] suffix
            title_zh = re.sub(r'\[.*?\]', '', title_zh).strip()
        except:
            title_zh = None

        browser.close()
        return title_zh

    except Exception as e:
        browser.close()
        return None


def update_page_title_zh(file_path, title_zh):
    """Update page with Chinese name."""
    content = file_path.read_text(encoding='utf-8')

    if re.search(r'^title_zh:', content, re.MULTILINE):
        content = re.sub(
            r'^title_zh:\s*["\']?.*?["\']?\s*$',
            f'title_zh: "{title_zh}"',
            content,
            flags=re.MULTILINE
        )
    else:
        content = re.sub(
            r'^(full_name:.*)$',
            r'\1\ntitle_zh: "' + title_zh + '"',
            content,
            flags=re.MULTILINE
        )

    file_path.write_text(content, encoding='utf-8')


def main():
    from playwright.sync_api import sync_playwright

    import argparse
    parser = argparse.ArgumentParser(description='Enrich KB with Chinese names from Wikipedia')
    parser.add_argument('--limit', type=int, default=100, help='Max scholars to process')
    parser.add_argument('--dry-run', action='store_true', help='Dry run only')
    args = parser.parse_args()

    scholars = get_scholars_needing_enrichment()
    log_info(f"Found {len(scholars)} scholars needing enrichment")

    if not scholars:
        log_success("All scholars have Chinese names!")
        return 0

    to_process = scholars[:args.limit]
    log_info(f"Processing {len(to_process)} scholars...")

    with sync_playwright() as p:
        for i, scholar in enumerate(to_process):
            log_info(f"[{i+1}/{len(to_process)}] {scholar['full_name']}")

            if not args.dry_run:
                title_zh = fetch_chinese_name(scholar['full_name'], p)

                if title_zh:
                    update_page_title_zh(scholar['file'], title_zh)
                    log_success(f"  → {title_zh}")
                else:
                    log_warn(f"  → Not found")

                time.sleep(0.5)  # Rate limiting

    return 0


if __name__ == '__main__':
    sys.exit(main())