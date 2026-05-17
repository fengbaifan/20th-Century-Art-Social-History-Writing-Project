import os
import json

output_dir = r'C:\Users\001\Desktop\20th-Century-Art-Social-History-Writing-Project\art_historians_json'

index_data = []

for filename in sorted(os.listdir(output_dir)):
    if filename.endswith('.json') and filename != 'index.json':
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        entry = {
            'filename': filename,
            'full_name': data.get('Full Name', ''),
            'title': data.get('Title', ''),
            'url': data.get('URL', ''),
            'birth_year': data.get('Birth Year', ''),
            'death_year': data.get('Death Year', ''),
            'home_country': data.get('Home Country', ''),
            'gender': data.get('Gender', ''),
            'subject_area': data.get('Subject Area', ''),
            'overview': data.get('Overview', '')[:200] + '...' if len(data.get('Overview', '')) > 200 else data.get('Overview', '')
        }
        
        index_data.append(entry)

index_file = os.path.join(output_dir, 'index.json')
with open(index_file, 'w', encoding='utf-8') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print(f"索引文件已创建，包含 {len(index_data)} 条记录")
print(f"索引文件路径: {index_file}")
