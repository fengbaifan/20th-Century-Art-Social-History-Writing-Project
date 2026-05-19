#!/usr/bin/env python3
"""
Ingest Pipeline — Main entry point for knowledge base building
Processes JSON records into enriched Markdown with bilingual bidirectional links

Schema v2: Bilingual (Chinese/English), Personal Bibliography, Related Research
"""

import json
import re
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

# Global cache for all records (avoids O(n²) loading)
_ALL_RECORDS_CACHE = None
_ALL_RECORDS_CACHE_PATH = None


def log_info(msg):
    print(f"{BLUE}[INFO]{NC} {msg}")


def log_success(msg):
    print(f"{GREEN}[SUCCESS]{NC} {msg}")


def log_warn(msg):
    print(f"{YELLOW}[WARN]{NC} {msg}")


def log_error(msg):
    print(f"{RED}[ERROR]{NC} {msg}")


# Paths
SOURCE_DIR = PROJECT_ROOT / "RwaFiles" / "mid-data"
KB_DIR = PROJECT_ROOT / "knowledge-base"
GRAPH_DIR = PROJECT_ROOT / "graph"
CACHE_DIR = PROJECT_ROOT / ".processing" / "enrichment-cache"
ALL_RECORDS_CACHE_FILE = PROJECT_ROOT / ".processing" / "all_records.json"
LOG_FILE = KB_DIR / "log.md"
INDEX_FILE = KB_DIR / "index.md"

