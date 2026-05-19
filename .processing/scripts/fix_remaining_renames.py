#!/usr/bin/env python3
"""
Fix remaining renames - handles files that weren't renamed properly.
"""

import json
import re
import shutil
import sys
import io
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
MID_DATA_DIR = PROJECT_ROOT / "RwaFiles" / "mid-data"
KB_DIR = PROJECT_ROOT / "knowledge-base"

# Force UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def build_shortcode_from_title(title):
    """Convert 'Last, First' to 'First Last' then to 'first_last'."""
    if not title:
        return None

    if ',' in title:
        parts = title.split(',')
        if len(parts) >= 2:
            last_name = parts[0].strip()
            first_part = parts[1].strip()
            first_parts = first_part.split()
            if first_parts:
                first_name = first_parts[0]
                # "Karl Abraham" from "Abraham, Karl"
                display_name = f"{first_name} {last_name}"
                safe = display_name.lower().replace(' ', '_')
                safe = re.sub(r'[^a-z0-9_]', '', safe)
                return safe
    return None


def get_title_from_json(json_file):
    """Extract Title from JSON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('Title', '')
    except Exception as e:
        return None


def create_safe_filename(name):
    """Convert to safe filename."""
    if not name:
        return None
    safe = name.lower().replace(' ', '_')
    safe = re.sub(r'[^a-z0-9_]', '', safe)
    return safe


def main():
    print("=== Fix Remaining Renames ===")

    # Build mapping from mid-data filenames
    json_to_title = {}
    for json_file in MID_DATA_DIR.glob("*.json"):
        title = get_title_from_json(json_file)
        if title:
            new_shortcode = build_shortcode_from_title(title)
            if new_shortcode:
                json_to_title[json_file.stem] = (title, new_shortcode)

    print(f"Found {len(json_to_title)} JSON files with titles")

    # Find KB files that don't match their JSON counterparts
    fixed = 0
    skipped = 0

    for md_file in KB_DIR.glob("*.md"):
        if md_file.name in ('index.md', 'log.md'):
            continue

        old_stem = md_file.stem

        # Check if this file's JSON has a different (new) shortcode
        if old_stem in json_to_title:
            title, new_stem = json_to_title[old_stem]

            if old_stem != new_stem:
                new_path = KB_DIR / f"{new_stem}.md"

                if new_path.exists():
                    # Both exist - check which is newer/correct
                    # Read old file content to see if it was already renamed
                    old_content = md_file.read_text(encoding='utf-8')
                    if f'name: {new_stem}' in old_content:
                        # Old file already has new name, just delete it
                        print(f"  Removing duplicate: {old_stem}.md (already has name: {new_stem})")
                        md_file.unlink()
                        fixed += 1
                    else:
                        print(f"  CONFLICT: Both {old_stem}.md and {new_stem}.md exist")
                        skipped += 1
                else:
                    # Rename old file
                    print(f"  Renaming: {old_stem}.md → {new_stem}.md")
                    shutil.move(str(md_file), str(new_path))

                    # Update frontmatter name
                    content = new_path.read_text(encoding='utf-8')
                    content = re.sub(
                        r'^name:\s*' + re.escape(old_stem) + r'$',
                        f'name: {new_stem}',
                        content,
                        flags=re.MULTILINE
                    )
                    new_path.write_text(content, encoding='utf-8')
                    fixed += 1

    print(f"\nFixed: {fixed}, Skipped: {skipped}")

    # Now update all wikilinks across all MD files
    print("\n=== Updating wikilinks ===")

    # Build complete old→new map from JSON files
    complete_map = {}
    for json_file in MID_DATA_DIR.glob("*.json"):
        title = get_title_from_json(json_file)
        if title:
            new_shortcode = build_shortcode_from_title(title)
            if new_shortcode and json_file.stem != new_shortcode:
                complete_map[json_file.stem] = new_shortcode

    print(f"Wikilinks to update: {len(complete_map)}")

    wikilinks_updated = 0
    for md_file in KB_DIR.glob("*.md"):
        if md_file.name in ('index.md', 'log.md'):
            continue

        content = md_file.read_text(encoding='utf-8')
        original = content

        for old_name, new_name in complete_map.items():
            pattern = r'\[\[' + re.escape(old_name) + r'\]\]'
            content = re.sub(pattern, f'[[{new_name}]]', content)

        if content != original:
            md_file.write_text(content, encoding='utf-8')
            wikilinks_updated += 1

    print(f"Files with wikilinks updated: {wikilinks_updated}")
    print("\nDone!")


if __name__ == '__main__':
    main()