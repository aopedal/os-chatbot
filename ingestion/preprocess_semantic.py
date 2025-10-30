import json
from pathlib import Path
from typing import List, Dict, TypedDict, Union
from urllib.parse import quote
from bs4 import BeautifulSoup, Tag, Comment
from bs4.element import NavigableString

# --- TYPE DEFINITION ---

class SectionMetadata(TypedDict):
    """Defines the expected structure of the metadata dictionary for a section."""
    title: str
    section_id: str
    anchor_id: str

class Section(TypedDict):
    """Defines the expected structure of a single semantic section."""
    text: str # Renamed from chunk_text
    metadata: SectionMetadata

# --- CONFIGURATION ---
DATA_DIR = Path("./knowledge")
POSTPROCESSED_DIR = Path("./knowledge_processed")
CHUNK_OUTPUT_FILE = "processed_chunks.jsonl" # File to store all chunks

# --- CORE PARSING LOGIC ---

def parse_html_to_sections(path: Path, save_path: Path) -> List[Section]:
    """
    Parses a single HTML file, splits content into semantic sections based on H2 and H3 tags.
    Targets the specific inline anchor structure: <H2><A ID="...">...</A></H2>.
    
    Returns a list of Section dictionaries.
    """
    
    print(f"Loading {path} for semantic parsing...")
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    if path.suffix.lower() != ".html":
        if path.suffix.lower() == ".txt":
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return [{
                        "text": content,
                        "metadata": {"title": "Full Document Content", "section_id": "0", "anchor_id": ""}
                    }]
        return [] 

    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    # --- 1. PRE-CLEANUP ---
    for selector in ['a#CHILD_LINKS', 'ul.ChildLinks', 'hr', 'address']:
        tag = soup.select_one(selector)
        if tag: tag.decompose()

    for img in soup.find_all('img'):
        img.decompose()
        
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
        
    # Variables for semantic splitting
    sections: List[Section] = []
    current_section_lines: List[str] = []
    current_heading_text: str = ""
    current_heading_id: str = ""
    last_anchor_id: str = "" 

    # Traversal/Splitting Configuration
    RECURSION_SKIP = ['h1', 'h2', 'h3', 'li', 'table', 'pre', 'a']
    BREAK_AFTER = ['h1', 'h2', 'h3', 'p', 'li'] 
    BREAK_BEFORE = ['h1', 'h2', 'h3', 'p', 'ul', 'ol', 'pre', 'table']

    def _flush_section():
        """Saves the current section buffer and resets."""
        nonlocal current_heading_text, current_heading_id, current_section_lines, last_anchor_id
        if current_section_lines and current_heading_text:
            text_content = "\n".join([line.strip() for line in current_section_lines if line.strip() or line.startswith(('*', '-'))])
            text_content = text_content.replace('\n\n\n', '\n\n').strip()
            
            if text_content:
                sections.append(Section( 
                    text=text_content,
                    metadata=SectionMetadata(
                        title=current_heading_text,
                        section_id=current_heading_id,
                        anchor_id=last_anchor_id
                    )
                ))

        # Reset for the next section
        current_section_lines = []
        current_heading_text = ""
        current_heading_id = ""

    def _extract_anchor_from_header(header_element: Tag) -> str:
        """
        Looks specifically for an <a> tag with an ID inside the header element,
        or the ID on the header itself, as a fallback.
        """
        # 1. Target the inline anchor structure: <H2><A ID="..."></A></H2>
        inline_anchor = header_element.find('a', id=True)
        if inline_anchor:
            return inline_anchor['id']
            
        # 2. Fallback: Check the header itself for a direct ID
        if header_element.has_attr('id') and header_element['id']:
            return header_element['id']
            
        # 3. Last Fallback: Check the immediate previous sibling for a classic anchor
        anchor_tags = header_element.find_previous_siblings(['a'], limit=2) 
        if anchor_tags:
            for anchor_tag in anchor_tags:
                 if anchor_tag and (anchor_tag.has_attr('id') or anchor_tag.has_attr('name')):
                    return anchor_tag.get('id') or anchor_tag.get('name')
            
        return ""


    def get_tag_text(element):
        """Recursively extracts text into the current_section_lines buffer."""
        nonlocal current_heading_text, current_heading_id, last_anchor_id
        
        # 1. Handle NavigableString (Text Node)
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
        
        # --- Heading Detection (The core of semantic splitting) ---
        if element.name in ['h2', 'h3']:
            _flush_section() 
            
            # --- FIXED ANCHOR LOGIC ---
            # Use the new targeted extraction function
            found_anchor = _extract_anchor_from_header(element)
            if found_anchor:
                 last_anchor_id = found_anchor
            # If no anchor is found, last_anchor_id retains its previous value or remains ""
            
            # Start the new section metadata
            # We use get_text() on the header element to capture the full title text
            current_heading_text = element.get_text(strip=True)
            current_heading_id = current_heading_text.split()[0].strip().replace('.', '') if current_heading_text.split() and current_heading_text.split()[0].replace('.', '').isdigit() else element.name
            
            current_section_lines.append(current_heading_text)
            current_section_lines.append('\n\n') 
            
            # IMPORTANT: We stop recursion here for H2/H3 tags to prevent 
            # reprocessing the title text which we just captured with get_text()
            return

        # 2. Handle Tag (Element)
        
        # --- Inline <em> HANDLING ---
        elif element.name == 'em':
            italic_text = f"*{element.get_text(strip=False).strip()}*"
            
            if current_section_lines and current_section_lines[-1] and not current_section_lines[-1].endswith('\n'):
                 if not current_section_lines[-1].endswith(' '):
                    current_section_lines[-1] += ' '
                 current_section_lines[-1] += italic_text
            else:
                 current_section_lines.append(italic_text)
            
            return 

        # --- BLOCK ELEMENT START ---
        if element.name in BREAK_BEFORE:
            current_section_lines.append('\n\n')

        # Handle H1
        if element.name == 'h1':
            text = element.text.strip()
            if "Forelesning slides ." in text:
                 text = text.split("Forelesning slides .")[0].strip()
            current_section_lines.append(text)
            
            # Also check for inline anchors or direct IDs in H1
            found_anchor = _extract_anchor_from_header(element)
            if found_anchor:
                 last_anchor_id = found_anchor

        # Handle Lists
        elif element.name == 'li':
            current_section_lines.append(f'* {element.text.strip()}')

        # Handle Links (Only extract text if it's not the inline anchor we target above)
        elif element.name == 'a':
            link_text = element.text.strip()
            if link_text:
                current_section_lines.append(link_text)
            
        # Handle Code Blocks (PRE)
        elif element.name == 'pre':
            current_section_lines.append('---CODE START---')
            current_section_lines.append(element.get_text(strip=False).strip())
            current_section_lines.append('---CODE END---')

        # Handle Tables
        elif element.name == 'table':
            pre_tags = element.find_all('pre')
            td_tags = element.find_all('td')
            th_tags = element.find_all('th')
            is_code_table = (len(pre_tags) == 1 and len(td_tags) <= 1 and len(th_tags) == 0)

            caption = element.find('caption', class_='BOTTOM')
            caption_text = None
            if caption:
                caption_text = caption.text.strip().replace("Figure: Figure:", "Figure:").replace("Figure: Figure", "Figure:")
                caption.decompose() 

            if is_code_table:
                current_section_lines.append('---CODE START---')
                current_section_lines.append(pre_tags[0].get_text(strip=False).strip())
                current_section_lines.append('---CODE END---')
                if caption_text: current_section_lines.append(caption_text)
            else:
                current_section_lines.append('\n---TABLE START---')
                headers = [th.text.strip() for th in element.find_all('th')]
                if headers: current_section_lines.append(" | ".join(headers) + " |")
                
                for tr in element.find_all('tr'):
                    row_data = [td.text.strip() for td in tr.find_all('td')]
                    current_section_lines.append(" | ".join([d for d in row_data if d]) + " |")
                
                if caption_text: current_section_lines.append(caption_text)
                current_section_lines.append('---TABLE END---')

        # 3. RECURSION
        if element.name not in RECURSION_SKIP and element.name not in ['h2', 'h3', 'em']:
            for child in element.children: 
                if isinstance(child, (Tag, NavigableString)):
                    get_tag_text(child)

        # 4. BREAK AFTER
        if element.name in BREAK_AFTER and current_section_lines and current_section_lines[-1].strip() not in ('\n', ''):
            current_section_lines.append('\n')

    # Start traversal from the body tag
    if soup.body:
        for child in soup.body.children:
             if isinstance(child, (Tag, NavigableString)):
                 get_tag_text(child)
    
    _flush_section() 
    
    # Save the full concatenated text for inspection
    full_text = "\n\n---\n\n".join(s['text'] for s in sections)
    save_path = save_path.with_suffix(".txt")
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"  -> Saved concatenated postprocessed text to {save_path}")
    
    return sections


