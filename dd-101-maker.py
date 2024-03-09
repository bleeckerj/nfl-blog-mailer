import os
import argparse
import json
from jinja2 import Environment, FileSystemLoader

# Setup command line argument parsing
parser = argparse.ArgumentParser(description="Render a Jinja2 template with data from a JSON file.")
parser.add_argument('json_file', type=str, help='Path to the JSON file with the data to render.')
args = parser.parse_args()

# Load the JSON data from the file provided as command line argument
with open(args.json_file, 'r') as file:
    data = json.load(file)

file_directory = os.path.dirname(os.path.abspath(args.json_file))
# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('templates'))

# Step 2: Parse 'content_typ_1'
#box_items = data['box-items']


# Step 4 & 5: Render the Template and Create New Files
# for index, item in enumerate(box_items, start=1):
#     print(item)  # To check each item's content before rendering
#     print(item['image_url'])
for section_name, section_content in data.items():
    template_name = section_content['metadata']['template_name']
    print(f"Section: {section_name}, Template: {template_name}")
    template_name = data[section_name]['metadata']['template_name']
    template = env.get_template(template_name)

    for index, element in enumerate(section_content['elements'], start=1):
        #print(element)
        # Render the template with the current item's data
        rendered_content = template.render(item=element)
        
        # Create a new file for the rendered content
        # Naming the files uniquely, for example: content_item_1.html, content_item_2.html, etc.
        file_name = f'output_{section_name}_{index}.html'
        full_path = os.path.join(file_directory, file_name)

        with open(full_path, 'w') as file:
            file.write(rendered_content)
        print(f'File {file_name} created successfully.')

    # Note: Replace 'your_file.json' with the path to your JSON file
    # Replace 'templates' with the path to your template directory
    # Replace 'your_template_name.html' with the name of your actual template file
