import os
import json
from collections import defaultdict

output_dir = r'C:\Users\001\Desktop\20th-Century-Art-Social-History-Writing-Project\art_historians_json'

print("=" * 70)
print("JSON 文件逐字段审查报告")
print("=" * 70)

# 获取所有JSON文件
json_files = [f for f in os.listdir(output_dir) if f.endswith('.json') and f != 'index.json']

# 定义所有可能字段
all_fields = set()
field_stats = defaultdict(lambda: {
    'total': 0,
    'empty': 0,
    'samples': [],
    'min_len': float('inf'),
    'max_len': 0
})

# 逐文件分析
for i, filename in enumerate(json_files):
    filepath = os.path.join(output_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for field, value in data.items():
            all_fields.add(field)
            stats = field_stats[field]
            stats['total'] += 1
            
            str_value = str(value).strip() if value else ''
            field_len = len(str_value)
            
            stats['min_len'] = min(stats['min_len'], field_len)
            stats['max_len'] = max(stats['max_len'], field_len)
            
            if not str_value:
                stats['empty'] += 1
            elif len(stats['samples']) < 3:
                stats['samples'].append(str_value[:100])
                
    except Exception as e:
        print(f"错误处理文件 {filename}: {e}")
    
    if (i + 1) % 500 == 0:
        print(f"已处理 {i + 1} / {len(json_files)} 文件...")

print(f"\n总计检查文件数: {len(json_files)}")
print("\n" + "=" * 70)
print("字段完整性统计")
print("=" * 70)

# 按字段统计
field_analysis = []
for field in sorted(all_fields):
    stats = field_stats[field]
    fill_rate = (stats['total'] - stats['empty']) / stats['total'] * 100 if stats['total'] > 0 else 0
    field_analysis.append({
        'field': field,
        'total': stats['total'],
        'filled': stats['total'] - stats['empty'],
        'empty': stats['empty'],
        'fill_rate': fill_rate,
        'min_len': stats['min_len'],
        'max_len': stats['max_len'],
        'samples': stats['samples']
    })

# 按填充率排序
field_analysis.sort(key=lambda x: x['fill_rate'], reverse=True)

print(f"\n{'字段名称':<30} {'填充率':<10} {'已填':<8} {'空值':<8} {'最小长度':<10} {'最大长度':<10}")
print("-" * 70)

for item in field_analysis:
    print(f"{item['field']:<30} {item['fill_rate']:>6.1f}% {item['filled']:>6} {item['empty']:>6} {item['min_len']:>8} {item['max_len']:>10}")

# 重点字段详细分析
print("\n" + "=" * 70)
print("关键字段详细分析")
print("=" * 70)

key_fields = ['Full Name', 'Birth Year', 'Death Year', 'Home Country', 'Gender', 
              'Subject Area', 'Overview', 'Selected Bibliography', 'Sources', 'Archives']

for field in key_fields:
    if field in field_stats:
        stats = field_stats[field]
        fill_rate = (stats['total'] - stats['empty']) / stats['total'] * 100 if stats['total'] > 0 else 0
        
        print(f"\n【{field}】")
        print(f"  填充率: {fill_rate:.1f}%")
        print(f"  数据量: {stats['total']} 条")
        
        if stats['samples']:
            print(f"  示例数据:")
            for i, sample in enumerate(stats['samples'], 1):
                print(f"    {i}. {sample}...")
        
        # 字段特定分析
        if field == 'Birth Year' or field == 'Death Year':
            years = []
            for filename in json_files[:100]:
                filepath = os.path.join(output_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    year = data.get(field, '')
                    if year:
                        years.append(year)
                except:
                    pass
            
            if years:
                print(f"  年份样本: {', '.join(set(years[:20]))}")
                
        elif field == 'Gender':
            gender_counts = defaultdict(int)
            for filename in json_files:
                filepath = os.path.join(output_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    gender = data.get(field, '')
                    if gender:
                        gender_counts[gender] += 1
                except:
                    pass
            
            print(f"  性别分布:")
            for gender, count in sorted(gender_counts.items(), key=lambda x: x[1], reverse=True):
                pct = count / sum(gender_counts.values()) * 100
                print(f"    - {gender}: {count} ({pct:.1f}%)")
                
        elif field == 'Home Country':
            country_counts = defaultdict(int)
            for filename in json_files:
                filepath = os.path.join(output_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    country = data.get(field, '')
                    if country:
                        country_counts[country] += 1
                except:
                    pass
            
            print(f"  国家分布 (前10):")
            for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                pct = count / sum(country_counts.values()) * 100
                print(f"    - {country}: {count} ({pct:.1f}%)")
                
        elif field == 'Subject Area':
            subject_counts = defaultdict(int)
            for filename in json_files:
                filepath = os.path.join(output_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    subjects = data.get(field, '').split('|')
                    for s in subjects:
                        s = s.strip()
                        if s:
                            subject_counts[s] += 1
                except:
                    pass
            
            print(f"  研究领域分布 (前15):")
            for subject, count in sorted(subject_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
                pct = count / sum(subject_counts.values()) * 100
                print(f"    - {subject}: {count} ({pct:.1f}%)")

# 数据质量检查
print("\n" + "=" * 70)
print("数据质量检查")
print("=" * 70)

# 检查必填字段
required_fields = ['Full Name']
missing_required = []

for filename in json_files:
    filepath = os.path.join(output_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for field in required_fields:
            if not data.get(field, '').strip():
                missing_required.append((filename, field))
    except:
        pass

if missing_required:
    print(f"\n⚠️ 发现 {len(missing_required)} 个文件缺少必填字段:")
    for filename, field in missing_required[:10]:
        print(f"  - {filename}: {field}")
else:
    print("\n✅ 所有文件都包含必填字段")

# 检查年份格式
print(f"\n年份格式检查:")
year_errors = []
for filename in json_files:
    filepath = os.path.join(output_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for year_field in ['Birth Year', 'Death Year']:
            year = data.get(year_field, '').strip()
            if year:
                try:
                    year_int = int(year)
                    if year_int < 1800 or year_int > 2000:
                        year_errors.append((filename, year_field, year))
                except ValueError:
                    if year.lower() != 'unknown':
                        year_errors.append((filename, year_field, year))
    except:
        pass

if year_errors:
    print(f"  ⚠️ 发现 {len(year_errors)} 个年份格式异常:")
    for filename, field, year in year_errors[:10]:
        print(f"    - {filename}: {field} = '{year}'")
else:
    print("  ✅ 年份格式正确")

print("\n" + "=" * 70)
print("审查完成")
print("=" * 70)