# Translation map for common terms
TRANSLATIONS = {
    # Countries
    "United States": "美国",
    "United Kingdom": "英国",
    "France": "法国",
    "Germany": "德国",
    "Italy": "意大利",
    "Spain": "西班牙",
    "Netherlands": "荷兰",
    "Belgium": "比利时",
    "Switzerland": "瑞士",
    "Austria": "奥地利",
    "Russia": "俄罗斯",
    "Japan": "日本",
    "China": "中国",
    "Canada": "加拿大",
    "Australia": "澳大利亚",

    # Subjects
    "American (North American)": "美国（北美）",
    "Modern (style or period)": "现代（风格或时期）",
    "Medieval": "中世纪",
    "Renaissance": "文艺复兴",
    "Baroque": "巴洛克",
    "Ancient": "古代",
    "Asian": "亚洲",
    "European": "欧洲",
    "art theory": "艺术理论",
    "Italian (culture or style)": "意大利（文化或风格）",
    "psychoanalysis": "精神分析",
    "psychology": "心理学",
    "Marxism": "马克思主义",
    "Gothic (Medieval)": "哥特式（中世纪）",
    "architecture (object genre)": "建筑（物品类型）",
    "sculpture (visual works)": "雕塑（视觉作品）",
    "decorative art (art genre)": "装饰艺术（艺术类型）",
    "African (general, continental cultures)": "非洲（一般、大陆文化）",
    "nineteenth century (dates CE)": "十九世纪（公元纪年）",
    "Rococo": "洛可可",
    "Romantic": "浪漫主义",
    "Impressionism": "印象派",
    "Expressionism": "表现主义",
    "Cubism": "立体主义",
    "Symbolism": "象征主义",
    "Neoclassicism": "新古典主义",
    "Realism": "现实主义",
    "Surrealism": "超现实主义",
    "Abstract": "抽象",
    "Contemporary": "当代",
    "Byzantine": "拜占庭",
    "Egyptian": "埃及",
    "Greek": "希腊",
    "Roman": "罗马",
    "Chinese": "中国",
    "Japanese": "日本",
    "Indian": "印度",
    "Islamic": "伊斯兰",
    "Pre-Columbian": "前哥伦布时期",
    "Native American": "美洲原住民",
    "Russian": "俄罗斯",
    "Dutch": "荷兰",
    "Flemish": "佛兰芒",
    "German": "德国",
    "French": "法国",
    "Spanish": "西班牙",
    "British": "英国",
    "American": "美国",
    "Swiss": "瑞士",
    "Austrian": "奥地利",
    "Belgian": "比利时",
    "Scandinavian": "斯堪的纳维亚",
    "Polish": "波兰",
    "Hungarian": "匈牙利",
    "Czech": "捷克",
    "Latin American": "拉丁美洲",
    "Oceania": "大洋洲",
    "Australian": "澳大利亚",
    "Canadian": "加拿大",
    "photography": "摄影",
    "film": "电影",
    "printmaking": "版画制作",
    "drawing": "Drawing",
    "painting": "绘画",
    "ceramics": "陶瓷",
    "textiles": "纺织",
    "glass": "玻璃",
    "metalwork": "金属工艺",
    "furniture": "家具",
    "jewelry": "珠宝",
    "Fashion": "时尚",
    "Museum studies": "博物馆研究",
    "Conservation": "文物保护",
    "Historiography": "史学",
    "Archaeology": "考古学",
    "Anthropology": "人类学",
    "Philosophy": "哲学",
    "Literature": "文学",
    "Music": "音乐",
    "Theater": "戏剧",
    "Dance": "舞蹈",
    "Cinema": "电影",
    "Graphic arts": "平面艺术",
    "Applied arts": "应用艺术",
    "Decorative arts": "装饰艺术",
    "Fine arts": "纯艺术",
    "Visual arts": "视觉艺术",
    "Performing arts": "表演艺术",
    "Arts and crafts movement": "工艺美术运动",
    "Art Nouveau": "新艺术运动",
    "Art Deco": "装饰艺术风格",
    "Bauhaus": "包豪斯",
    "Minimalism": "极简主义",
    "Conceptual art": "概念艺术",
    "Performance art": "行为艺术",
    "Installation art": "装置艺术",
    "Video art": "视频艺术",
    "Digital art": "数字艺术",
    "New media": "新媒体",
    "Feminist art": "女性主义艺术",
    "Queer art": "酷儿艺术",
    "Postcolonial art": "后殖民艺术",
    "Postmodernism": "后现代主义",
    "Modernism": "现代主义",
    "Avant-garde": "先锋派",
    "Academic art": "学院派艺术",
    "Landscape painting": "风景画",
    "Portrait painting": "肖像画",
    "Genre painting": "风俗画",
    "Still life": "静物画",
    "Religious art": "宗教艺术",
    "Mythology": "神话",
    "Allegory": "寓言",
    "Landscape": "风景",
    "Marine": "海洋",
    "Animal": "动物",
    "Flower painting": "花卉画",
    "Miniature": "微型画",
    "Mural": "壁画",
    "Tapestry": "挂毯",
    "Illumination": "彩饰",
    "Manuscript": "手稿",
    "Codex": "法典",
    "Icon": "圣像",
    "Altarpiece": "祭坛画",
    "Fresco": "湿壁画",
    "Panel painting": "板面画",
    "Oil painting": "油画",
    "Watercolor": "水彩",
    "Tempera": "蛋彩",
    "Acrylic": "丙烯",
    " gouache": "水粉",
    "Pastel": "粉彩",
    "Encaustic": "蜡彩",
    "Spray paint": "喷漆",
    "Collage": "拼贴",
    "Assemblage": "集合艺术",
    "Mosaic": "马赛克",
    "Relief": "浮雕",
    "Statue": "雕像",
    "Bust": "胸像",
    "Monument": "纪念碑",
    "Memorial": "纪念物",
    "Garden": "园林",
    "Interior": "室内",
    "Architectural history": "建筑史",
    "Urban planning": "城市规划",
    "Landscape architecture": "景观建筑",
    "Historic preservation": "历史保护",
    "Cultural heritage": "文化遗产",
    "World art": "世界艺术",
    "Comparative art": "比较艺术",
    "Cross-cultural": "跨文化",
    "Transnational": "跨国",
    "Global": "全球",
    "Regional": "区域",
    "Local": "本地",
    "National": "国家",
    "International": "国际",
    "Universal": "普遍",
    "Universalism": "普遍主义",
    "Particularism": "特殊主义",
    "Formalism": "形式主义",
    "Structuralism": "结构主义",
    "Post-structuralism": "后结构主义",
    "Deconstruction": "解构",
    "Semiotics": "符号学",
    "Hermeneutics": "诠释学",
    "Phenomenology": "现象学",
    "Aesthetics": "美学",
    "Criticism": "批评",
    "Theory": "理论",
    "Methodology": "方法论",
    "Pedagogy": "教育学",
    "Museum education": "博物馆教育",
    "Art education": "艺术教育",
    "Cataloging": "编目",
    "Classification": "分类",
    "Nomenclature": "命名法",
    "Terminology": "术语",
    "Biography": "传记",
    "Autobiography": "自传",
    "Diary": "日记",
    "Letter": "书信",
    "Document": "文献",
    "Archive": "档案",
    "Collection": "收藏",
    "Exhibition": "展览",
    "Display": "展示",
    "Presentation": "呈现",
    "Interpretation": "阐释",
    "Documentation": "文献记录",
    "Provenance": "出处",
    "Attribution": "归属",
    "Authentication": "鉴定",
    "Forgery": "伪造",
    "Replication": "复制",
    "Reproduction": "复制品",
    "Restoration": "修复",
    "Reconstruction": "重建",
    "Conservation science": "保护科学",
    "Materials analysis": "材料分析",
    "Technical art history": "技术艺术史",
    "Scientific examination": "科学检查",
    "X-ray": "X射线",
    "Infrared": "红外",
    "Ultraviolet": "紫外",
    "Photography (technical)": "摄影（技术）",
    "Dendrochronology": "树轮年代学",
    "Radiocarbon dating": "放射性碳定年",
    "Stylistic analysis": "风格分析",
    "Iconography": "图像学",
    "Iconology": "图像志",
    "Symbolic": "象征",
    "Allegorical": "寓言式",
    "Narrative": "叙事",
    "Figurative": "具象",
    "Non-representational": "非具象",
    "Abstraction": "抽象",
    "Non-objective": "无对象",
    "Geometric": "几何",
    "Organic": "有机",
    "Flowing": "流动",
    "Dynamic": "动态",
    "Static": "静态",
    "Symmetrical": "对称",
    "Asymmetrical": "不对称",
    "Balanced": "平衡",
    "Composed": "构图",
    "Spontaneous": "自发",
    "Controlled": "控制",
    "Expressive": "表现",
    "Reserved": "含蓄",
    "Decorative": "装饰",
    "Ornamental": "装饰性",
    "Functional": "功能",
    "Dysfunctional": "失功能",
    "Aesthetic": "审美",
    "Utilitarian": "实用",
    "Sacred": "神圣",
    "Secular": "世俗",
    "Religious": "宗教",
    "Devotional": "虔诚",
    "Ceremonial": "仪式",
    "Ritual": "礼节",
    "Magical": "魔法",
    "Mythological": "神话",
    "Historical": "历史",
    "Legendary": "传说",
    "Fictional": "虚构",
    "Documentary": "记录",
    "Symbolic (content)": "象征（内容）",
    "Allegorical (content)": "寓言（内容）",

    # Institutions
    "Harvard University": "哈佛大学",
    "Yale University": "耶鲁大学",
    "Princeton University": "普林斯顿大学",
    "Columbia University": "哥伦比亚大学",
    "MIT": "麻省理工学院",
    "Stanford University": "斯坦福大学",
    "Museum of Modern Art": "纽约现代艺术博物馆",
    "MoMA": "MoMA（现代艺术博物馆）",
    "Metropolitan Museum": "大都会艺术博物馆",
    "Smith College": "史密斯学院",
    "Bowdoin College": "鲍登学院",
    "Louvre": "卢浮宫",
    "British Museum": "大英博物馆",
    "National Gallery": "国家美术馆",
    "Pierpont Morgan Library": "皮尔庞特·摩根图书馆",
    "Colby College": "科尔比学院",
}