# --- MAIN INGESTION FUNCTION (REVISED) ---

def load_and_split_documents(data_dir: Path, postprocessed_dir: Path) -> List[Dict]:
    """
    Walks through data_dir recursively, extracts content, and uses semantic chunking
    to generate chunks (sections), using the HTML header ID as the link anchor.
    """
    all_chunks = []

    for path in data_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in [".html", ".txt"]:
            relative_path = path.relative_to(data_dir)
            save_path = postprocessed_dir / relative_path

            sections = parse_html_to_sections(path, save_path)
            
            if not sections:
                continue

            for i, section in enumerate(sections):
                text = section['text']
                identifier = f"{relative_path.stem}_{i}_{len(text)}"
                
                anchor_id = section['metadata']['anchor_id']
                # Only create the anchor link if an ID was successfully found
                # This creates the desired format: #SECTION...
                anchor = f"#{anchor_id}" if anchor_id else None 

                all_chunks.append({
                    "identifier": identifier,
                    "text": text,
                    "anchor": anchor,
                    "source": str(relative_path),
                    "section_title": section['metadata']['title'],
                    "section_id": section['metadata']['section_id'],
                })

    return all_chunks


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    POSTPROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    print("--- 1. STARTING DOCUMENT PREPROCESSING (Targeting Inline Anchors) ---")
    
    # Redefine SectionMetadata to ensure it has the anchor_id when running standalone
    class SectionMetadata(TypedDict):
        title: str
        section_id: str
        anchor_id: str
    
    all_chunks = load_and_split_documents(DATA_DIR, POSTPROCESSED_DIR)
    
    if not all_chunks:
        print("Error: No chunks were generated. Check DATA_DIR and file types.")
    else:
        print(f"\nSuccessfully generated {len(all_chunks)} semantic chunks.")

        # Save the chunks to a JSON Lines file
        with open(CHUNK_OUTPUT_FILE, "w", encoding="utf-8") as f:
            for chunk in all_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
        
        print(f"--- CHUNKS SAVED TO {CHUNK_OUTPUT_FILE} ---")