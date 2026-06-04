import re
import os
from pypdf import PdfReader
# pyrefly: ignore [missing-import]
import docx

# A predefined master list of common skills to match against
SKILLS_DB = [
    'python', 'java', 'c++', 'c#', 'ruby', 'php', 'golang', 'rust', 'swift', 'kotlin',
    'javascript', 'typescript', 'html', 'css', 'sass', 'bootstrap', 'tailwind',
    'react', 'angular', 'vue', 'next.js', 'node.js', 'express', 'django', 'flask', 'fastapi',
    'spring boot', 'laravel', 'asp.net', 'sql', 'mysql', 'postgresql', 'mongodb', 'sqlite', 
    'redis', 'cassandra', 'elasticsearch', 'aws', 'azure', 'gcp', 'docker', 'kubernetes',
    'git', 'github', 'ci/cd', 'jenkins', 'terraform', 'ansible', 'linux', 'unix',
    'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch',
    'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'keras', 'opencv',
    'tableau', 'power bi', 'excel', 'spark', 'hadoop', 'hive', 'data structures', 'algorithms',
    'ui/ux', 'figma', 'adobe xd', 'photoshop', 'illustrator', 'wireframing', 'prototyping',
    'agile', 'scrum', 'jira', 'project management', 'communication', 'leadership', 'teamwork'
]

def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file page by page."""
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text

def extract_text_from_docx(file_path):
    """Extracts text from a DOCX file, including paragraphs and table cells."""
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            if para.text:
                text += para.text + "\n"
        # Extract text from tables if any
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text += cell.text + " "
                text += "\n"
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
    return text

def extract_text_from_txt(file_path):
    """Extracts text from a TXT file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT {file_path}: {e}")
        return ""

def extract_text(file_path):
    """Extracts text based on the file extension."""
    _, ext = os.path.splitext(file_path.lower())
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    else:
        return ""

def extract_candidate_info(text, file_name):
    """
    Heuristically extracts candidate name, email, phone number, and skills.
    Uses file name as a fallback for the candidate's name.
    """
    # 1. Clean the text slightly for email/phone matching
    cleaned_text = text.strip()
    
    # 2. Extract email using regex
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    email_match = re.search(email_pattern, cleaned_text)
    email = email_match.group(0) if email_match else "N/A"
    
    # 3. Extract phone number using regex
    # Matches formats like +91-98765-43210, +1-123-456-7890, (123) 456-7890, 123-456-7890, 1234567890, etc.
    phone_pattern = r'(?:\+?\d{1,4}[-.\s]?)?\(?\d{2,5}\)?[-.\s]?\d{2,5}[-.\s]?\d{3,6}'
    phone_match = re.search(phone_pattern, cleaned_text)
    phone = phone_match.group(0) if phone_match else "N/A"
    
    # 4. Extract skills by matching against the SKILLS_DB
    found_skills = []
    # Make sure we search using word boundaries so 'go' doesn't match 'good'
    for skill in SKILLS_DB:
        # Escape skill to handle special characters like C++ or C#
        escaped_skill = re.escape(skill)
        # We allow word boundaries. Note: for c++ and c#, word boundary \b doesn't work well on trailing special chars.
        # We build a custom regex boundary check
        if '+' in skill or '#' in skill:
            pattern = rf'(?i)(?:^|[\s,;.]){escaped_skill}(?:$|[\s,;.])'
        else:
            pattern = rf'(?i)\b{escaped_skill}\b'
            
        if re.search(pattern, cleaned_text):
            # Format the skill to look nice (matching the capitalization in SKILLS_DB)
            found_skills.append(skill)
            
    # 5. Extract Candidate Name heuristically
    # Split text into lines
    lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
    candidate_name = ""
    
    # Fallback to file name if no name found
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    # Clean file name (remove underscores, hyphens, and title case it)
    clean_base_name = re.sub(r'[_|-]', ' ', base_name).title()
    # Remove words like "Resume" or "CV" from the base name
    clean_base_name = re.sub(r'(?i)\b(resume|cv|pdf|docx|txt|final|latest)\b', '', clean_base_name).strip()
    
    # Check first few lines for name
    # Usually a name is 2-3 capitalized words in the first 3 lines
    name_found = False
    for line in lines[:5]:  # Look at the first 5 lines to be safer
        # Skip lines that look like emails, phone numbers, addresses, or resume titles
        if "@" in line or any(c.isdigit() for c in line) and len(line) < 15:
            continue
        if re.search(r'(?i)(resume|curriculum|cv|portfolio|profile|contact|summary)', line):
            continue
        # Skip lines that contain social media or contact keywords
        if re.search(r'(?i)(github|linkedin|gmail|yahoo|email|phone|mobile|website|http|www|\.com)', line):
            continue
            
        # Check if line contains 1 to 4 capitalized words (candidate name)
        words = line.split()
        if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
            # Make sure it's not just a single word like 'Personal' or 'Details'
            if len(words) == 1 and re.search(r'(?i)(personal|details|info|about)', words[0]):
                continue
            candidate_name = line
            name_found = True
            break
            
    if not name_found or not candidate_name:
        candidate_name = clean_base_name if clean_base_name else "Unknown Candidate"
        
    return {
        "name": candidate_name,
        "email": email,
        "phone": phone,
        "skills": found_skills
    }
