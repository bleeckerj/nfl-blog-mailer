import os
import argparse
import json
import tomli  # For reading TOML files
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

def load_config():
    """Load configuration from TOML file if it exists"""
    config_paths = [
        # Check for config in script directory
        Path(__file__).parent / "config.toml",
        # Check in user's home directory
        Path.home() / ".config" / "nfl-blog-mailer" / "config.toml",
    ]
    
    # Default configuration
    config = {
        "templates_directory": os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
        "static_directory": os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/static'),
        "output_directory": None,  # Will default to the directory of the input JSON file
    }
    
    # Try to load from config file
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, "rb") as f:
                    file_config = tomli.load(f)
                    if "settings" in file_config:
                        config.update(file_config["settings"])
                    print(f"Loaded configuration from {config_path}")
                    break
            except Exception as e:
                print(f"Error loading config from {config_path}: {e}")
    
    return config

# Load configuration
config = load_config()

# Setup command line argument parsing
parser = argparse.ArgumentParser(description="Render a Jinja2 template with data from a JSON file.")
parser.add_argument('json_file', type=str, help='Path to the JSON file with the data to render.')
parser.add_argument('--templates', type=str, help='Path to the templates directory', 
                   default=config["templates_directory"])
parser.add_argument('--static', type=str, help='Path to the static templates directory',
                   default=config["static_directory"])
parser.add_argument('--output', type=str, help='Directory to output generated files',
                   default=config["output_directory"])
args = parser.parse_args()

# Modified section for processing JSON list format
with open(args.json_file, 'r') as file:
    data = json.load(file)

# Handle both list and dictionary formats
if isinstance(data, list):
    print(f"JSON file contains a list with {len(data)} items")
    # Keep track of original order
    sections_in_order = []
    # Convert to dictionary while preserving order
    merged_data = {}
    
    for item in data:
        if isinstance(item, dict):
            for section_name, section_content in item.items():
                merged_data[section_name] = section_content
                sections_in_order.append(section_name)
        else:
            print(f"Warning: Skipping non-dictionary item in JSON list: {item}")
    
    data = merged_data
else:
    # If it's already a dictionary, just get the keys in order
    sections_in_order = list(data.keys())

# Set file directory (either from command line or based on input file)
file_directory = args.output if args.output else os.path.dirname(os.path.abspath(args.json_file))
os.makedirs(file_directory, exist_ok=True)  # Ensure output directory exists

# Use the template directory from command line argument or config
templates_directory = args.templates
static_directory = args.static

# Set up Jinja2 environment with the specified template directory
env = Environment(loader=FileSystemLoader(templates_directory))

# Dictionary to keep track of the generated file names by section
generated_files = {}

# Process each section in the JSON data
for section_name, section_content in data.items():
    # Skip if not a dictionary or missing required keys
    if not isinstance(section_content, dict) or 'metadata' not in section_content:
        print(f"Skipping section '{section_name}': invalid format")
        continue
        
    # Get template name from metadata
    try:
        template_name = section_content['metadata']['template_name']
        ordinal = section_content['metadata'].get('ordinal', '')
        
        print(f"Section: {section_name}, Template: {template_name}, Order: {ordinal}")
        
        # Check if template exists
        try:
            template = env.get_template(template_name)
        except Exception as e:
            print(f"Error loading template '{template_name}': {e}")
            continue
        
        # Process each element in the section
        if 'elements' in section_content and isinstance(section_content['elements'], list):
            section_generated_files = []
            for index, element in enumerate(section_content['elements'], start=1):
                # Render the template with the current element's data
                try:
                    rendered_content = template.render(item=element)
                    
                    # Create a new file for the rendered content
                    file_name = f'output_{section_name}_{index}.html'
                    full_path = os.path.join(file_directory, file_name)
    
                    with open(full_path, 'w') as file:
                        file.write(rendered_content)
                    print(f'File {file_name} created successfully.')
    
                    # Add the file name to the list of generated files for the section
                    section_generated_files.append(full_path)
                except Exception as e:
                    print(f"Error rendering template for section '{section_name}', element {index}: {e}")
            generated_files[section_name] = section_generated_files
        else:
            print(f"Skipping section '{section_name}': missing or invalid 'elements' property")
    except Exception as e:
        print(f"Error processing section '{section_name}': {e}")

# Path to static HTML parts
top_file_path = os.path.join(static_directory, 'top.html')
bottom_file_path = os.path.join(static_directory, 'bottom.html')

# Get the base name of the JSON file without its extension
base_name = os.path.splitext(os.path.basename(args.json_file))[0]

# Construct the final HTML file name using the base name
final_file_name = f"{base_name}.html"
final_file_path = os.path.join(file_directory, final_file_name)

# Concatenate all files together into the final HTML file
try:
    with open(final_file_path, 'w') as final_file:
        # Include the top part if it exists
        if os.path.exists(top_file_path):
            with open(top_file_path, 'r') as file:
                final_file.write(file.read())
        else:
            print(f"Warning: Top file '{top_file_path}' not found")
        
        # Include all the generated content following the original order from the JSON
        for section_name in sections_in_order:
            if section_name in generated_files:
                for file_path in generated_files[section_name]:
                    with open(file_path, 'r') as file:
                        final_file.write(file.read())
        
        # Include the bottom part if it exists
        if os.path.exists(bottom_file_path):
            with open(bottom_file_path, 'r') as file:
                final_file.write(file.read())
        else:
            print(f"Warning: Bottom file '{bottom_file_path}' not found")
    
    print(f'All content successfully concatenated into {final_file_path}')
except Exception as e:
    print(f"Error creating final HTML file: {e}")
