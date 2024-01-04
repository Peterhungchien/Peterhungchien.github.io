import subprocess
import sys
import argparse
from bs4 import BeautifulSoup, Tag
import yaml
import os
from pathlib import Path

# Define the command line arguments
parser = argparse.ArgumentParser(description='Process .qmd files and generate an HTML file with default YAML headers.')
parser.add_argument('input_file', help='The Quarto (.qmd) file to process.')
parser.add_argument('output_path', help='The output path for the final HTML file.')
args = parser.parse_args()

# Default YAML headers
default_yaml_headers = {
    "math": True,
    "layout": "post"
    # Add any other default headers here
}

# Function to render .qmd to .html explicitly
def render_html(input_file):
    try:
        # Explicitly specify the output format as HTML
        subprocess.run(['quarto', 'render', input_file, '--to', 'html'], check=True)
        return input_file.replace('.qmd', '.html')
    except subprocess.CalledProcessError as e:
        print(f"Error rendering HTML: {e}")
        sys.exit(1)

# Function to extract content from the <main> element
def extract_main_content(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        main_content = soup.find('main')
        header = main_content.find('header')
        if header:
            header.decompose()  # Remove the header element from main_content
        return str(main_content)

# Function to extract and merge YAML headers
def merge_yaml_headers(qmd_file):
    with open(qmd_file, 'r', encoding='utf-8') as file:
        content = file.read()
        yaml_header = content.split('---')[1]  # Assuming there's a YAML header enclosed by '---'
        original_yaml = yaml.safe_load(yaml_header)
        
        # Merge the default YAML headers with the original
        merged_yaml = {**default_yaml_headers, **original_yaml}
        return yaml.dump(merged_yaml, sort_keys=False)

def cleanup_generated_files_and_dirs(input_file):
    # Remove the generated HTML file
    html_file = input_file.replace('.qmd', '.html')
    Path(html_file).unlink()

    # Remove files recursively from the generated_files directory
    # use rm -r command
    generated_dir = input_file.replace('.qmd', '_files')
    subprocess.run(['rm', '-r', generated_dir], check=True)
    

# Main process
if __name__ == '__main__':
    # Step 1: Render the .qmd to .html
    html_file = render_html(args.input_file)
    print(args.input_file)

    # Step 2: Extract content from the <main> element
    main_content = extract_main_content(html_file)

    # Step 3: Merge the YAML headers
    merged_yaml_header = merge_yaml_headers(args.input_file)

    # Step 4: Concatenate and create the new .html file at the specified output path
    output_file = args.output_path
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(f"---\n{merged_yaml_header}---\n{main_content}")

    print(f"New HTML file created at: {output_file}")
    cleanup_generated_files_and_dirs(args.input_file)
