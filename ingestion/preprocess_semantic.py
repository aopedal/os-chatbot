import json
from pathlib import Path
from typing import List, Dict, TypedDict, Union
from urllib.parse import quote
from bs4 import BeautifulSoup, Tag, Comment
from bs4.element import NavigableString
import re

# --- TYPE DEFINITION ---

class SectionMetadata(TypedDict):
    """Defines the expected structure of the metadata dictionary for a section."""
    title: str
    section_id: str
    anchor_id: str

class Section(TypedDict):
    """Defines the expected structure of a single semantic section."""
    text: str
    metadata: SectionMetadata

# --- CONFIGURATION ---
DATA_DIR = Path("./knowledge")
POSTPROCESSED_DIR = Path("./knowledge_processed")
CHUNK_OUTPUT_FILE = "processed_chunks.jsonl"

# --- CORE PARSING LOGIC ---

def parse_html_to_sections(path: Path, save_path: Path) -> (List[Section], Dict[str, Union[str, None]]):
    """
    Parses a single HTML file, splits content into semantic sections based on H2 and H3 tags,
    and extracts document-level metadata from <meta> and <title> tags.
    """
    print(f"Loading {path} for semantic parsing...")
    save_path.parent.mkdir(parents=True, exist_ok=True)

    if path.suffix.lower() != ".html":
        if path.suffix.lower() == ".txt":
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return ([{
                        "text": content,
                        "metadata": {"title": "Full Document Content", "section_id": "0", "anchor_id": ""}
                    }], {"source_category": None, "source_id": None, "source_title": None})
        return ([], {"source_category": None, "source_id": None, "source_title": None})

    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # --- DOCUMENT METADATA EXTRACTION ---
    def extract_document_metadata(soup: BeautifulSoup) -> Dict[str, Union[str, None]]:
        """Extracts source_category, source_id, and source_title from <meta> and <title>."""
        source_category = None
        source_id = None
        source_title = None

        meta_kw = soup.find("meta", attrs={"name": "keywords"})
        if meta_kw and meta_kw.has_attr("content"):
            source_category = meta_kw["content"].strip()

        title_tag = soup.find("title")
        if title_tag and title_tag.text.strip():
            title_text = title_tag.text.strip()
            match = re.match(r"(\d+)\s+Forelesning.*?\.\s*(.+)", title_text)
            if match:
                source_id = match.group(1)
                source_title = match.group(2).strip()
            else:
                source_title = title_text

        return {
            "source_category": source_category,
            "source_id": source_id,
            "source_title": source_title,
        }

    doc_meta = extract_document_metadata(soup)

    # --- 1. PRE-CLEANUP ---
    for selector in ['a#CHILD_LINKS', 'ul.ChildLinks', 'hr', 'address']:
        tag = soup.select_one(selector)
        if tag:
            tag.decompose()

    for img in soup.find_all('img'):
        img.decompose()

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    sections: List[Section] = []
    current_section_lines: List[str] = []
    current_heading_text: str = ""
    current_heading_id: str = ""
    last_anchor_id: str = ""

    RECURSION_SKIP = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'table', 'pre', 'a', 'em', 'b']
    BREAK_AFTER = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']
    BREAK_BEFORE = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre', 'table']

    def _flush_section():
        nonlocal current_heading_text, current_heading_id, current_section_lines, last_anchor_id
        if current_section_lines and current_heading_text:
            text_content = "\n".join(current_section_lines)
            text_content = re.sub(r'\n{3,}', '\n\n', text_content).strip()

            if text_content:
                sections.append(Section(
                    text=text_content,
                    metadata=SectionMetadata(
                        title=current_heading_text,
                        section_id=current_heading_id,
                        anchor_id=last_anchor_id
                    )
                ))

        current_section_lines = []
        current_heading_text = ""
        current_heading_id = ""

    def _extract_anchor_from_header(header_element: Tag) -> str:
        inline_anchor = header_element.find('a', id=True)
        if inline_anchor:
            return inline_anchor['id']
        if header_element.has_attr('id') and header_element['id']:
            return header_element['id']
        anchor_tags = header_element.find_previous_siblings(['a'], limit=2)
        if anchor_tags:
            for anchor_tag in anchor_tags:
                if anchor_tag and (anchor_tag.has_attr('id') or anchor_tag.has_attr('name')):
                    return anchor_tag.get('id') or anchor_tag.get('name') or ''
        return ""

    def get_tag_text(element):
        nonlocal current_heading_text, current_heading_id, last_anchor_id

        if isinstance(element, NavigableString):
            stripped_text = str(element).strip()
            if stripped_text:
                if current_section_lines and current_section_lines[-1] and not current_section_lines[-1].endswith('\n'):
                    if not current_section_lines[-1].endswith(' '):
                        current_section_lines[-1] += ' '
                    current_section_lines[-1] += stripped_text
                else:
                    current_section_lines.append(stripped_text)
            return

        if element.name in ['h2', 'h3']:
            _flush_section()
            found_anchor = _extract_anchor_from_header(element)
            if found_anchor:
                last_anchor_id = found_anchor
            heading_text = element.get_text(strip=False).strip()
            if heading_text and heading_text[0].isdigit():
                heading_parts = heading_text.split(maxsplit=1)
                current_heading_id = heading_parts[0]
                current_heading_text = heading_parts[1]
            else:
                current_heading_id = ""
                current_heading_text = heading_text
            current_section_lines.append('## ' + current_heading_text)
            current_section_lines.append('\n\n')
            return

        elif element.name in ['em', 'b']:
            styled_text = element.get_text(strip=False).strip()
            if element.name == 'em':
                styled_text = f'*{styled_text}*'
            elif element.name == 'b':
                styled_text = f'**{styled_text}**'
            if current_section_lines and current_section_lines[-1] and not current_section_lines[-1].endswith('\n'):
                if not current_section_lines[-1].endswith(' '):
                    current_section_lines[-1] += ' '
                current_section_lines[-1] += styled_text
            else:
                current_section_lines.append(styled_text)
            return

        if element.name in BREAK_BEFORE:
            current_section_lines.append('\n\n')

        if element.name == 'h1':
            text = element.text.strip()
            current_section_lines.append(text)
            found_anchor = _extract_anchor_from_header(element)
            if found_anchor:
                last_anchor_id = found_anchor

        elif element.name == 'li':
            current_section_lines.append(f'* {element.get_text(strip=True)}')

        elif element.name == 'a':
            link_text = element.text.strip()
            if link_text:
                current_section_lines.append(link_text)

        elif element.name == 'pre':
            current_section_lines.append('```')
            current_section_lines.append(element.get_text(strip=False).strip())
            current_section_lines.append('```')

        elif element.name == 'table':
            pre_tags = element.find_all('pre')
            td_tags = element.find_all('td')
            th_tags = element.find_all('th')
            is_code_table = (len(pre_tags) == 1 and len(td_tags) <= 1 and len(th_tags) == 0)
            is_single_cell_layout = (len(pre_tags) == 0 and len(td_tags) + len(th_tags) == 1)

            caption = element.find('caption', class_='BOTTOM')
            caption_text = None
            if caption:
                caption_text = caption.text.replace('Figure:', 'Illustrasjon:').strip()
                caption.decompose()

            # --- CASE 1: Code table ---
            if is_code_table:
                current_section_lines.append('```')
                current_section_lines.append(pre_tags[0].get_text(strip=False).strip())
                current_section_lines.append('```\n')
                if caption_text:
                    current_section_lines.append(caption_text)
                return

            # --- CASE 2: Single-cell layout ---
            if is_single_cell_layout:
                text_content = element.get_text(separator=" ", strip=True)
                if text_content:
                    current_section_lines.append(text_content)
                if caption_text:
                    current_section_lines.append(caption_text)
                return

            # --- CASE 3: Normal multi-cell table ---
            current_section_lines.append('\n\n')

            # Collect all rows and their cell contents
            rows = []
            for tr in element.find_all('tr'):
                row_data = [td.get_text(strip=True) for td in tr.find_all('td')]
                if row_data:
                    rows.append(row_data)

            if not rows:
                return

            # Compute max column count
            max_cols = max(len(r) for r in rows)

            # Extract headers (first row with <th>, or generate placeholders)
            headers = [th.text.strip() for th in element.find_all('th')]

            for i in range(len(headers), max_cols):
                headers.append(" ")

            # Render table header and separator line
            current_section_lines.append("| " + " | ".join(headers) + " |")
            current_section_lines.append("|" + "|".join(["-" * max(len(h), 3) for h in headers]) + "|")

            # Render table rows
            for row in rows:
                # Pad rows to match max_cols
                row += [""] * (max_cols - len(row))
                current_section_lines.append("| " + " | ".join(row) + " |")

            if caption_text:
                current_section_lines.append(caption_text)
            current_section_lines.append('\n')

        if element.name not in RECURSION_SKIP:
            for child in element.children:
                if isinstance(child, (Tag, NavigableString)):
                    get_tag_text(child)

        if element.name in BREAK_AFTER and current_section_lines:
            current_section_lines[-1] += '\n'

        if element.name in ['ul', 'ol']:
            current_section_lines[-1] += '\n\n'

    if soup.body:
        for child in soup.body.children:
            if isinstance(child, (Tag, NavigableString)):
                get_tag_text(child)

    _flush_section()
    
    sections = [s for s in sections if s['metadata']['title'].strip().lower() != "forelesningsvideoer"]

    full_text = "\n\n---\n\n".join(s['text'] for s in sections)
    save_path = save_path.with_suffix(".md")
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"  -> Saved concatenated postprocessed text to {save_path}")

    return sections, doc_meta

