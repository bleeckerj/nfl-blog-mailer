from premailer import transform
from bs4 import BeautifulSoup
import urllib.parse
import os

def make_urls_absolute(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')

    # List of tag-attribute pairs: tags and their respective URL attributes
    url_attributes = [('a', 'href'), ('img', 'src'), ('script', 'src'), ('link', 'href')]

    for tag_name, attribute in url_attributes:
        for tag in soup.find_all(tag_name):
            url = tag.get(attribute)
            # Check if the URL is relative and not absolute
            if url and not urllib.parse.urlparse(url).netloc:
                # Make the URL absolute
                absolute_url = urllib.parse.urljoin(base_url, url)
                tag[attribute] = absolute_url

    return str(soup)

# Path to your HTML file

def process_html_with_premailer(html_content, output_file_path):
    try:
        # Read the HTML content from the file
        # with open(input_file_path, 'r') as file:
        #     html_content = file.read()

        # Use Premailer to inline the CSS
        processed_html = transform(html_content)
        fresh_soup = BeautifulSoup(processed_html, 'html.parser')
        
        sm_style_tag = fresh_soup.new_tag('style')
        sm_style_tag.string = "@import url('https://fonts.googleapis.com/css2?family=Space+Mono&display=swap');"
        sm_style_tag.string += """
            @font-face {
            src: url('https://backoffice.nearfuturelaboratory.com/fonts/formadjr/FormaDJRVariable[opsz,slnt,wdth,wght].woff2') format("woff2"),
                url('https://backoffice.nearfuturelaboratory.com/fonts/formadjr/FormaDJRVariable[opsz,slnt,wdth,wght].woff') format("woff");
            font-family: 'FormaDJRVariable';
            font-style: normal;
            font-weight: normal;
}
            @font-face {
            src: url('https://backoffice.nearfuturelaboratory.com/fonts/warbler/WarblerTextV1.2-Regular.woff2') format("woff2"),
                url('https://backoffice.nearfuturelaboratory.com/fonts/warbler/WarblerTextV1.2-Regular.woff') format("woff");
            font-family: 'WarblerText';
            font-style: normal;
            font-weight: 400;
            }

            @font-face {
            src: url('https://backoffice.nearfuturelaboratory.com/fonts/warbler/WarblerTextV1.2-Italic.woff2') format("woff2"),
                url('https://backoffice.nearfuturelaboratory.com/fonts/warbler/WarblerTextV1.2-Italic.woff') format("woff");
            font-family: 'WarblerText';
            font-style: italic;
            font-weight: 400;
            }

            @font-face {
            src: url('https://backoffice.nearfuturelaboratory.com/fonts/warbler/WarblerTextV1.2-Bold.woff2') format("woff2"),
                url('https://backoffice.nearfuturelaboratory.com/fonts/warbler/WarblerTextV1.2-Bold.woff') format("woff");
            font-family: 'WarblerText';
            font-style: normal;
            font-weight: 700;
            }
        """
        fresh_soup.head.append(sm_style_tag)
        foo = str(fresh_soup.prettify())
        # Write the processed HTML back to a new file
        with open(output_file_path, 'w') as file:
            file.write(foo)

        print(f"Processed HTML saved to {output_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# # Example usage
# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python premailer_script.py <input_html_file> <output_html_file>")
#     else:
#         input_path = sys.argv[1]
#         output_path = sys.argv[2]
#         process_html_with_premailer(input_path, output_path)
# Path to your HTML and CSS files
html_file_path = '/Users/julian/Code/nfl-backoffice/dist/blog/2024/02/w7-2024/index.html'
css_file_paths = ['/Users/julian/Code/nfl-backoffice/src/styles/email_responsive.css', '/Users/julian/Code/nfl-backoffice/src/styles/email_styles.css']
base_url = 'https://backoffice.nearfuturelaboratory.com/'
directory_name = os.path.basename(os.path.dirname(html_file_path))

# Create the new filename
new_file_name = directory_name + "_email.html"

# Read the HTML file
with open(html_file_path, 'r') as html_file:
    html_content = html_file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find the <body> tag and clear its contents
head_tag = soup.find('head')
if head_tag:
    head_tag.clear()
    
nav_tag = soup.find('nav')
if nav_tag:
    nav_tag.decompose()

# Convert back to string
modified_html_content = str(soup)
abs_html_content = make_urls_absolute(modified_html_content, base_url)

# Read and combine CSS files
combined_css_content = ''
if css_file_paths.count != 0:
    for css_file_path in css_file_paths:
        with open(css_file_path, 'r') as css_file:
            combined_css_content += css_file.read() + '\n'

# Read the HTML file
# with open(html_file_path, 'r') as html_file:
#     html_content = html_file.read()

# Insert CSS into the HTML
soup = BeautifulSoup(abs_html_content, 'html.parser')
style_tag = soup.new_tag("style", type="text/css")
style_tag.string = combined_css_content
soup.head.append(style_tag)

# Convert back to string
html_with_inline_css = str(soup)

# Now you can process 'html_with_inline_css' with Premailer
process_html_with_premailer(html_with_inline_css, new_file_name)

