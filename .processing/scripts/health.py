#!/usr/bin/env python3
"""
Health Check — Structural integrity checks for knowledge base
Zero LLM calls — runs completely offline
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent.parent
KB_DIR = PROJECT_ROOT / "knowledge-base"
GRAPH_DIR = PROJECT_ROOT / "graph"


def log_info(msg):
    print(f"\033[94m[INFO]\033[0m {msg}")


def log_error(msg):
    print(f"\033[91m[ERROR]\033[0m {msg}")


def log_warn(msg):
    print(f"\033[93m[WARN]\033[0m {msg}")


def log_success(msg):
    print(f"\033[92m[SUCCESS]\033[0m {msg}")


def check_empty_files():
    """Check for empty or near-empty markdown files."""
    log_info("Checking for empty files...")
    issues = []

    if not KB_DIR.exists():
        log_warn("knowledge-base/ directory not found")
        return issues

    for md_file in KB_DIR.glob("*.md"):
        if md_file.name == "index.md":
            continue
        content = md_file.read_text(encoding='utf-8')
        # Remove frontmatter
        content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
        content = content.strip()
        if len(content) < 50:
            issues.append({
                "severity": "ERROR",
                "file": str(md_file.relative_to(PROJECT_ROOT)),
                "issue": f"Empty or stub file ({len(content)} chars)",
                "fix": "Expand content or delete if truly empty"
            })

    return issues


def check_frontmatter():
    """Check that all files have valid YAML frontmatter."""
    log_info("Checking frontmatter...")
    issues = []

    if not KB_DIR.exists():
        return issues

    required_fields = ["full_name", "title_zh"]

    for md_file in KB_DIR.glob("*.md"):
        if md_file.name == "index.md":
            continue
        content = md_file.read_text(encoding='utf-8')

        if not content.startswith('---'):
            issues.append({
                "severity": "ERROR",
                "file": str(md_file.relative_to(PROJECT_ROOT)),
                "issue": "Missing YAML frontmatter",
                "fix": "Add frontmatter with name and title"
            })
            continue

        # Extract frontmatter
        match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not match:
            issues.append({
                "severity": "ERROR",
                "file": str(md_file.relative_to(PROJECT_ROOT)),
                "issue": "Malformed frontmatter",
                "fix": "Check YAML syntax"
            })
            continue

        fm = match.group(1)
        for field in required_fields:
            if not re.search(rf'^{field}:', fm, re.MULTILINE):
                issues.append({
                    "severity": "WARN",
                    "file": str(md_file.relative_to(PROJECT_ROOT)),
                    "issue": f"Missing frontmatter field: {field}",
                    "fix": f"Add {field} to frontmatter"
                })

    return issues


def check_broken_links():
    """Check for broken [[wikilinks]] to non-existent pages."""
    log_info("Checking for broken links...")
    issues = []

    if not KB_DIR.exists():
        return issues

    # Build set of valid page names (use filename as shortcode)
    valid_pages = set()
    for md_file in KB_DIR.glob("*.md"):
        if md_file.name == "index.md":
            continue
        # Use filename (shortcode derived from Title) instead of frontmatter name
        valid_pages.add(md_file.stem)

    # Check for broken links
    for md_file in KB_DIR.glob("*.md"):
        if md_file.name == "index.md":
            continue
        content = md_file.read_text(encoding='utf-8')

        # Find all wikilinks
        wikilinks = re.findall(r'\[\[([^\]]+)\]\]', content)
        for link in wikilinks:
            # Strip any anchor/text after |
            link = link.split('|')[0].strip()
            if link not in valid_pages and link not in ['index', 'log', 'overview']:
                issues.append({
                    "severity": "ERROR",
                    "file": str(md_file.relative_to(PROJECT_ROOT)),
                    "issue": f"Broken link [[{link}]]",
                    "fix": "Create page or fix link target"
                })

    return issues


def check_index_sync():
    """Check that index.md is synchronized with actual pages."""
    log_info("Checking index synchronization...")
    issues = []

    index_file = KB_DIR / "index.md"
    if not index_file.exists():
        issues.append({
            "severity": "ERROR",
            "file": "knowledge-base/index.md",
            "issue": "Missing index.md",
            "fix": "Create index.md with page catalog"
        })
        return issues

    content = index_file.read_text(encoding='utf-8')

    # Extract page names from index
    index_pages = set()
    for match in re.finditer(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content):
        index_pages.add(match.group(1).strip())

    # Compare with actual pages (use filename as shortcode)
    actual_pages = set()
    for md_file in KB_DIR.glob("*.md"):
        if md_file.name in ["index.md", "log.md", "overview.md"]:
            continue
        # Use filename (shortcode derived from Title)
        actual_pages.add(md_file.stem)

    # Find pages in index but not in filesystem
    for page in index_pages:
        if page not in actual_pages:
            issues.append({
                "severity": "ERROR",
                "file": "knowledge-base/index.md",
                "issue": f"Index references missing page: [[{page}]]",
                "fix": "Remove from index or create page"
            })

    # Find pages not in index
    orphan_pages = actual_pages - index_pages
    if orphan_pages:
        for page in orphan_pages:
            issues.append({
                "severity": "WARN",
                "file": f"knowledge-base/{page}.md",
                "issue": "Page not in index",
                "fix": f"Add [[{page}]] to index.md"
            })

    return issues


def main():
    log_info("=" * 60)
    log_info("Knowledge Base Health Check")
    log_info("=" * 60)

    all_issues = []

    # Run checks
    all_issues.extend(check_empty_files())
    all_issues.extend(check_frontmatter())
    all_issues.extend(check_broken_links())
    all_issues.extend(check_index_sync())

    # Summary
    log_info("=" * 60)
    log_info("Health Report")
    log_info("=" * 60)

    if not all_issues:
        log_success("No issues found!")
        return 0

    errors = [i for i in all_issues if i["severity"] == "ERROR"]
    warnings = [i for i in all_issues if i["severity"] == "WARN"]

    log_error(f"Found {len(errors)} errors, {len(warnings)} warnings")

    # Print issues table
    print("\n{:<10} {:<40} {:<30}".format("SEVERITY", "FILE", "ISSUE"))
    print("-" * 80)
    for issue in all_issues:
        print("{:<10} {:<40} {:<30}".format(
            issue["severity"],
            issue["file"][-40:],
            issue["issue"][:30]
        ))

    print("\nRun /kb-lint for semantic analysis (uses LLM).")
    print("Run /kb-heal to automatically fix issues.")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