# Institution alias map (for deduplication)
INSTITUTION_ALIASES = {
    "Harvard": "Harvard University",
    "Yale": "Yale University",
    "Princeton": "Princeton University",
    "Columbia": "Columbia University",
    "Stanford": "Stanford University",
    "MoMA": "Museum of Modern Art",
    "Metropolitan": "Metropolitan Museum",
    "Bowdoin": "Bowdoin College",
}


def translate(text):
    """Translate English term to Chinese."""
    if not text:
        return ""
    return TRANSLATIONS.get(text, text)


def init_dirs():
    """Initialize required directories."""
    for d in [KB_DIR, GRAPH_DIR, CACHE_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.parent.mkdir(parents=True, exist_ok=True)


def strip_html(text):
    """Remove HTML tags from text."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def compute_hash(content):
    """Compute SHA256 hash of content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:12]


def load_json(filepath):
    """Load and parse JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    """Save data as JSON."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def title_to_shortcode(title):
    """Convert Title to unique shortcode using full name.

    Uses full name string (normalized) to avoid collisions.
    Examples:
        "Abell, Walter" -> "abell_walter"
        "Abraham, Karl" -> "abraham_karl"
        "Eastlake, Charles L." -> "eastlake_charles_l"
        "Eastlake, Charles Lock, Sir" -> "eastlake_charles_lock_sir"
        "Dinsmoor, William B., Jr." -> "dinsmoor_william_b_jr"
    """
    if not title:
        return None

    # Normalize: lowercase, replace spaces with underscores, remove special chars
    # Keep periods and initials intact to differentiate names
    safe = title.lower()
    # Replace spaces and commas with underscores
    safe = safe.replace(' ', '_').replace(',', '_')
    # Remove anything that's not alphanumeric or underscore
    safe = re.sub(r'[^a-z0-9_]', '', safe)
    # Clean up multiple underscores
    safe = re.sub(r'_+', '_', safe)
    # Remove leading/trailing underscores
    safe = safe.strip('_')
    return safe if safe else None


