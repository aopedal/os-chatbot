import json
from pathlib import Path
from typing import List, Dict
from urllib.parse import quote

# LangChain/Utilities
from langchain_text_splitters import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
DATA_DIR = Path("./knowledge")
POSTPROCESSED_DIR = Path("./knowledge_processed")
CHUNK_OUTPUT_FILE = "processed_chunks.jsonl"  # File to store all chunks

# Chunking
TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=900)

# --- HELPER FUNCTIONS ---

def generate_text_fragment_anchor(text: str, max_chars: int = 60) -> str:
    """
    Generates a #:~:text= style anchor for a chunk.
    Takes the first max_chars of the chunk as the highlight text.
    """
    snippet = text.strip().replace("\n", " ")
    if len(snippet) > max_chars:
        snippet = snippet[:max_chars]
    encoded = quote(snippet, safe="")
    return f"#:~:text={encoded}"


from bs4 import BeautifulSoup, Tag, Comment
from bs4.element import NavigableString
from pathlib import Path

from bs4 import BeautifulSoup, Tag, Comment
from bs4.element import NavigableString
from pathlib import Path

def extract_content_traversal(path: Path, save_path: Path) -> str | None:

    print(f"Loading {path}...")
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    if path.suffix.lower() != ".html":
        if path.suffix.lower() == ".txt":
            with open(path, "r", encoding="utf-8") as f:
                text_content = f.read().strip()
            return text_content
        return None 

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
        
    output_lines = []
    
    RECURSION_SKIP = ['h1', 'h2', 'h3', 'li', 'table', 'pre', 'a']
    BREAK_AFTER = ['h1', 'h2', 'h3', 'p', 'li'] 
    BREAK_BEFORE = ['h1', 'h2', 'h3', 'p', 'ul', 'ol', 'pre', 'table']

    def get_tag_text(element):
        """Recursively extracts text, ensuring new lines and preventing duplication."""
        
        # 1. Handle NavigableString (Text Node) - REVISED LOGIC
        if isinstance(element, NavigableString):
            stripped_text = str(element).strip()
            if stripped_text:
                # If the last line is not a hard block break ('\n'), aggressively concatenate.
                if output_lines and output_lines[-1] and not output_lines[-1].endswith('\n'):
                    # Ensure space separation if needed
                    if not output_lines[-1].endswith(' '):
                        output_lines[-1] += ' '
                    output_lines[-1] += stripped_text
                else:
                    # If the last item was a newline or the list is empty, append as a new item.
                    output_lines.append(stripped_text)
            return 
        
        # 2. Handle Tag (Element)
        
        # --- REVISED <em> HANDLING ---
        elif element.name == 'em':
            italic_text = f"*{element.get_text(strip=False).strip()}*"
            
            # Concatenate aggressively onto the last line item, treating it as inline text.
            if output_lines and output_lines[-1] and not output_lines[-1].endswith('\n'):
                 if not output_lines[-1].endswith(' '):
                    output_lines[-1] += ' '
                 output_lines[-1] += italic_text
            else:
                 output_lines.append(italic_text)
            
            return # Skip children since we used get_text()

        # --- BLOCK ELEMENT START ---
        if element.name in BREAK_BEFORE:
            output_lines.append('\n\n')

        # Handle Headings
        if element.name in ['h1', 'h2', 'h3']:
            text = element.text.strip()
            if element.name == 'h1' and "Forelesning slides ." in text:
                 text = text.split("Forelesning slides .")[0].strip()
            output_lines.append(text)
            
        # Handle Lists
        elif element.name == 'li':
            output_lines.append(f'* {element.text.strip()}')

        # Handle Links
        elif element.name == 'a':
            link_text = element.text.strip()
            if link_text:
                output_lines.append(link_text)

        # Handle Code Blocks (PRE)
        elif element.name == 'pre':
            output_lines.append('---CODE START---')
            output_lines.append(element.get_text(strip=False).strip())
            output_lines.append('---CODE END---')

        elif element.name == 'table':
            
            pre_tags = element.find_all('pre')
            td_tags = element.find_all('td')
            th_tags = element.find_all('th')
            
            is_code_table = (
                len(pre_tags) == 1 and 
                len(td_tags) <= 1 and 
                len(th_tags) == 0
            )

            # Extract Caption and DECOMPOSE it
            caption = element.find('caption', class_='BOTTOM')
            caption_text = None
            if caption:
                caption_text = caption.text.strip().replace("Figure: Figure:", "Figure:").replace("Figure: Figure", "Figure:")
                caption.decompose() 

            if is_code_table:
                # TREAT AS CODE BLOCK ONLY
                output_lines.append('---CODE START---')
                output_lines.append(pre_tags[0].get_text(strip=False).strip())
                output_lines.append('---CODE END---')
                if caption_text:
                    output_lines.append(caption_text)
            else:
                # TREAT AS STANDARD TABLE
                output_lines.append('\n---TABLE START---')
                
                headers = [th.text.strip() for th in element.find_all('th')]
                if headers: 
                    output_lines.append(" | ".join(headers) + " |")
                
                for tr in element.find_all('tr'):
                    row_data = [td.text.strip() for td in tr.find_all('td')]
                    output_lines.append(" | ".join([d for d in row_data if d]) + " |")
                
                if caption_text:
                    output_lines.append(caption_text)
                    
                output_lines.append('---TABLE END---')

        # 3. RECURSION
        if element.name not in RECURSION_SKIP and element.name != 'em':
            for child in element.children: 
                if isinstance(child, (Tag, NavigableString)):
                    get_tag_text(child)

        # 4. BREAK AFTER
        if element.name in BREAK_AFTER and output_lines and output_lines[-1].strip() not in ('\n', ''):
            output_lines.append('\n')

    # Start recursion from the body tag
    if soup.body:
        for child in soup.body.children:
             if isinstance(child, (Tag, NavigableString)):
                 get_tag_text(child)
    
    # --- 3. FINAL CLEANUP ---
    text_content = "\n".join([line.strip() for line in output_lines if line.strip() or line.startswith(('*', '-'))])
    text_content = text_content.replace('\n\n\n', '\n\n').strip()
    
    # Save the processed text
    if text_content:
        save_path = save_path.with_suffix(".txt")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(text_content)
        print(f"  -> Saved postprocessed text to {save_path}")
        
    return text_content


