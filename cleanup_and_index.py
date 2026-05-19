import os
import json

output_dir = r'C:\Users\001\Desktop\20th-Century-Art-Social-History-Writing-Project\art_historians_json'

# 删除旧的单字母文件
files_to_remove = []
for filename in os.listdir(output_dir):
    if filename.endswith('.json') and len(filename.split('.')[0]) == 1:
        files_to_remove.append(filename)

for filename in files_to_remove:
    filepath = os.path.join(output_dir, filename)
    try:
        os.remove(filepath)
        print(f"已删除: {filename}")
    except Exception as e:
        print(f"删除失败 {filename}: {e}")

# 重新创建索引
index_data = []

for filename in sorted(os.listdir(output_dir)):
    if filename.endswith('.json') and filename != 'index.json':
        filepath = os.path.join(output_dir, filename)
        
        try:
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
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {e}")

index_file = os.path.join(output_dir, 'index.json')
with open(index_file, 'w', encoding='utf-8') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print(f"\n清理完成！删除了 {len(files_to_remove)} 个旧文件")
print(f"索引文件已创建，包含 {len(index_data)} 条记录")
print(f"索引文件路径: {index_file}")