def parse_record(shortcode):
    """Parse JSON record from source."""
    json_file = SOURCE_DIR / f"{shortcode}.json"
    if not json_file.exists():
        raise FileNotFoundError(f"Source file not found: {json_file}")
    return load_json(json_file)


def get_enrichment_cache(shortcode):
    """Get cached enrichment data."""
    cache_file = CACHE_DIR / f"{shortcode}.json"
    if cache_file.exists():
        return load_json(cache_file)
    return None


def save_enrichment_cache(shortcode, data):
    """Save enrichment data to cache."""
    cache_file = CACHE_DIR / f"{shortcode}.json"
    save_json(cache_file, data)


def load_all_records(force=False):
    """Load all records from JSON files with caching to avoid O(n²)."""
    global _ALL_RECORDS_CACHE, _ALL_RECORDS_CACHE_PATH

    if _ALL_RECORDS_CACHE is not None and _ALL_RECORDS_CACHE_PATH == str(SOURCE_DIR) and not force:
        return _ALL_RECORDS_CACHE

    # Check cache file
    if not force and ALL_RECORDS_CACHE_FILE.exists():
        log_info("Loading all_records from cache...")
        _ALL_RECORDS_CACHE = load_json(ALL_RECORDS_CACHE_FILE)
        _ALL_RECORDS_CACHE_PATH = str(SOURCE_DIR)
        return _ALL_RECORDS_CACHE

    log_info("Loading all records...")
    all_records = {}
    for json_file in SOURCE_DIR.glob("*.json"):
        try:
            data = load_json(json_file)
            # Use JSON filename as key (not Title-derived shortcode)
            # This ensures wikilinks reference actual files on disk
            code = json_file.stem
            # Store Title-derived shortcode in the record for reference
            title = data.get('Title', '')
            title_shortcode = title_to_shortcode(title) if title else code
            data['_title_shortcode'] = title_shortcode
            data['_json_filename'] = code
            all_records[code] = data
        except Exception as e:
            log_warn(f"Failed to load {json_file.stem}: {e}")

    # Save to cache
    save_json(ALL_RECORDS_CACHE_FILE, all_records)
    _ALL_RECORDS_CACHE = all_records
    _ALL_RECORDS_CACHE_PATH = str(SOURCE_DIR)
    log_success(f"Loaded {len(all_records)} records")

    return all_records


