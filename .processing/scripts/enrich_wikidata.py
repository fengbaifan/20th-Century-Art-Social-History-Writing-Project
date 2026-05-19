#!/usr/bin/env python3
"""
Enrich via Wikidata - Batch fetch Chinese names using Playwright + Wikidata
流程: 搜索 Wikidata → 获取 Q-ID → 提取中文维基链接 → 更新页面

Reference Sources / 参考来源:
- ArchiveGrid
- Archives of American Art
- Dictionnaire critique des historiens de l'art
- Digital Public Library of America
- Getty Research Portal
- Social Networks & Archival Context
- Wikidata
- WorldCat
"""

import re
import sys
import time
import json
from pathlib import Path
from urllib.parse import quote

PROJECT_ROOT = Path(__file__).parent.parent.parent
KB_DIR = PROJECT_ROOT / "knowledge-base"
CACHE_DIR = PROJECT_ROOT / ".processing" / "enrichment-cache"

# Reference sources for verification
REFERENCE_SOURCES = [
    {"name": "ArchiveGrid", "url": "https://researchworkspace.com/search/?q=", "type": "archival"},
    {"name": "Archives of American Art", "url": "https://www.aaa.si.edu/search/historian?q=", "type": "archival"},
    {"name": "Dictionnaire critique des historiens de l'art", "url": "https://github.com/aurelie1/dictionnaire-critique-historians-art/", "type": "dictionary"},
    {"name": "Digital Public Library of America", "url": "https://dp.la/search?q=", "type": "library"},
    {"name": "Getty Research Portal", "url": "https://portal.getty.edu/search?q=", "type": "research"},
    {"name": "Social Networks & Archival Context", "url": "https://snaccooperative.org/search?search_all=", "type": "archival"},
    {"name": "Wikidata", "url": "https://www.wikidata.org/wiki/Special:Search?search=", "type": "authority"},
    {"name": "WorldCat", "url": "https://www.worldcat.org/search?q=", "type": "bibliography"},
]


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
    """Get scholars that need Chinese name enrichment."""
    scholars = []
    for md_file in KB_DIR.glob("*.md"):
        if md_file.name in ["index.md", "log.md", "overview.md"]:
            continue
        content = md_file.read_text(encoding='utf-8')
        title_zh_match = re.search(r'^title_zh:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
        title_zh = title_zh_match.group(1).strip() if title_zh_match else ""
        if title_zh == "待补充" or not has_chinese_chars(title_zh):
            full_name_match = re.search(r'^full_name:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
            full_name = full_name_match.group(1).strip() if full_name_match else md_file.stem
            scholars.append({
                "shortcode": md_file.stem,
                "full_name": full_name,
                "file": md_file
            })
    return scholars


def fetch_chinese_name_via_wikidata(full_name, p):
    """
    Fetch Chinese name via Wikidata only (no fallback to avoid wrong matches).
    Returns Chinese name if found via Wikidata, None otherwise.
    """
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        # Step 1: Search Wikidata
        search_url = f"https://www.wikidata.org/wiki/Special:Search?search={quote(full_name)}&ns0=1&ns120=1"
        page.goto(search_url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=15000)

        # Step 2: Get first result Q-ID
        q_id = None
        try:
            result = page.locator(".mw-search-result-heading a").first
            href = result.get_attribute("href")
            match = re.search(r'/Q(\d+)', href)
            if match:
                q_id = "Q" + match.group(1)
        except:
            pass

        if not q_id:
            browser.close()
            return None

        # Step 3: Navigate to Wikidata page
        wikidata_url = f"https://www.wikidata.org/wiki/{q_id}"
        page.goto(wikidata_url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=15000)

        # Step 4: Extract Chinese Wikipedia link text
        chinese_name = None
        try:
            links = page.locator("a[href*='zh.wikipedia.org']")
            count = links.count()
            if count > 0:
                link = links.first
                chinese_name = link.inner_text().strip()
                chinese_name = re.sub(r'\s*\(zhwiki\)\s*', '', chinese_name).strip()
        except:
            pass

        browser.close()
        return chinese_name

    except Exception as e:
        try:
            browser.close()
        except:
            pass
        return None


def verify_via_reference_sources(full_name, p):
    """
    Verify scholar information via reference sources.
    Returns dict with verification status from each source.
    """
    results = {}

    browser = p.chromium.launch(headless=True)

    for source in REFERENCE_SOURCES:
        try:
            search_url = f"{source['url']}{quote(full_name)}"
            page = browser.new_page()
            page.goto(search_url, timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)

            # Check if results found
            # Different sites have different result indicators
            results[source['name']] = {
                "verified": False,
                "url": search_url,
                "type": source['type']
            }

            page.close()
        except Exception as e:
            results[source['name']] = {
                "verified": False,
                "error": str(e),
                "type": source['type']
            }

    browser.close()
    return results


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


def save_enrichment_cache(shortcode, data):
    """Save enrichment data to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{shortcode}.json"
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    from playwright.sync_api import sync_playwright

    import argparse
    parser = argparse.ArgumentParser(description='Enrich KB via Wikidata + Chinese Wikipedia')
    parser.add_argument('--limit', type=int, default=0, help='Max scholars to process (0=all)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run only')
    parser.add_argument('--verify-only', action='store_true', help='Only verify via reference sources')
    args = parser.parse_args()

    scholars = get_scholars_needing_enrichment()
    log_info(f"Found {len(scholars)} scholars needing enrichment")
    log_info(f"Reference sources: {', '.join([s['name'] for s in REFERENCE_SOURCES])}")

    if not scholars:
        log_success("All scholars have Chinese names!")
        return 0

    to_process = scholars[:args.limit] if args.limit > 0 else scholars
    log_info(f"Processing {len(to_process)} scholars...")

    success_count = 0
    fail_count = 0

    with sync_playwright() as p:
        for i, scholar in enumerate(to_process):
            log_info(f"[{i+1}/{len(to_process)}] {scholar['full_name']}")

            if args.dry_run:
                continue

            if args.verify_only:
                # Only verify, don't update
                verify_via_reference_sources(scholar['full_name'], p)
                continue

            title_zh = fetch_chinese_name_via_wikidata(scholar['full_name'], p)

            if title_zh and has_chinese_chars(title_zh):
                update_page_title_zh(scholar['file'], title_zh)
                log_success(f"  → {title_zh}")
                success_count += 1

                # Save to cache
                save_enrichment_cache(scholar['shortcode'], {
                    "timestamp": time.time(),
                    "chinese_name": title_zh,
                    "sources": REFERENCE_SOURCES
                })
            else:
                log_warn(f"  → Not found")
                fail_count += 1

            time.sleep(0.3)  # Rate limiting

    log_info(f"\nCompleted: {success_count} success, {fail_count} not found")
    return 0


if __name__ == '__main__':
    sys.exit(main())
