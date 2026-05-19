import csv
import json
import os

csv_file = r'C:\Users\001\Desktop\20th-Century-Art-Social-History-Writing-Project\Dictionary_Art_Historians.csv'
output_dir = r'C:\Users\001\Desktop\20th-Century-Art-Social-History-Writing-Project\art_historians_json'

os.makedirs(output_dir, exist_ok=True)

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    count = 0
    for row in reader:
        full_name = row.get('Full Name', '').strip()
        
        if not full_name:
            continue
        
        wp_id = row.get('WordPress Unique ID', '').strip()
        url = row.get('URL', '').strip().strip('/')
        
        if url:
            filename = f"{url}.json"
        elif wp_id:
            name_part = ''.join(c for c in full_name if c.isalnum() or c in (' ', '-', ','))
            name_part = name_part.replace(',', '').replace(' ', '_')
            filename = f"{name_part}_{wp_id}.json"
        else:
            name_part = ''.join(c for c in full_name if c.isalnum() or c in (' ', '-', ','))
            name_part = name_part.replace(',', '').replace(' ', '_')
            filename = f"{name_part}_{count}.json"
        
        filepath = os.path.join(output_dir, filename)
        
        entry = {key: value for key, value in row.items() if value.strip()}
        
        with open(filepath, 'w', encoding='utf-8') as out_f:
            json.dump(entry, out_f, ensure_ascii=False, indent=2)
        
        count += 1
        if count % 200 == 0:
            print(f"已处理 {count} 条记录...")

print(f"\n转换完成！共处理 {count} 条记录")
print(f"JSON 文件已保存到: {output_dir}")
