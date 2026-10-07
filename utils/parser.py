import os
import re

def parse_pdf(file_path):
    """Extract text from a PDF file using PyMuPDF (fitz)."""
    text = ""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        for page in doc:
            page_text = page.get_text("text")
            if page_text:
                text += page_text + "\n"
        doc.close()
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text.strip()

def parse_docx(file_path):
    """Extract text from a DOCX file using python-docx."""
    text = ""
    try:
        import docx
        doc = docx.Document(file_path)
        # Extract paragraph text
        for paragraph in doc.paragraphs:
            if paragraph.text:
                text += paragraph.text + "\n"
        # Extract table text
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text:
                        text += cell.text + " "
                text += "\n"
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
    return text.strip()

def parse_txt(file_path):
    """Extract text from a TXT file with encoding fallbacks."""
    encodings = ['utf-8', 'latin-1', 'cp1252']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read().strip()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error reading TXT {file_path}: {e}")
            break
    return ""

def parse_resume(file_path):
    """Parses resume text depending on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return parse_pdf(file_path)
    elif ext in ['.docx', '.doc']:
        return parse_docx(file_path)
    elif ext == '.txt':
        return parse_txt(file_path)
    else:
        # Fallback to plain text reader
        return parse_txt(file_path)

def extract_candidate_name(text, filename=""):
    """
    Extract candidate name from resume text or filename.
    Looks for Name headers, email patterns, or top non-empty lines.
    """
    if not text:
        clean_fn = os.path.splitext(os.path.basename(filename))[0]
        return clean_fn.replace('_', ' ').replace('-', ' ').title()

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # 1. Check for explicit "Name: Candidate Name" or "Resume of Candidate Name"
    for line in lines[:10]:
        name_match = re.search(r'^(?:name|candidate name|full name)\s*:\s*([A-Za-z\s\.\'\-]+)', line, re.IGNORECASE)
        if name_match:
            return name_match.group(1).strip().title()

    # 2. Check header line if it looks like a clean person name (2-3 words, no numbers/symbols)
    for line in lines[:5]:
        # Ignore common titles like "RESUME", "CURRICULUM VITAE", "CONTACT", etc.
        if re.match(r'^(?:resume|curriculum vitae|cv|profile|contact information|summary)$', line, re.IGNORECASE):
            continue
        # Check if line consists of 2-4 alphabetic words
        words = line.split()
        if 1 <= len(words) <= 4 and all(re.match(r'^[A-Za-z\.\'\-]+$', w) for w in words):
            # Exclude common section headers
            if not any(header in line.lower() for header in ['education', 'skills', 'experience', 'projects', 'email', 'phone']):
                return line.strip().title()

    # 3. Fallback to filename
    clean_fn = os.path.splitext(os.path.basename(filename))[0]
    # Remove leading digits or 'resume' prefix if any
    clean_fn = re.sub(r'^(?:resume|cv)[_\-\s]*', '', clean_fn, flags=re.IGNORECASE)
    clean_fn = re.sub(r'^[0-9]+[_\-\s]*', '', clean_fn)
    return clean_fn.replace('_', ' ').replace('-', ' ').title() or "Candidate"
