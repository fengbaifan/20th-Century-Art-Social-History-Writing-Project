#!/usr/bin/env python3
"""
Ingest Pipeline — Main entry point for knowledge base building
Processes JSON records into enriched Markdown with bilingual bidirectional links

Schema v3:
- Pinyin transliteration for Chinese names
- Chicago format bibliography (17th ed.)
- Full bilingual content (English primary, Chinese translation)
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

# Pinyin transliteration for common Western name parts
PINYIN_NAME_MAP = {
    # First names / given names
    "john": "约翰", "james": "詹姆斯", "robert": "罗伯特", "michael": "迈克尔",
    "david": "戴维", "william": "威廉", "richard": "理查德", "charles": "查尔斯",
    "joseph": "约瑟夫", "thomas": "托马斯", "christopher": "克里斯托弗",
    "daniel": "丹尼尔", "matthew": "马修", "anthony": "安东尼", "mark": "马克",
    "donald": "唐纳德", "steven": "史蒂文", "paul": "保罗", "andrew": "安德鲁",
    "joshua": "乔舒亚", "kenneth": "肯尼思", "kevin": "凯文", "brian": "布莱恩",
    "george": "乔治", "edward": "爱德华", "ronald": "罗纳德", "timothy": "蒂莫西",
    "jason": "贾森", "jeffrey": "杰弗里", "ryan": "瑞安", "jacob": "雅各布",
    "gary": "加里", "nicholas": "尼古拉斯", "eric": "埃里克", "jonathan": "乔纳森",
    "stephen": "斯蒂芬", "larry": "拉里", "justin": "贾斯汀", "scott": "斯科特",
    "brandon": "布兰登", "benjamin": "本杰明", "samuel": "塞缪尔", "raymond": "雷蒙德",
    "gregory": "格雷戈里", "frank": "弗兰克", "alexander": "亚历山大", "patrick": "帕特里克",
    "jack": "杰克", "dennis": "丹尼斯", "jerry": "杰里", "tyler": "泰勒",
    "aaron": "艾伦", "jose": "何塞", "adam": "亚当", "nathan": "内森",
    "henry": "亨利", "douglas": "道格拉斯", "zachary": "扎卡里", "peter": "彼得",
    "kyle": "凯尔", "noah": "诺亚", "wayne": "韦恩", "eugene": "尤金",
    "russell": "拉塞尔", "bobby": "博比", "mason": "梅森", "logan": "洛根",
    "albert": "艾伯特", "warren": "沃伦", "emmett": "埃米特", "harrison": "哈里森",
    "arthur": "阿瑟", "calvin": "卡尔文", "carl": "卡尔", "lawrence": "劳伦斯",
    "jerome": "杰罗姆", "roland": "罗兰", "harold": "哈罗德", "vernon": "弗农",
    "edmund": "埃德蒙", "frederick": "弗雷德里克", "gerald": "杰拉尔德", "ralph": "拉尔夫",
    "rachel": "雷切尔", "claire": "克莱尔", "agnes": "阿格尼丝", "anna": "安娜",
    "anne": "安妮", "beatrice": "比阿特丽斯", "catherine": "凯瑟琳", "christine": "克里斯廷",
    "dorothy": "多萝西", "elizabeth": "伊丽莎白", "ellen": "埃伦", "emily": "埃米莉",
    "esther": "埃丝特", "eugenia": "尤金尼亚", "eva": "伊娃", "florence": "弗洛伦斯",
    "helen": "海伦", "irene": "艾琳", "jane": "简", "joan": "琼",
    "julia": "朱莉娅", "katherine": "凯瑟琳", "laura": "劳拉", "lillian": "莉莲",
    "linda": "琳达", "louise": "路易丝", "margaret": "玛格丽特", "maria": "玛丽亚",
    "martha": "玛莎", "mary": "玛丽", "mildred": "米尔德丽德", "nancy": "南希",
    "nora": "诺拉", "norma": "诺尔玛", "olivia": "奥利维亚", "pauline": "波琳",
    "phyllis": "菲利斯", "priscilla": "普里西拉", "rebecca": "丽贝卡", "rose": "罗丝",
    "ruth": "露丝", "sarah": "萨拉", "shirley": "雪莉", "sophia": "索菲娅",
    "susan": "苏珊", "margery": "玛吉", "mabel": "梅布尔", "ada": "艾达",
    "adeline": "阿德琳", "adolf": "阿道夫", "adolph": "阿道夫",
    # Last names / surnames
    "smith": "史密斯", "johnson": "约翰逊", "williams": "威廉姆斯", "brown": "布朗",
    "jones": "琼斯", "garcia": "加西亚", "miller": "米勒", "davis": "戴维斯",
    "rodriguez": "罗德里格斯", "martinez": "马丁内斯", "hernandez": "埃尔南德斯",
    "lopez": "洛佩斯", "gonzalez": "冈萨雷斯", "wilson": "威尔逊", "anderson": "安德森",
    "thomas": "托马斯", "taylor": "泰勒", "moore": "穆尔", "jackson": "杰克逊",
    "martin": "马丁", "lee": "李", "perez": "佩雷斯", "thompson": "汤普森",
    "white": "怀特", "harris": "哈里斯", "sanchez": "桑切斯", "clark": "克拉克",
    "ramirez": "拉米雷斯", "lewis": "刘易斯", "robinson": "鲁滨逊", "walker": "沃克",
    "young": "扬", "allen": "艾伦", "king": "金", "wright": "赖特",
    "scott": "斯科特", "torres": "托雷斯", "nguyen": "阮", "hill": "希尔",
    "flores": "弗洛雷斯", "green": "格林", "adams": "亚当斯", "nelson": "纳尔逊",
    "baker": "贝克", "hall": "霍尔", "rivera": "里维拉", "campbell": "坎贝尔",
    "mitchell": "米切尔", "carter": "卡特", "roberts": "罗伯茨", "gomez": "戈麦斯",
    "phillips": "菲利普斯", "evans": "埃文斯", "turner": "特纳", "diaz": "迪亚兹",
    "parker": "帕克", "cruz": "克鲁兹", "edwards": "爱德华兹", "collins": "柯林斯",
    "reyes": "雷耶斯", "stewart": "斯图尔特", "morris": "莫里斯", "morales": "莫拉莱斯",
    "murphy": "墨菲", "cook": "库克", "rogers": "罗杰斯", "gutierrez": "古铁雷斯",
    "ortiz": "奥尔蒂斯", "morgan": "摩根", "cooper": "库珀", "peterson": "彼得森",
    "bailey": "贝利", "reed": "里德", "kelly": "凯利", "howard": "霍华德",
    "ramos": "拉莫斯", "kim": "金", "cox": "考克斯", "ward": "沃德",
    "richardson": "理查森", "watson": "沃森", "brooks": "布鲁克斯", "chavez": "查韦斯",
    "wood": "伍德", "james": "詹姆斯", "bennett": "贝内特", "gray": "格雷",
    "mendoza": "门多萨", "ruiz": "鲁伊斯", "hughes": "休斯", "price": "普赖斯",
    "alvarez": "阿尔瓦雷斯", "castillo": "卡斯蒂略", "sanders": "桑德斯", "patel": "帕特尔",
    "myers": "迈尔斯", "long": "朗", "ross": "罗斯", "foster": "福斯特",
    "jimenez": "希门尼斯", "powell": "鲍威尔", "jenkins": "詹金斯", "perry": "佩里",
    "russell": "拉塞尔", "sullivan": "沙利文", "bell": "贝尔", "coleman": "科尔曼",
    "butler": "巴特勒", "henderson": "亨德森", "barnes": "巴恩斯", "gonzales": "冈萨尔斯",
    "fisher": "费希尔", "vasquez": "巴斯克斯", "simmons": "西蒙斯", "garrett": "加勒特",
    "burke": "伯克", "olson": "奥尔森", "simpson": "辛普森", "porter": "波特",
    "mason": "梅森", "moreno": "莫雷诺", "hansen": "汉森", "obrien": "奥布赖恩",
    "hunt": "亨特", "mcdonald": "麦克唐纳", "crawford": "克劳福德", "gibson": "吉布森",
    "armstrong": "阿姆斯特朗", "wagner": "瓦格纳", "webb": "韦布", "austin": "奥斯汀",
    "wells": "威尔斯", "kennedy": "肯尼迪", "parsons": "帕森斯", "cole": "科尔",
    "blake": "布莱克", "cross": "克罗斯", "harrison": "哈里森", "morris": "莫里斯",
    "hicks": "希克斯", "houston": "休斯顿", "perez": "佩雷斯", "morrison": "莫里森",
    "cunningham": "坎宁安", "banks": "班克斯", "fowler": "福勒", "murray": "默里",
    "mitchell": "米切尔", "palmer": "帕尔默", "cahill": "卡希尔", "marsh": "马什",
    "burch": "伯奇", "fletcher": "弗莱彻", "floyd": "弗洛伊德", "hammond": "哈蒙德",
    "harrison": "哈里森", "harmon": "哈蒙", "hayes": "海斯", "holt": "霍尔特",
    "hood": "胡德", "hooker": "胡克", "horn": "霍恩", "huber": "胡贝尔",
    "huffman": "赫夫曼", "hughes": "休斯", "keller": "凯勒", "kelley": "凯利",
    "kennedy": "肯尼迪", "kent": "肯特", "kerr": "克尔",
    # Art historian specific names
    "panofsky": "潘诺夫斯基", "warburg": "瓦尔堡", "riegl": "里格尔", "worringer": "沃林格",
    "hauser": "豪泽", "antal": "安塔尔", "gombrich": "贡布里希", "clark": "克拉克",
    "friedlnder": "弗里德伦德尔", "blunt": "布伦特", "waterhouse": "沃特豪斯", "poiler": "波伊勒",
    "bingham": "宾厄姆", "crespon": "克雷 respons", "kubler": "库布勒",
    "janson": "詹森", "janson's": "詹森的", "paolo": "保罗", "tucci": "图奇",
    "sebastiano": "塞巴斯蒂亚诺", "del serra": "德尔塞拉", "friedl": "弗里德尔",
    "bene": "贝内", "charl": "查尔", "eliza": "伊莱扎", "blythe": "布莱思",
    "borg": "博格", "alborg": "阿尔博格", "ferrero": "费雷罗", "mann": "曼",
    "wolff": "沃尔夫", "metzger": "梅策尔", "schrade": "施拉德", "schneider": "施奈德",
    "loe": "洛", "sloane": "斯隆", "harrsen": "哈尔森", "ferguson": "弗格森",
}

# Common surname prefixes that need special handling
SURNAME_PREFIXES = ["de", "del", "da", "di", "van", "von", "der", "den", "le", "la", "O'", "Mc", "Mac"]


def transliterate_name_to_pinyin(full_name):
    """
    Transliterate a Western name to Chinese pinyin.
    Handles "Last, First" and "First Last" formats.
    Returns (surname_pinyin, given_name_pinyin) or None if unable.
    """
    if not full_name:
        return None

    # Clean the name
    name = full_name.strip()
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'[.,]', ' ', name)
    name = name.strip()

    # Determine format
    if ',' in name:
        # "Last, First" format
        parts = name.split(',')
        surname = parts[0].strip()
        given_name = parts[1].strip() if len(parts) > 1 else ""
    else:
        # "First Last" format
        parts = name.split()
        surname = parts[-1].strip() if parts else ""
        given_name = ' '.join(parts[:-1]) if len(parts) > 1 else ""

    surname_lower = surname.lower()
    given_lower = given_name.lower()

    # Check if surname is in our map
    surname_zh = None
    for key, value in PINYIN_NAME_MAP.items():
        if surname_lower == key.lower():
            surname_zh = value
            break

    # Transliterate given name parts
    given_parts = given_name.split()
    given_zh_parts = []
    for part in given_parts:
        part_clean = re.sub(r'[^a-zA-Z]', '', part).lower()
        for key, value in PINYIN_NAME_MAP.items():
            if part_clean == key.lower():
                given_zh_parts.append(value)
                break

    if surname_zh and given_zh_parts:
        # Chinese name order: surname + given name
        return f"{surname_zh}{''.join(given_zh_parts)}"
    elif surname_zh:
        return surname_zh
    elif given_zh_parts:
        return ''.join(given_zh_parts)

    return None


def format_name_for_display(full_name, title_zh):
    """
    Format name for display.
    If title_zh is valid Chinese, use it directly.
    Otherwise, transliterate the Western name.
    """
    if title_zh and re.search(r'[一-鿿]', title_zh):
        return title_zh

    # Try transliteration
    pinyin = transliterate_name_to_pinyin(full_name)
    if pinyin:
        return pinyin

    return full_name


# Translation map for common terms (abbreviated - same as before)
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
    # ... (keep all existing translations)
}

# Institution alias map (for deduplication)
INSTITUTION_ALIASES = {
    "Harvard": "Harvard University",
    "MoMA": "Museum of Modern Art",
    "Met": "Metropolitan Museum",
    "NGA": "National Gallery of Art",
    "Louvre": "Musée du Louvre",
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


def format_chicago_bibliography(entries, entry_type='book'):
    """
    Format bibliography entries in Chicago Manual of Style 17th edition format.

    Book: Author. *Title*. Place: Publisher, Year.
    Article: Author. "Title." *Journal* Volume, no. Issue (Year): Pages.
    """
    formatted = []

    for entry in entries:
        text = entry.get('text', '')
        if not text:
            continue

        # Try to parse and reformat
        formatted_entry = parse_chicago_entry(text)
        formatted.append(formatted_entry)

    return formatted


def parse_chicago_entry(text):
    """
    Parse a bibliography entry and reformat to Chicago style.
    Returns formatted string.
    """
    if not text:
        return text

    # Clean up the text
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)

    # If it already looks like Chicago style (has periods in right places), leave it
    if re.match(r'^[A-Z][a-z]+.*\.\s*.+\.\s*[A-Z][a-z]+.*,\s*\d{4}', text):
        return text

    # Try to extract components
    # Pattern: Author(s). Title. Publisher, Year.
    match = re.match(r'^([^(]+?)\s*\(([^)]+)\)?)\s*[-–]\s*(.+)', text)
    if match:
        author = match.group(1).strip()
        year = match.group(2).strip()
        title = match.group(3).strip()

        # If title is in quotes or italics markers, format accordingly
        if title.startswith('"') and title.endswith('"'):
            return f"{author}. {title}. {year}."
        else:
            return f"{author}. *{title}*. {year}."

    # Return original if can't parse
    return text


def format_bibliography_item(entry):
    """
    Format a single bibliography entry in proper Chicago style.
    """
    text = entry.get('text', '')
    year = entry.get('year', '')

    if not text:
        return None

    # Clean trailing year in parentheses if present
    text = re.sub(r'\s*\(\d{4}\)\s*$', '', text).strip()
    text = re.sub(r',\s*\d{4}\s*$', '', text).strip()

    # Add year back in Chicago format
    if year:
        # Check if text already ends with year
        if not re.search(r'\d{4}\.?$', text):
            text = f"{text}. {year}."

    return text


def load_all_records():
    """Load all records from cache or source directory."""
    global _ALL_RECORDS_CACHE, _ALL_RECORDS_CACHE_PATH

    if _ALL_RECORDS_CACHE is not None:
        return _ALL_RECORDS_CACHE

    cache_file = ALL_RECORDS_CACHE_FILE
    if cache_file.exists():
        log_info("Loading all_records from cache...")
        with open(cache_file, 'r', encoding='utf-8') as f:
            _ALL_RECORDS_CACHE = json.load(f)
        _ALL_RECORDS_CACHE_PATH = str(cache_file)
        return _ALL_RECORDS_CACHE

    # Fallback: load from source directory
    log_info("Loading from source directory...")
    records = {}
    for json_file in SOURCE_DIR.glob("*.json"):
        if json_file.name == "README.md":
            continue
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            shortcode = json_file.stem
            records[shortcode] = data

    _ALL_RECORDS_CACHE = records
    _ALL_RECORDS_CACHE_PATH = None
    return records


def get_record(shortcode):
    """Get a single record by shortcode."""
    records = load_all_records()
    return records.get(shortcode)


def compute_shortcode(title):
    """Compute shortcode from title (first author's last name + first word of title)."""
    if not title:
        return "unknown"

    # Take first author's last name
    author_match = re.match(r'^([^,]+)', title)
    if author_match:
        author = author_match.group(1).strip()
        # Get last word (last name)
        parts = author.split()
        if parts:
            last_name = parts[-1].lower()
            last_name = re.sub(r'[^a-z]', '', last_name)
            return last_name

    return "unknown"


def compute_links(shortcode, all_records):
    """Compute bidirectional links with weighted scoring."""
    if shortcode not in all_records:
        return []

    record = all_records[shortcode]
    subjects = set(s.strip().lower() for s in record.get('Subject Area', '').split('|') if s.strip())
    institutions = set()
    for inst_list in record.get('Institutions', '').values():
        for inst in inst_list:
            inst = inst.strip().lower()
            if inst:
                institutions.add(inst)

    birth = record.get('Birth Year')
    try:
        birth = int(birth) if birth else None
    except:
        birth = None

    links = []
    for other_shortcode, other in all_records.items():
        if other_shortcode == shortcode:
            continue

        score = 0
        reasons = []

        # Institutional connection (weight: 0.8)
        other_institutions = set()
        for inst_list in other.get('Institutions', '').values():
            for inst in inst_list:
                inst = inst.strip().lower()
                if inst:
                    other_institutions.add(inst)
        shared_inst = institutions & other_institutions
        if shared_inst:
            score += 0.8
            reasons.append(f"shared institution: {list(shared_inst)[0]}")

        # Subject similarity (weight: 0.7)
        other_subjects = set(s.strip().lower() for s in other.get('Subject Area', '').split('|') if s.strip())
        shared_subj = subjects & other_subjects
        if shared_subj:
            score += 0.7
            reasons.append(f"shared subject: {list(shared_subj)[0]}")

        # Temporal proximity (weight: 0.6)
        other_birth = other.get('Birth Year')
        try:
            other_birth = int(other_birth) if other_birth else None
        except:
            other_birth = None
        if birth and other_birth and abs(birth - other_birth) <= 10:
            score += 0.6
            reasons.append(f"contemporary (±10 years)")

        if score >= 0.5:
            links.append({
                "target": other_shortcode,
                "score": score,
                "reasons": reasons
            })

    # Sort by score, take top 10
    links.sort(key=lambda x: x['score'], reverse=True)
    return links[:10]


def process_record(shortcode, force=False):
    """Process a single record into Markdown."""
    record = get_record(shortcode)
    if not record:
        log_warn(f"Record not found: {shortcode}")
        return False

    output_file = KB_DIR / f"{shortcode}.md"

    # Check if up to date (skip if not forcing)
    if not force and output_file.exists():
        # Simple timestamp check
        file_mtime = output_file.stat().st_mtime
        source_mtime = SOURCE_DIR / f"{shortcode}.json"
        if source_mtime.exists() and source_mtime.stat().st_mtime < file_mtime:
            log_info(f"Skipping (up to date): {shortcode}")
            return True

    log_info(f"Processing: {shortcode}")

    # Load enrichment if available
    enrichment = None
    cache_file = CACHE_DIR / f"{shortcode}.json"
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            enrichment = json.load(f)

    # Parse record
    json_data = record
    raw_name = json_data.get('Full Name', '')
    birth = json_data.get('Birth Year')
    death = json_data.get('Death Year')
    country = json_data.get('Country', '')
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

    # Get Chinese name
    # Priority: enrichment data > transliteration > "待补充"
    title_zh = None
    if enrichment and enrichment.get('data', {}).get('chinese_name'):
        title_zh = enrichment['data']['chinese_name']
    else:
        # Try transliteration
        title_zh = transliterate_name_to_pinyin(raw_name)
        if not title_zh:
            title_zh = "待补充"

    # Translate fields
    country_zh = translate(country)
    subjects_seen = set()
    subjects = []
    if subject_area:
        for s in subject_area.split('|'):
            s = s.strip().strip('"')
            if s and s not in subjects_seen:
                subjects_seen.add(s)
                subjects.append(s)
                translated = translate(s)
                if translated and translated != s:
                    subjects_seen.add(translated)
                    subjects.append(translated)

    # Extract institutions (deduplicated)
    institutions_raw = json_data.get('Institutions', {})
    institutions_formatted = []
    institutions_seen = set()
    for inst_name, inst_zh in institutions_raw.items():
        if not inst_name:
            continue
        inst_name_clean = INSTITUTION_ALIASES.get(inst_name, inst_name)
        if inst_name_clean in institutions_seen:
            continue
        institutions_seen.add(inst_name_clean)
        inst_zh_text = inst_zh[0] if inst_zh else translate(inst_name)
        institutions_formatted.append(f"  - name: {inst_name_clean}")
        institutions_formatted.append(f"    name_zh: {inst_zh_text}")

    # Parse bibliography
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
    all_records = load_all_records()
    links = compute_links(shortcode, all_records)
    wikilinks = []
    for link in links:
        target = link["target"]
        reason = link["reasons"][0] if link["reasons"] else "related"
        wikilinks.append(f"- [[{target}]] — {reason}")

    wikilinks_str = '\n'.join(wikilinks) if wikilinks else "  []"

    # Generate Chinese biography (abbreviated translation of overview)
    overview_zh = ""
    if overview:
        # For now, mark as needing translation
        # In production, this would use an LLM or translation API
        overview_zh = f"[英] {overview[:200]}..." if len(overview) > 200 else f"[英] {overview}"
        if overview_zh.endswith('...'):
            overview_zh = overview_zh[:-3] + "... [待翻译 / Translation pending]"

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

    frontmatter += "\n---\n"

    # Personal bibliography in Chicago format
    frontmatter += "\n# 著作清单 / Personal Bibliography\n\n"
    if personal_bib:
        for item in personal_bib:
            formatted = format_bibliography_item(item)
            if formatted:
                frontmatter += f"- {formatted}\n"
    else:
        frontmatter += "暂无 / None available\n"

    # Related research in Chicago format
    frontmatter += "\n# 相关研究 / Related Research\n\n"
    if related_research:
        for entry in related_research:
            formatted = format_bibliography_item(entry)
            if formatted:
                frontmatter += f"- {formatted}\n"
    else:
        frontmatter += "暂无 / None available\n"

    # Main content with bilingual structure
    frontmatter += f"""# {full_name}

**{birth if birth else '?'}**–**{death if death else '?'}** | {country if country else 'Unknown'} {country_zh if country_zh else ''}

## 传记 / Biography

### English

{overview if overview else 'No biography available.'}

### 中文

{overview_zh if overview_zh else '暂无中文翻译 / No Chinese translation available.'}

## 档案 / Archives

{archives if archives else 'No archive information available. / 暂无档案信息。'}

## 相关学者 / Related Scholars

{wikilinks_str}

---

*Generated: {datetime.now(timezone.utc).isoformat()} | Source: {shortcode}.json*
"""

    # Write output
    output_file.write_text(frontmatter, encoding='utf-8')
    log_success(f"Completed: {shortcode}")
    return True


def parse_bibliography(bib_text):
    """Parse bibliography text into structured entries."""
    entries = []
    if not bib_text:
        return entries

    # Split on citation boundaries
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


def append_to_log(shortcode, action="processed"):
    """Append entry to operation log."""
    timestamp = datetime.now(timezone.utc).isoformat()
    log_entry = f"- `{timestamp}` {action}: [[{shortcode}]]\n"

    if LOG_FILE.exists():
        content = LOG_FILE.read_text(encoding='utf-8')
    else:
        content = "---\ntitle: \"Operation Log\"\n---\n\n# Operation Log\n\n"

    content += log_entry
    LOG_FILE.write_text(content, encoding='utf-8')


def process_all(force=False, continue_on_error=False):
    """Process all records."""
    records = load_all_records()
    log_info(f"Processing {len(records)} records...")

    success = 0
    failed = 0

    for i, shortcode in enumerate(sorted(records.keys())):
        try:
            result = process_record(shortcode, force=force)
            if result:
                success += 1
                append_to_log(shortcode, "processed" if not force else "reprocessed")
            else:
                failed += 1
        except Exception as e:
            log_error(f"Error processing {shortcode}: {e}")
            failed += 1
            if not continue_on_error:
                raise

        if (i + 1) % 100 == 0:
            log_info(f"Progress: {i + 1}/{len(records)}")

    log_success(f"Completed: {success} success, {failed} failed")
    return success, failed


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Ingest pipeline for knowledge base')
    parser.add_argument('--file', type=str, help='Process single file (shortcode)')
    parser.add_argument('--all', action='store_true', help='Process all records')
    parser.add_argument('--force', action='store_true', help='Force reprocess')
    parser.add_argument('--continue-on-error', action='store_true', help='Continue on error')

    args = parser.parse_args()

    init_dirs()

    if args.file:
        process_record(args.file, force=True)
    elif args.all:
        process_all(force=args.force, continue_on_error=args.continue_on_error)
    else:
        parser.print_help()


if __name__ == '__main__':
    sys.exit(main())
