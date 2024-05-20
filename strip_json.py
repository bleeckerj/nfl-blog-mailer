import json
import os

def strip_values(obj):
    if isinstance(obj, dict):
        return {key: strip_values(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [strip_values(item) for item in obj]
    else:
        return ""

def process_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        stripped_data = strip_values(data)
        
        # Construct the new file name
        base, ext = os.path.splitext(file_path)
        new_file_path = f"{base}_stripped{ext}"
        
        with open(new_file_path, 'w', encoding='utf-8') as file:
            json.dump(stripped_data, file, indent=4, ensure_ascii=False)
            
        print(f"JSON values have been stripped. New file saved as: {new_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
file_path = "./w20-y24.json/w20-y24.json"
process_json_file(file_path)