def load_and_split_documents(data_dir: Path, postprocessed_dir: Path) -> List[Dict]:
    """
    Walks through data_dir recursively, extracts content, splits into chunks,
    and generates text-fragment anchors for HTML files.
    Returns a list of flattened chunk dictionaries.
    """
    all_chunks = []

    for path in data_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in [".html", ".txt"]:
            relative_path = path.relative_to(data_dir)
            save_path = postprocessed_dir / relative_path

            content = extract_content_traversal(path, save_path)
            if not content:
                continue

            chunks = TEXT_SPLITTER.split_text(content)
            for i, chunk in enumerate(chunks):
                chunk_id = f"{relative_path.stem}_{i}_{len(chunk)}"
                anchor = generate_text_fragment_anchor(chunk) if path.suffix.lower() == ".html" else None

                all_chunks.append({
                    "identifier": chunk_id,
                    "text": chunk,
                    "anchor": anchor,
                    "source": str(relative_path),
                })

    return all_chunks


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    POSTPROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    print("--- 1. STARTING DOCUMENT PREPROCESSING ---")
    
    all_chunks = load_and_split_documents(DATA_DIR, POSTPROCESSED_DIR)
    
    if not all_chunks:
        print("Error: No chunks were generated. Check DATA_DIR and file types.")
    else:
        print(f"\nSuccessfully generated {len(all_chunks)} total chunks.")

        # Save the chunks to a JSON Lines file
        with open(CHUNK_OUTPUT_FILE, "w", encoding="utf-8") as f:
            for chunk in all_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
        
        print(f"--- CHUNKS SAVED TO {CHUNK_OUTPUT_FILE} ---")