#!/usr/bin/env python3
"""
Rename Shortcodes Script
Converts URL-based shortcodes to Title-based shortcodes.

Input: "Abell, Walter" (Title field format)
Output: "walter_abel" (filename format)
"""

import json
import re
import shutil
import sys
from pathlib import Path

# Force UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).parent.parent.parent
MID_DATA_DIR = PROJECT_ROOT / "RwaFiles" / "mid-data"
KB_DIR = PROJECT_ROOT / "knowledge-base"


def title_to_shortcode(title):
    """Convert 'Last, First' to 'first_last' format."""
    if not title:
        return None

    # Handle "Last, First" format
    if ',' in title:
        parts = title.split(',')
        if len(parts) >= 2:
            last_name = parts[0].strip()
            first_part = parts[1].strip()
            # Handle "First Middle" or just "First"
            first_parts = first_part.split()
            if first_parts:
                first_name = first_parts[0].lower()
                last_name_lower = last_name.lower()
                # Use first 4 chars of last name + first char of first name (classic shortcode style)
                # But also handle collisions with a more robust approach
                return f"{last_name_lower}_{first_name}"
    return None


def build_shortcode_from_title(title):
    """Build a unique shortcode from title 'First Last' format."""
    if not title:
        return None

    # Handle "Last, First" format → convert to "First Last"
    if ',' in title:
        parts = title.split(',')
        if len(parts) >= 2:
            last_name = parts[0].strip()
            first_part = parts[1].strip()
            first_parts = first_part.split()
            if first_parts:
                first_name = first_parts[0]
                # "Karl Abraham" from "Abraham, Karl"
                return f"{first_name} {last_name}"

    return title


def create_safe_filename(name):
    """Convert 'First Last' to 'first_last' safe filename."""
    if not name:
        return None
    # Lowercase, replace spaces with underscore, remove special chars
    safe = name.lower().replace(' ', '_')
    safe = re.sub(r'[^a-z0-9_]', '', safe)
    return safe


def get_title_from_json(json_file):
    """Extract Title from JSON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('Title', '')
    except Exception as e:
        print(f"Error reading {json_file}: {e}")
        return None


def main():
    print("=== Shortcode Rename Tool ===")
    print(f"MID_DATA: {MID_DATA_DIR}")
    print(f"KB_DIR: {KB_DIR}")
    print()

    # Build mapping: old_shortcode -> new_shortcode
    rename_map = {}  # old_name -> new_name

    print("Building rename map...")
    for json_file in MID_DATA_DIR.glob("*.json"):
        old_name = json_file.stem  # e.g., "abrahamk"
        title = get_title_from_json(json_file)
        if not title:
            print(f"  WARNING: No title for {old_name}, skipping")
            continue

        # Convert "Last, First" to "First Last"
        display_name = build_shortcode_from_title(title)
        new_name = create_safe_filename(display_name)

        if new_name and new_name != old_name:
            rename_map[old_name] = new_name
            print(f"  {old_name} → {new_name} ({title})")
        elif new_name == old_name:
            print(f"  {old_name} (unchanged)")
        else:
            print(f"  WARNING: Could not generate shortcode for {title}")

    print(f"\nTotal files to rename: {len(rename_map)}")
    print()

    # Create reverse map: new_name -> old_name (for wikilink updates)
    reverse_map = {v: k for k, v in rename_map.items()}

    # Phase 1: Rename JSON files
    print("=== Phase 1: Renaming JSON files ===")
    json_renamed = 0
    for old_name, new_name in rename_map.items():
        old_path = MID_DATA_DIR / f"{old_name}.json"
        new_path = MID_DATA_DIR / f"{new_name}.json"

        if old_path.exists() and not new_path.exists():
            shutil.move(str(old_path), str(new_path))
            print(f"  {old_name}.json → {new_name}.json")
            json_renamed += 1
        elif new_path.exists():
            print(f"  SKIP: {new_name}.json already exists")
        else:
            print(f"  ERROR: {old_name}.json not found")

    print(f"JSON files renamed: {json_renamed}")
    print()

    # Phase 2: Rename MD files
    print("=== Phase 2: Renaming MD files ===")
    md_renamed = 0
    for old_name, new_name in rename_map.items():
        old_path = KB_DIR / f"{old_name}.md"
        new_path = KB_DIR / f"{new_name}.md"

        if old_path.exists() and not new_path.exists():
            shutil.move(str(old_path), str(new_path))
            print(f"  {old_name}.md → {new_name}.md")
            md_renamed += 1
        elif new_path.exists():
            print(f"  SKIP: {new_name}.md already exists")
        else:
            print(f"  ERROR: {old_name}.md not found")

    print(f"MD files renamed: {md_renamed}")
    print()

    # Phase 3: Update wikilinks in all MD files
    print("=== Phase 3: Updating wikilinks ===")
    wikilinks_updated = 0
    files_updated = 0

    for md_file in KB_DIR.glob("*.md"):
        content = md_file.read_text(encoding='utf-8')
        original_content = content

        # Replace all wikilinks using old shortcodes with new shortcodes
        for old_name, new_name in rename_map.items():
            # Match [[oldname]] but not [[oldname123]] (partial matches)
            pattern = r'\[\[' + re.escape(old_name) + r'\]\]'
            replacement = f'[[{new_name}]]'
            content = re.sub(pattern, replacement, content)

        if content != original_content:
            md_file.write_text(content, encoding='utf-8')
            files_updated += 1
            wikilinks_updated += content.count(f'[[{new_name}]]')

    print(f"Files updated: {files_updated}")
    print(f"Wikilinks updated: {wikilinks_updated}")
    print()

    # Phase 4: Update frontmatter in MD files
    print("=== Phase 4: Updating frontmatter 'name' field ===")
    frontmatter_updated = 0
    for old_name, new_name in rename_map.items():
        md_path = KB_DIR / f"{new_name}.md"
        if md_path.exists():
            content = md_path.read_text(encoding='utf-8')
            # Update name: in frontmatter
            content = re.sub(
                r'^name:\s*' + re.escape(old_name) + r'$',
                f'name: {new_name}',
                content,
                flags=re.MULTILINE
            )
            md_path.write_text(content, encoding='utf-8')
            frontmatter_updated += 1

    print(f"Frontmatter updated: {frontmatter_updated}")
    print()

    # Summary
    print("=== Rename Complete ===")
    print(f"JSON files renamed: {json_renamed}")
    print(f"MD files renamed: {md_renamed}")
    print(f"Wikilinks updated: {wikilinks_updated}")
    print(f"Note: Run 'python .processing/scripts/health.py' to verify")


if __name__ == '__main__':
    main()