# --- MAIN INGESTION FUNCTION (REVISED) ---

def load_and_split_documents(data_dir: Path, postprocessed_dir: Path) -> List[Dict]:
    all_chunks = []

    for path in data_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in [".html", ".txt"]:
            relative_path = path.relative_to(data_dir)
            save_path = postprocessed_dir / relative_path

            sections, doc_meta = parse_html_to_sections(path, save_path)
            if not sections:
                continue

            for i, section in enumerate(sections):
                text = section['text']
                section_id = section['metadata']['section_id'] or f"{doc_meta["source_id"]}.{i + 1}"
                identifier = f"{doc_meta["source_category"]}{section_id}"

                all_chunks.append({
                    "identifier": identifier,
                    "section_id": section_id,
                    "section_title": section['metadata']['title'],
                    "source_category": doc_meta["source_category"],
                    "source_id": doc_meta["source_id"],
                    "source_title": doc_meta["source_title"],
                    "anchor": section['metadata']['anchor_id'],
                    "source": str(relative_path),
                    "text": text,
                })

    return all_chunks

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    POSTPROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    print("--- 1. STARTING DOCUMENT PREPROCESSING (Targeting Inline Anchors) ---")

    all_chunks = load_and_split_documents(DATA_DIR, POSTPROCESSED_DIR)

    if not all_chunks:
        print("Error: No chunks were generated. Check DATA_DIR and file types.")
    else:
        print(f"\nSuccessfully generated {len(all_chunks)} semantic chunks.")
        with open(CHUNK_OUTPUT_FILE, "w", encoding="utf-8") as f:
            for chunk in all_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
        print(f"--- CHUNKS SAVED TO {CHUNK_OUTPUT_FILE} ---")
