from bs4 import BeautifulSoup
import sys
from pathlib import Path

def clean_html(input_file, output_file="cleaned.html"):
    html = Path(input_file).read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # Unwrap tables and their structure
    for tag in soup.find_all(["table", "tr", "td", "div", "span"]):
        tag.unwrap()

    # Remove all inline styles, classes, widths
    for tag in soup.find_all(True):
        for attr in ["style", "class", "width", "cellspacing", "cellpadding", "border"]:
            if attr in tag.attrs:
                del tag[attr]

    # Write to file
    Path(output_file).write_text(str(soup), encoding="utf-8")
    print(f"✅ Cleaned HTML saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_email_html.py path/to/input.html")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = "cleaned.html"  # You can make this configurable
    clean_html(input_path, output_path)