def extract_institutions(text):
    """Extract institution names from text with deduplication."""
    found = set()
    known = [
        "Harvard University", "Harvard", "Yale", "Princeton", "Columbia", "MIT",
        "Stanford", "Museum of Modern Art", "MoMA", "Metropolitan Museum",
        "Smith College", "Bowdoin", "Louvre", "British Museum", "National Gallery",
        "Pierpont Morgan Library", "Colby College", "Oxford", "Cambridge"
    ]
    for inst in known:
        if inst.lower() in text.lower():
            # Normalize alias to canonical name
            canonical = INSTITUTION_ALIASES.get(inst, inst)
            found.add(canonical)
    return list(found)


def parse_bibliography(bib_text):
    """Parse bibliography text into structured entries."""
    entries = []
    if not bib_text:
        return entries

    # Pattern: Author. Title. Publisher, Year.
    # Split on patterns like "Author. " where Author is followed by Title
    # Better regex: split on citation boundaries
    parts = re.split(r'(?<=[.,;:])\s+(?=[A-Z][a-z]+[.,])', bib_text)

    for part in parts:
        part = part.strip()
        if not part or len(part) < 5:
            continue

        entry = {"text": part}

        # Extract year (various formats: (2023), 2023, c.2023)
        year_match = re.search(r'\(?(\d{4})\)?', part)
        if year_match:
            entry["year"] = year_match.group(1)

        # Extract author (first word before period)
        author_match = re.search(r'^([A-Z][a-z]+)', part)
        if author_match:
            entry["author"] = author_match.group(1)

        entries.append(entry)

    return entries


def compute_links(shortcode, json_data, all_records):
    """Compute bidirectional links for a scholar."""
    links = []

    name = json_data.get('Full Name', '') or json_data.get('Title', '')
    birth = json_data.get('Birth Year', '')
    subject = json_data.get('Subject Area', '')
    overview = json_data.get('Overview', '')

    for other_code, other_data in all_records.items():
        if other_code == shortcode:
            continue
        if not isinstance(other_data, dict):
            continue

        score = 0
        reasons = []

        # Institutional
        other_overview = other_data.get('Overview', '')
        inst_a = extract_institutions(overview)
        inst_b = extract_institutions(other_overview)
        shared = set(inst_a) & set(inst_b)
        if shared:
            score += 0.8
            reasons.append(f"shared institution: {list(shared)[0]}")

        # Temporal
        other_birth = other_data.get('Birth Year', '')
        if birth and other_birth:
            try:
                diff = abs(int(birth) - int(other_birth))
                if diff <= 10:
                    score += 0.6
                    reasons.append(f"temporal proximity ({birth}s vs {other_birth}s)")
            except ValueError:
                pass

        # Subject
        other_subject = other_data.get('Subject Area', '')
        if subject and other_subject:
            subj_a = set(s.strip().lower() for s in subject.split('|'))
            subj_b = set(s.strip().lower() for s in other_subject.split('|'))
            if subj_a & subj_b:
                score += 0.7
                reasons.append("shared subject area")

        # Textual mention
        other_name = other_data.get('Full Name', '') or other_data.get('Title', '')
        if name and other_name:
            if name.split(',')[0].strip().lower() in other_overview.lower():
                score += 0.4
                reasons.append("mentioned in other overview")

        if score >= 0.5:
            links.append({
                "target": other_code,
                "score": round(score, 2),
                "reasons": reasons
            })

    links.sort(key=lambda x: x["score"], reverse=True)
    return links[:10]


