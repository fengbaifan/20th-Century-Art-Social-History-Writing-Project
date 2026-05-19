#!/usr/bin/env python3
"""
Fix Traditional Chinese characters and incorrect translations to Simplified Chinese.
Academic standard translation corrections.
"""

import re
from pathlib import Path

KB_DIR = Path(__file__).parent.parent.parent / "knowledge-base"

# Mapping of Traditional to Simplified Chinese
TRAD_TO_SIMP = {
    '喬': '乔', '馬': '马', '羅': '罗', '裡': '里', '溫': '温',
    '約': '约', '華': '华', '龔': '龚', '薩': '萨', '爾': '尔',
    '爾': '尔', '維': '维', '德': '德', '克': '克', '斯': '斯',
    '強': '强', '沃': '沃', '瑪': '玛', '麗': '丽', '劉': '刘',
    '裡': '里', '愛': '爱', '寧': '宁', '漢': '汉', '萊': '莱',
    '鮑': '鲍', '納': '纳', '費': '费', '愛德華': '爱德华',
    '布萊': '布莱', '弗蘭克': '弗兰克', '喬治': '乔治',
    '馬丁': '马丁', '馬克': '马克', '馬裡': '马里',
    '羅伯森': '罗伯森', '羅裡默': '罗里默', '詹姆斯': '詹姆斯',
}

# Corrections for specific name translations (wrong translations)
NAME_CORRECTIONS = {
    'gaston_maspero.md': '加斯顿·马伯罗',  # was 馬伯樂
    'george_reisner.md': '乔治·安德鲁·赖斯纳',  # was 賴斯納
    'james_rorimer.md': '詹姆斯·罗里默',  # was 羅里默
    'johann_winckelmann.md': '约翰·温克尔曼',  # was 溫克爾曼
    'john_hayes.md': '约翰·海斯',  # was 海斯 (OK but traditional)
    'john_richardson.md': '约翰·理查森',  # was 理查森 (Traditional)
    'john_walsh.md': '约翰·沃尔什',  # was 沃爾什
    'john_white.md': '约翰·怀特',  # was with Traditional
    'joseph_henry.md': '约瑟·亨利',  # was 約瑟·亨利
    'jules_goncourt.md': '朱尔·德·龚古尔',  # was 龔固爾
    'j_wardperkins.md': '约翰·沃德-珀金斯',  # was Traditional
    'kenneth_clark.md': '肯尼思·克拉克',  # was 肯尼斯
    'langdon_warner.md': '兰登·华纳',  # was 华尔纳 (simplified ok)
    'louis_vauxcelles.md': '路易·沃克塞勒',  # was 沃塞勒
    'ludwig_borchardt.md': '路德维希·波尔哈特',  # was 路德維希
    'margaret_murray.md': '玛格丽特·穆雷',  # was 瑪格麗特
    'margherita_sarfatti.md': '玛格丽塔·萨尔法蒂',  # was 玛格丽塔·萨尔法季
    'martin_robertson.md': '马丁·罗伯森',  # was 馬丁·羅伯森
    'mile_mle.md': '埃米尔·马勒',  # was 馬勒
    'mm_davy.md': 'MM·戴维',  # was completely wrong
    'philip_johnson.md': '菲利普·约翰逊',  # was 菲力普·強生
    'robert_wheeler.md': '罗伯特·惠勒',  # was 莫蒂默·惠勒 (wrong!)
    'walter_pater.md': '沃尔特·佩特',  # was 華特·佩特
    'wollaston_franks.md': '奥古斯都·沃拉斯顿·弗兰克斯',  # was Traditional
    'wolfgang_lotz.md': '沃尔夫冈·洛茨',  # was 沃爾夫岡
    'henry_breasted.md': '亨利·布雷斯特德',  # was 詹姆斯·亨利·布雷斯特德 (wrong!)
    'hercules_read.md': '赫拉克勒斯·里德',  # was 查尔斯·赫拉克勒斯·里德 (wrong!)
    'henry_adams.md': '亨利·布鲁克斯·亚当斯',  # was 亨利·布鲁克斯·亚当斯 (OK)
    'lewis_mumford.md': '刘易斯·芒福德',  # was 劉易斯·芒福德
}

def convert_trad_to_simp(text):
    """Convert Traditional Chinese to Simplified Chinese."""
    result = text
    for trad, simp in TRAD_TO_SIMP.items():
        result = result.replace(trad, simp)
    return result

def fix_file(file_path):
    """Fix a single file's title_zh."""
    content = file_path.read_text(encoding='utf-8')

    filename = file_path.name

    # Check if this file needs a name correction
    if filename in NAME_CORRECTIONS:
        old_title = re.search(r'^title_zh:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
        if old_title:
            old_value = old_title.group(1)
            new_value = NAME_CORRECTIONS[filename]
            if old_value != new_value:
                content = re.sub(
                    r'^title_zh:\s*["\']?.*?["\']?\s*$',
                    f'title_zh: "{new_value}"',
                    content,
                    flags=re.MULTILINE
                )
                print(f"  Fixed name: {old_value} -> {new_value}")
    else:
        # Convert any remaining Traditional characters
        match = re.search(r'^title_zh:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
        if match:
            old_value = match.group(1)
            new_value = convert_trad_to_simp(old_value)
            if old_value != new_value:
                content = re.sub(
                    r'^title_zh:\s*["\']?.*?["\']?\s*$',
                    f'title_zh: "{new_value}"',
                    content,
                    flags=re.MULTILINE
                )
                print(f"  Converted: {old_value} -> {new_value}")

    file_path.write_text(content, encoding='utf-8')

def main():
    print("Fixing Traditional Chinese to Simplified Chinese...")

    count = 0
    for md_file in KB_DIR.glob("*.md"):
        if md_file.name in ["index.md", "log.md", "overview.md"]:
            continue

        content = md_file.read_text(encoding='utf-8')

        # Check if file has Chinese characters that need conversion
        has_trad = any(c in content for c in '繁華馬羅裡溫約華龔薩爾維德克斯坦強沃瑪麗劉愛寧漢萊鮑納費')
        has_trad |= any(c in content for c in '喬治馬丁羅伯森羅裡默詹姆斯溫克爾曼')

        if has_trad:
            fix_file(md_file)
            count += 1

    print(f"Fixed {count} files")

if __name__ == '__main__':
    main()