import json
from pathlib import Path
from typing import List, Dict, TypedDict, Union
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

# --- DOCUMENT METADATA EXTRACTION ---
def extract_document_metadata(soup: BeautifulSoup) -> Dict[str, Union[str, None]]:
    """Extracts source_category, source_id, and source_title from <meta> and <title>."""
    source_category = None
    source_id = None
    source_title = None

    meta_kw = soup.find("meta", attrs={"name": "keywords"})
    if meta_kw and meta_kw.has_attr("content"):
        source_category = str(meta_kw["content"]).strip()

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


def extract_anchor_from_header(header_element: Tag) -> str:
    inline_anchor = header_element.find('a', id=True)
    if not inline_anchor: raise ValueError("Section has no anchor")
    id = inline_anchor['id']
    return id[0] if isinstance(id, list) else id

# --- CORE PARSING LOGIC ---
def parse_html_to_sections(
    path: Path, 
    save_path: Path
) -> tuple[list[Section], dict[str, str | None]]:
    """
    Parses a single HTML file, splits content into semantic sections based on H2 and H3 tags,
    and extracts document-level metadata from <meta> and <title> tags.
    """
    print(f"Loading {path} for semantic parsing...")
    save_path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

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
    current_section_text: str = ""
    current_heading_text: str = ""
    current_heading_id: str = ""
    last_anchor_id: str = ""

    def _flush_section():
        nonlocal current_heading_text, current_heading_id, last_anchor_id, current_section_text
        if current_section_text and current_heading_text:
            text_content = current_section_text
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

        current_section_text = ""

    def _process_inline_recursively(element, indent_level=0) -> str:
        text = process_element(element)
        if text is not None:
            return text
        
        # Handle definition lists specially
        if element.name == 'dl':
            dl_text = ""
            for child in element.children:
                if isinstance(child, Tag):
                    if child.name == 'dt':
                        term = _process_inline_recursively(child, indent_level).strip()
                        dl_text += f'\n{"  " * indent_level}  * '
                        if term:
                            dl_text += f'**{term}**: '
                    elif child.name == 'dd':
                        desc = _process_inline_recursively(child, indent_level).strip()
                        dl_text += desc
            return dl_text
        
        # For other elements, recurse through children
        parts = []
        for child in element.children:
            if isinstance(child, NavigableString):
                parts.append(str(child))
            elif child.name in ['ol', 'ul', 'dl']:
                continue
            else:
                parts.append(_process_inline_recursively(child, indent_level))
        
        text = ''.join(parts)
        text = text.replace('\n', ' ')
        text = re.sub(r' {2,}', ' ', text)
        text = text.strip()

        # Now process any nested lists or definition lists
        for child in element.children:
            if isinstance(child, Tag):
                if child.name in ['ul', 'ol']:
                    # Process nested list items with indentation
                    for nested_li in child.find_all('li', recursive=False):
                        nested_content = _process_inline_recursively(nested_li, indent_level + 1)
                        if nested_content:
                            text += f'\n{"  " * (indent_level + 1)}* {nested_content}'
                elif child.name == 'dl':
                    # Process nested definition list
                    dl_content = _process_inline_recursively(child, indent_level + 1)
                    if dl_content:
                        text += dl_content

        return text

    def process_element(element) -> str | None:
        if isinstance(element, NavigableString):
            text = str(element)
            text = text.replace('\n', ' ')
            text = re.sub(r' {2,}', ' ', text)
            text = text.strip()
            return text
        
        # Handle the element itself if it's a styled element
        elif element.name in ['em', 'b', 'code']:
            text = element.get_text().strip()
            if element.name == 'em':
                return f'*{text}*'
            elif element.name == 'b':
                return f'**{text}**'
            elif element.name == 'code':
                return f'`{text}`'
            
        elif element.name == 'a':
            link_text = element.get_text().strip()
            if element.has_attr('href') and not element['href'].startswith('#'):
                return f'[{link_text}]({element["href"]})'
            else:
                return link_text

    def get_tag_text(element):
        nonlocal current_heading_text, current_heading_id, last_anchor_id, current_section_text

        text = process_element(element)
        if text is not None:
            if current_section_text.endswith('\n'):
                current_section_text += '\n'
            elif text:
                current_section_text += ' '
            current_section_text += text
            return
        
        elif element.name == 'h5':
            heading_text = element.get_text(strip=False).strip()
            current_section_text += f'\n\n**{heading_text}**\n'
            return

        elif element.name == 'pre':
            current_section_text += f'\n```\n{element.get_text(strip=True)}\n```\n'
            return
        
        elif element.name == 'dl':
            # Definition list - render as structured list
            text = ""
            for child in element.children:
                if isinstance(child, Tag):
                    if child.name == 'dt':
                        # Definition term - bold text
                        term = _process_inline_recursively(child).strip()
                        if term:
                            text += f'\n\n**{term}**: '
                    elif child.name == 'dd':
                        desc = _process_inline_recursively(child)
                        text += desc
                    else:
                        raise ValueError("Non-dd/dt element inside dl element")
            current_section_text += text + '\n'
            return
        
        elif element.name == 'li':
            current_section_text += f'\n* {_process_inline_recursively(element)}'
            return

        elif element.name == 'table':
            current_section_text += '\n\n'
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
                current_section_text += '\n```\n'
                current_section_text += pre_tags[0].get_text(strip=True)
                current_section_text += '\n```\n'
                if caption_text:
                    current_section_text += caption_text
                return

            # --- CASE 2: Single-cell layout ---
            if is_single_cell_layout:
                if caption_text:
                    current_section_text += caption_text
                return

            # --- CASE 3: Normal multi-cell table ---
            current_section_text += '\n\n'

            # Collect all rows and their cell contents
            rows = []
            for tr in element.find_all('tr'):
                row_data = []
                for td in tr.find_all('td'):
                    # Collapse all whitespace in cells to single spaces
                    cell_text = td.get_text(separator=" ")
                    cell_text = re.sub(r'\s+', ' ', cell_text).strip()
                    row_data.append(cell_text)
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
            current_section_text += '\n' + "| " + " | ".join(headers) + " |"
            current_section_text += '\n' + "|" + "|".join(["-" * max(len(h), 3) for h in headers]) + "|"

            # Render table rows
            for row in rows:
                # Pad rows to match max_cols
                row += [""] * (max_cols - len(row))
                current_section_text += '\n' + "| " + " | ".join(row) + " |"

            if caption_text:
                current_section_text += '\n' + caption_text
            current_section_text += '\n'
            return

        elif element.name in ['h2', 'h3']:
            _flush_section()
            found_anchor = extract_anchor_from_header(element)
            if found_anchor:
                last_anchor_id = found_anchor
            heading_text = element.get_text(strip=False).strip()
            if heading_text and heading_text[0].isdigit():
                heading_parts = heading_text.split(maxsplit=1)
                current_heading_id = heading_parts[0]
                current_heading_text = heading_parts[1] if len(heading_parts) > 1 else heading_parts[0]
            else:
                heading_id_parts = current_heading_id.split('.')
                heading_id_parts[-1] = 'QA'
                current_heading_id = '.'.join(heading_id_parts)
                current_heading_text = heading_text
            current_section_text += f'\n## {current_heading_id} {current_heading_text}\n'
            return

        if element.name in ['p', 'ul', 'ol']:
            current_section_text += '\n'

        for child in element.children:
            get_tag_text(child)

        if element.name in ['p', 'ul', 'ol']:
            current_section_text += '\n'

    if soup.body:
        for child in soup.body.children:
            get_tag_text(child)

    _flush_section()
    
    sections = [
        s for s in sections
        if s['metadata']['title'].strip().lower() not in [
            "forelesningsvideoer", "video av forelesningen", "slides og opptak", "slides brukt i forelesningen", "sist"
        ]
    ]

    full_text = "\n\n---\n\n".join(s['text'] for s in sections)
    save_path = save_path.with_suffix(".md")
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"  -> Saved concatenated postprocessed text to {save_path}")

    return sections, doc_meta

# --- MAIN INGESTION FUNCTION ---

def load_and_split_documents(data_dir: Path, postprocessed_dir: Path) -> List[Dict]:
    all_chunks = []

    for path in data_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() == '.html':
            relative_path = path.relative_to(data_dir)
            save_path = postprocessed_dir / relative_path

            sections, doc_meta = parse_html_to_sections(path, save_path)
            if not sections:
                continue

            for i, section in enumerate(sections):
                text = section['text']
                section_id = section['metadata']['section_id'] or f"{doc_meta['source_id']}.{i + 1}"
                identifier = f"{doc_meta['source_category']}{section_id}"

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
    all_chunks = load_and_split_documents(DATA_DIR, POSTPROCESSED_DIR)

    if not all_chunks:
        print("Error: No chunks were generated. Check DATA_DIR and file types.")
    else:
        print(f"Successfully generated {len(all_chunks)} semantic chunks.")
        with open(CHUNK_OUTPUT_FILE, "w", encoding="utf-8") as f:
            for chunk in all_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
        print(f"--- CHUNKS SAVED TO {CHUNK_OUTPUT_FILE} ---")