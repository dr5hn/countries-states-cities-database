import os

def split_sql_file_by_crlf(input_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = [block.strip() for block in content.split('\n\n') if block.strip()]

    for i, block in enumerate(blocks, start=1):
        file_name = f"part_{i:03}.sql"
        file_path = os.path.join(output_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as out_file:
            out_file.write(block)  
        print(f"Saved: {file_name}")

    print(f"\n split {len(blocks)} files into：'{output_dir}'")


if __name__ == "__main__":
    input_path = 'cities.sql'              
    output_folder = 'cities_parts'    
    split_sql_file_by_crlf(input_path, output_folder)