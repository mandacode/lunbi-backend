# SB - Space Biology
import re
from pathlib import Path
import csv

import bs4
import requests

from .config import DATA_PATH, PROJECT_ROOT

BASE_DIR = Path(__file__).resolve().parent
SRC_FILE = "SB_publication_PMC.csv"
CSV_PATH = PROJECT_ROOT / "data" / SRC_FILE

NEW_BASE_URL = "https://pmc.ncbi.nlm.nih.gov/articles/{article_id}/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://google.com"
}


def to_snake_case(text):
    text = text.strip().lower()  # małe litery
    text = re.sub(r'[^a-z0-9]+', '_', text)  # zamiana wszystkiego poza literami/cyframi na _
    text = re.sub(r'_+', '_', text)  # usunięcie powtarzających się podkreślników
    return text.strip('_')


def section_to_markdown(section: dict, level: int = 1) -> str:
    """
    Recursively converts a section dict to Markdown.

    Parameters:
    - section: dict with 'id', 'headers', 'paragraphs', 'subsections'
    - level: integer representing the Markdown heading level (#, ##, ### ...)

    Returns:
    - string with Markdown content
    """
    md = ""

    # Add section headers
    for header in section.get("headers", []):
        md += f"{'#' * level + "#"} {header}\n\n"

    # Add paragraphs
    for para in section.get("paragraphs", []):
        md += f"{para}\n\n"

    # Recurse into subsections
    for subsec in section.get("subsections", []):
        md += section_to_markdown(subsec, level=level + 1)

    return md


def parse_section(section: bs4.element.Tag) -> dict:
    """
    Recursively parses a <section> tag and extracts headers, paragraphs, and nested sections.
    Returns a dictionary with:
      - 'id': section id
      - 'headers': list of headers in the section
      - 'paragraphs': list of paragraphs in the section
      - 'subsections': list of parsed nested sections
    """
    data = {
        "id": section.get("id"),
        "headers": [],
        "paragraphs": [],
        "subsections": []
    }

    for child in section.children:
        if child.name:
            # Collect headers
            if child.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                data["headers"].append(child.get_text(strip=True))

            # Collect paragraphs
            elif child.name == "p":
                data["paragraphs"].append(child.get_text(strip=True))

            # Recursive call for nested sections
            elif child.name == "section":
                data["subsections"].append(parse_section(child))

    return data



def main() -> None:
    with CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # skip header
        for title, url in reader:
            article_id = url.strip("/").split("/")[-1]
            url = NEW_BASE_URL.format(article_id=article_id)
            response = requests.get(url, headers=headers)

            # Parse HTML
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            article = soup.find("article")
            metadata, content = article.find_all("section", recursive=False)
            body = content.find("section", recursive=False, class_='body')
            sections = body.find_all("section", recursive=False)

            # To python dict
            parsed_sections = [parse_section(section) for section in sections]

            # To markdown
            text = "# " + title.title() + "\n\n"
            for section in parsed_sections:
                text += "\n"
                text += section_to_markdown(section)

            filename = to_snake_case(title) + '.md'
            path = DATA_PATH / filename
            with open(path, "w", encoding="utf-8") as md_file:
                md_file.write(text)

            print(f"Downloaded article {title.title()}")


if __name__ == "__main__":
    main()