def write_markdown(shortcode, json_data, enrichment, links):
    """Write Markdown file with frontmatter and wikilinks."""

    # Extract fields
    raw_name = json_data.get('Full Name') or json_data.get('Title', 'Unknown')
    birth = json_data.get('Birth Year', '')
    death = json_data.get('Death Year', '')
    country = json_data.get('Home Country', '')
    gender = json_data.get('Gender', '')
    subject_area = json_data.get('Subject Area', '')
    overview = strip_html(json_data.get('Overview', ''))
    sources_text = strip_html(json_data.get('Selected Bibliography', ''))
    archives = strip_html(json_data.get('Archives', ''))

    # Convert "Last, First" to "First Last" format
    def format_full_name(raw):
        if ',' in raw:
            parts = raw.split(',')
            last_name = parts[0].strip()
            first_part = parts[1].strip()
            return f"{first_part} {last_name}"
        return raw

    full_name = format_full_name(raw_name)

    # Translate fields
    country_zh = translate(country)
    title_zh = translate(raw_name)  # Translate the raw name for Chinese
    subjects_seen = set()
    subjects = []
    if subject_area:
        for s in subject_area.split('|'):
            s = s.strip().strip('"')
            if s and s not in subjects_seen:
                subjects_seen.add(s)
                subjects.append(s)
                translated = translate(s)
                if translated and translated != s:  # Only add if translation exists and differs
                    subjects_seen.add(translated)
                    subjects.append(translated)

    # Extract institutions (deduplicated)
    institutions_data = extract_institutions(overview)
    institutions_formatted = []
    for inst in sorted(set(institutions_data)):  # sorted + set for consistency
        institutions_formatted.append(f"  - name: {inst}")
        institutions_formatted.append(f"    name_zh: {translate(inst)}")

    # Parse related research
    related_research = parse_bibliography(sources_text)

    # Enrichment data
    enriched = False
    enrich_data = {}
    if enrichment and enrichment.get('data'):
        enriched = True
        enrich_data = enrichment.get('data', {})

    # Personal bibliography (from enrichment)
    personal_bib = enrich_data.get('bibliography', []) if enriched else []

    # Build wikilinks
    wikilinks = []
    for link in links:
        target = link["target"]
        reason = link["reasons"][0] if link["reasons"] else "related"
        wikilinks.append(f"- [[{target}]] — {reason}")

    wikilinks_str = '\n'.join(wikilinks) if wikilinks else "  []"

    # Build frontmatter
    frontmatter = f"""---
full_name: "{full_name.replace('"', '\\"')}"
title_zh: "{title_zh.replace('"', '\\"')}"
birth: {birth if birth else 'null'}
death: {death if death else 'null'}
country: {country if country else 'null'}
country_zh: {country_zh if country_zh else 'null'}
gender: {gender if gender else 'null'}
field: art_history
field_zh: 艺术史

subjects:
{chr(10).join([f"  - {s}" for s in subjects]) if subjects else "  []"}
"""

    if institutions_formatted:
        frontmatter += f"""
institutions:
{chr(10).join(institutions_formatted)}
"""

    # Personal bibliography
    if personal_bib:
        frontmatter += "\n# 著作清单 / Personal Bibliography\n"
        for item in personal_bib:
            title = item.get('title', '')
            year = item.get('year', '')
            frontmatter += f"- **{title}** ({year})\n"
    else:
        frontmatter += "\n# 著作清单 / Personal Bibliography\n\n暂无 / None available\n"

    # Related research
    frontmatter += """
# 相关研究 / Related Research

"""
    if related_research:
        for entry in related_research:
            text = entry.get('text', '')
            year = entry.get('year', '')
            if year:
                frontmatter += f"- {text} ({year})\n"
            else:
                frontmatter += f"- {text}\n"
    else:
        frontmatter += "暂无 / None available\n"

    # Main content
    frontmatter += f"""---

# {full_name}

**{birth if birth else '?'}**–**{death if death else '?'}** | {country if country else 'Unknown'} {country_zh if country_zh else ''}

## 传记 / Biography

{overview if overview else 'No biography available. / 暂无传记。'}
"""

    if enrich_data.get('biography'):
        frontmatter += f"### 补充信息 / Additional Information\n\n{enrich_data['biography']}\n"

    frontmatter += f"""
## 档案 / Archives

{archives if archives else 'No archive information available. / 暂无档案信息。'}

## 相关学者 / Related Scholars

{wikilinks_str}

---

*Generated: {datetime.now(timezone.utc).isoformat()} | Source: {shortcode}.json*
"""

    output_file = KB_DIR / f"{shortcode}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(frontmatter)

    return output_file


