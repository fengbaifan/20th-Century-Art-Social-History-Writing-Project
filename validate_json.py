import os
import json

output_dir = r'C:\Users\001\Desktop\20th-Century-Art-Social-History-Social-History-Writing-Project\art_historians_json'

print("=" * 60)
print("JSON 文件复查报告")
print("=" * 60)

# 1. 检查文件数量
json_files = [f for f in os.listdir(output_dir) if f.endswith('.json') and f != 'index.json']
print(f"\n1. 文件数量检查:")
print(f"   JSON数据文件数量: {len(json_files)}")

# 2. 检查索引文件
index_file = os.path.join(output_dir, 'index.json')
if os.path.exists(index_file):
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    print(f"   索引文件条目数: {len(index_data)}")
    
    # 检查索引与实际文件是否匹配
    index_filenames = set(entry['filename'] for entry in index_data)
    actual_filenames = set(json_files)
    
    missing_in_index = actual_filenames - index_filenames
    extra_in_index = index_filenames - actual_filenames
    
    if missing_in_index:
        print(f"   ⚠️ 索引中缺失的文件: {len(missing_in_index)}")
        for f in list(missing_in_index)[:5]:
            print(f"      - {f}")
        if len(missing_in_index) > 5:
            print(f"      ... 及其他 {len(missing_in_index) - 5} 个文件")
            
    if extra_in_index:
        print(f"   ⚠️ 索引中有但文件不存在的: {len(extra_in_index)}")
        for f in list(extra_in_index)[:5]:
            print(f"      - {f}")
else:
    print("   ⚠️ 索引文件不存在")

# 3. 验证JSON格式和内容
print(f"\n2. JSON格式验证:")
errors = []
empty_files = []
valid_count = 0

for filename in json_files[:100]:
    filepath = os.path.join(output_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            empty_files.append(filename)
        else:
            valid_count += 1
            
    except json.JSONDecodeError as e:
        errors.append((filename, str(e)))
    except Exception as e:
        errors.append((filename, str(e)))

print(f"   已检查文件: {len(json_files[:100])} 个样本")
print(f"   有效文件: {valid_count}")
print(f"   格式错误: {len(errors)}")

if errors:
    print(f"   ⚠️ 发现格式错误:")
    for filename, error in errors[:5]:
        print(f"      - {filename}: {error}")

if empty_files:
    print(f"   ⚠️ 空文件:")
    for f in empty_files[:5]:
        print(f"      - {f}")

# 4. 检查字段完整性
print(f"\n3. 字段完整性检查:")
sample_file = os.path.join(output_dir, json_files[0]) if json_files else None
if sample_file:
    with open(sample_file, 'r', encoding='utf-8') as f:
        sample_data = json.load(f)
    
    print(f"   样本文件: {json_files[0]}")
    print(f"   字段数量: {len(sample_data)}")
    print(f"   包含字段:")
    for field in sample_data.keys():
        value = sample_data[field]
        preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
        print(f"      - {field}: {preview}")

# 5. 检查重复
print(f"\n4. 重复检查:")
names_seen = {}
duplicates = []

for filename in json_files:
    filepath = os.path.join(output_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        name = data.get('Full Name', '')
        if name:
            if name in names_seen:
                duplicates.append((name, filename, names_seen[name]))
            else:
                names_seen[name] = filename
    except:
        pass

if duplicates:
    print(f"   ⚠️ 发现 {len(duplicates)} 个重复姓名:")
    for name, file1, file2 in duplicates[:5]:
        print(f"      - {name}")
        print(f"        来自: {file1}, {file2}")
else:
    print(f"   ✅ 未发现重复")

# 6. 统计摘要
print(f"\n5. 数据统计:")
countries = {}
genders = {}
subjects = {}

for filename in json_files:
    filepath = os.path.join(output_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        country = data.get('Home Country', 'Unknown')
        gender = data.get('Gender', 'Unknown')
        subject = data.get('Subject Area', '')
        
        countries[country] = countries.get(country, 0) + 1
        genders[gender] = genders.get(gender, 0) + 1
        
        if subject:
            for s in subject.split('|'):
                s = s.strip()
                if s:
                    subjects[s] = subjects.get(s, 0) + 1
    except:
        pass

print(f"   国家分布 (前10):")
for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"      - {country}: {count}")

print(f"   性别分布:")
for gender, count in genders.items():
    print(f"      - {gender}: {count}")

print(f"   研究领域 (前10):")
for subject, count in sorted(subjects.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"      - {subject}: {count}")

print("\n" + "=" * 60)
print("复查完成")
print("=" * 60)