def update_index():
    """Update index.md with all pages."""
    pages = []

    for md_file in KB_DIR.glob("*.md"):
        if md_file.name in ["index.md", "log.md", "overview.md"]:
            continue

        content = md_file.read_text(encoding='utf-8')

        match = re.search(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if match:
            fm = match.group(1)
            # Schema v2: use full_name and title_zh
            full_name_match = re.search(r'^full_name:\s*["\']?(.+?)["\']?\s*$', fm, re.MULTILINE)
            title_zh_match = re.search(r'^title_zh:\s*["\']?(.+?)["\']?\s*$', fm, re.MULTILINE)

            # Use filename (shortcode) as the wikilink target
            shortcode = md_file.stem
            # Use full_name as display name, title_zh as Chinese name
            display_name = full_name_match.group(1).strip() if full_name_match else shortcode
            chinese_name = title_zh_match.group(1).strip() if title_zh_match else ""

            birth_match = re.search(r'^birth:\s*(.+?)\s*$', fm, re.MULTILINE)
            birth = birth_match.group(1).strip() if birth_match else ""

            pages.append({
                "shortcode": shortcode,
                "display_name": display_name,
                "chinese_name": chinese_name,
                "birth": birth,
                "file": md_file.name
            })

    def sort_key(p):
        try:
            return (0, int(p['birth'])) if p['birth'] else (1, 0)
        except ValueError:
            return (1, 0)

    pages.sort(key=sort_key)

    index_content = """# Index

Auto-generated catalog of all art historians in the knowledge base.
艺术史学家知识库索引。

"""

    current_letter = None
    for page in pages:
        letter = page['display_name'][0].upper() if page['display_name'] else '#'
        if letter != current_letter:
            index_content += f"\n## {letter}\n\n"
            current_letter = letter

        birth_info = f" ({page['birth']})" if page['birth'] and page['birth'] != 'null' else ""
        chinese_info = f" ({page['chinese_name']})" if page['chinese_name'] else ""
        index_content += f"- [[{page['shortcode']}]] — {page['display_name']}{chinese_info}{birth_info}\n"

    INDEX_FILE.write_text(index_content, encoding='utf-8')
    return len(pages)


def append_log(operation, shortcode, details=""):
    """Append entry to log.md."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

    entry = f"## [{timestamp}] {operation} | {shortcode}\n"
    if details:
        entry += f"{details}\n"
    entry += "\n"

    if LOG_FILE.exists():
        existing = LOG_FILE.read_text(encoding='utf-8')
    else:
        existing = """---
name: log
title: "Operations Log"
---

# Log

Append-only chronological record of knowledge base operations.

Format: `## [YYYY-MM-DD HH:MM:SSZ] OPERATION | target`

---
"""

    LOG_FILE.write_text(existing + entry, encoding='utf-8')


def ingest_single(json_shortcode, all_records, force=False, continue_on_error=False):
    """Ingest a single scholar record.

    Args:
        json_shortcode: The shortcode derived from JSON filename (e.g., 'karl_abraham')
        all_records: Cached all_records data
        force: Force reprocess even if up to date
        continue_on_error: Continue on error
    """
    try:
        # Stage 0: Get record from all_records using JSON filename as key
        log_info(f"Processing: {json_shortcode}")
        if json_shortcode not in all_records:
            log_error(f"Record not found in all_records: {json_shortcode}")
            return False

        json_data = all_records[json_shortcode]
        title = json_data.get('Title', '')

        output_file = KB_DIR / f"{json_shortcode}.md"
        if not force and output_file.exists():
            source_mtime = (SOURCE_DIR / f"{json_shortcode}.json").stat().st_mtime
            output_mtime = output_file.stat().st_mtime
            if source_mtime <= output_mtime:
                log_info(f"Skipping (up to date): {json_shortcode}")
                return False

        # Stage 1: Parse
        log_info(f"[1/5] Parsing: {json_shortcode}")

        # Stage 2: Enrich (check cache first)
        log_info(f"[2/5] Checking enrichment: {json_shortcode}")
        enrichment = get_enrichment_cache(json_shortcode)

        if not enrichment:
            enrichment = {
                "shortcode": json_shortcode,
                "enriched_at": datetime.now(timezone.utc).isoformat(),
                "sources": {},
                "data": {}
            }
            save_enrichment_cache(json_shortcode, enrichment)

        # Stage 3: Compute links using cached all_records
        log_info(f"[3/5] Computing links: {json_shortcode}")
        links = compute_links(json_shortcode, json_data, all_records)

        # Stage 4: Write
        log_info(f"[4/5] Writing: {json_shortcode}")
        write_markdown(json_shortcode, json_data, enrichment, links)

        # Stage 5: Log
        log_info(f"[5/5] Logging: {json_shortcode}")
        append_log("INGEST", json_shortcode, f"Links: {len(links)}")

        log_success(f"Completed: {json_shortcode}")
        return True

    except Exception as e:
        log_error(f"Failed: {json_shortcode}: {e}")
        if continue_on_error:
            return False
        raise


def ingest_all(force=False, continue_on_error=False):
    """Ingest all scholar records."""
    if not SOURCE_DIR.exists():
        log_error(f"Source directory not found: {SOURCE_DIR}")
        return

    files = list(SOURCE_DIR.glob("*.json"))
    if not files:
        log_warn(f"No JSON files found in {SOURCE_DIR}")
        return

    log_info(f"Processing {len(files)} scholars...")

    # Load all records once (cached)
    all_records = load_all_records(force=force)

    count = 0
    failed = []
    for json_file in files:
        shortcode = json_file.stem
        try:
            if ingest_single(shortcode, all_records, force, continue_on_error):
                count += 1
        except Exception as e:
            log_error(f"Failed: {shortcode}: {e}")
            failed.append(shortcode)
            if not continue_on_error:
                break

    log_info("Updating index...")
    page_count = update_index()
    log_success(f"Indexed {page_count} pages")

    append_log("BATCH", "all", f"Processed {count}/{len(files)} scholars, {len(failed)} failed")
    log_success(f"Batch complete: {count} updated, {len(failed)} failed")

    if failed:
        log_warn(f"Failed: {', '.join(failed[:10])}{'...' if len(failed) > 10 else ''}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Art Historian Knowledge Base Ingest v2')
    parser.add_argument('--file', help='Process single scholar by shortcode')
    parser.add_argument('--all', action='store_true', help='Process all scholars')
    parser.add_argument('--force', action='store_true', help='Force reprocess')
    parser.add_argument('--continue-on-error', action='store_true', help='Continue on individual failures')

    args = parser.parse_args()

    init_dirs()

    if args.file:
        all_records = load_all_records()
        ingest_single(args.file, all_records, args.force)
    elif args.all:
        ingest_all(args.force, args.continue_on_error)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()