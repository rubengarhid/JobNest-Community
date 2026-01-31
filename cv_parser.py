"""
CV Parser Module
Extracts and normalizes text from PDF and DOCX files.
Uses heuristics to identify sections: experience, skills, education.
"""

import re
from typing import Dict, List, Optional
import pdfplumber
from docx import Document


class CVParser:
    """Parser for extracting structured data from CV files."""
    
    # Section headers patterns (case-insensitive)
    EXPERIENCE_PATTERNS = [
        r'work\s+experience',
        r'professional\s+experience',
        r'employment\s+history',
        r'work\s+history',
        r'experience',
        r'experiencia\s+laboral',
        r'experiencia\s+profesional',
    ]
    
    SKILLS_PATTERNS = [
        r'skills',
        r'technical\s+skills',
        r'competencies',
        r'technologies',
        r'habilidades',
        r'competencias',
    ]
    
    EDUCATION_PATTERNS = [
        r'education',
        r'academic\s+background',
        r'qualifications',
        r'formación',
        r'educación',
    ]
    
    def __init__(self):
        """Initialize the CV Parser."""
        self.experience_regex = self._compile_patterns(self.EXPERIENCE_PATTERNS)
        self.skills_regex = self._compile_patterns(self.SKILLS_PATTERNS)
        self.education_regex = self._compile_patterns(self.EDUCATION_PATTERNS)
    
    @staticmethod
    def _compile_patterns(patterns: List[str]) -> re.Pattern:
        """Compile multiple patterns into a single regex."""
        combined = '|'.join(f'({pattern})' for pattern in patterns)
        return re.compile(combined, re.IGNORECASE)
    
    def read_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text as string
        """
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise ValueError(f"Error reading PDF: {str(e)}")
        
        return text.strip()
    
    def read_docx(self, file_path: str) -> str:
        """
        Extract text from DOCX file.
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            Extracted text as string
        """
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            raise ValueError(f"Error reading DOCX: {str(e)}")
        
        return text.strip()
    
    def read_file(self, file_path: str) -> str:
        """
        Read file based on extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text
        """
        if file_path.lower().endswith('.pdf'):
            return self.read_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            return self.read_docx(file_path)
        else:
            raise ValueError("Unsupported file format. Use PDF or DOCX.")
    
    def _split_into_sections(self, text: str) -> Dict[str, str]:
        """
        Split CV text into sections based on headers.
        
        Args:
            text: Full CV text
            
        Returns:
            Dictionary with sections
        """
        sections = {
            'experience': '',
            'skills': '',
            'education': '',
            'other': ''
        }
        
        lines = text.split('\n')
        current_section = 'other'
        
        for line in lines:
            line_lower = line.strip().lower()
            
            # Check which section this line belongs to
            if self.experience_regex.search(line_lower):
                current_section = 'experience'
                continue
            elif self.skills_regex.search(line_lower):
                current_section = 'skills'
                continue
            elif self.education_regex.search(line_lower):
                current_section = 'education'
                continue
            
            # Add line to current section
            if line.strip():
                sections[current_section] += line + '\n'
        
        # Clean sections
        for key in sections:
            sections[key] = sections[key].strip()
        
        return sections
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract potential skills from text using heuristics.
        
        Args:
            text: Text to extract skills from
            
        Returns:
            List of identified skills
        """
        # Common skill keywords
        skill_keywords = [
            'python', 'java', 'javascript', 'c\\+\\+', 'sql', 'html', 'css',
            'react', 'angular', 'vue', 'node', 'django', 'flask', 'fastapi',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git',
            'machine learning', 'deep learning', 'ai', 'data science',
            'agile', 'scrum', 'devops', 'ci/cd',
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in skill_keywords:
            if re.search(r'\b' + skill + r'\b', text_lower):
                # Capitalize first letter of each word
                found_skills.append(skill.replace('\\+\\+', '++').title())
        
        return list(set(found_skills))  # Remove duplicates
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse CV file and extract structured data.
        
        Args:
            file_path: Path to CV file
            
        Returns:
            Dictionary with parsed CV data
        """
        # Read file
        full_text = self.read_file(file_path)
        
        # Split into sections
        sections = self._split_into_sections(full_text)
        
        # Extract skills from skills section
        skills = self.extract_skills(sections['skills'])
        
        # If no skills found in skills section, try experience section
        if not skills:
            skills = self.extract_skills(sections['experience'])
        
        return {
            'full_text': full_text,
            'experience': sections['experience'],
            'skills': sections['skills'],
            'education': sections['education'],
            'other': sections['other'],
            'extracted_skills': skills
        }


def parse_cv_from_bytes(file_bytes: bytes, filename: str) -> Dict:
    """
    Parse CV from bytes (for API uploads).
    
    Args:
        file_bytes: File content as bytes
        filename: Original filename
        
    Returns:
        Parsed CV data
    """
    import tempfile
    import os
    
    # Create temporary file
    suffix = os.path.splitext(filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(file_bytes)
        tmp_path = tmp_file.name
    
    try:
        parser = CVParser()
        result = parser.parse(tmp_path)
        return result
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# Example usage
if __name__ == "__main__":
    parser = CVParser()
    
    # Example: Parse a sample CV
    sample_text = """
    JOHN DOE
    Software Engineer
    
    EXPERIENCE
    Senior Developer at Tech Corp (2020-2023)
    - Developed Python applications
    - Led team of 5 developers
    
    SKILLS
    Python, JavaScript, React, AWS, Docker
    
    EDUCATION
    BS Computer Science, University XYZ (2016-2020)
    """
    
    sections = parser._split_into_sections(sample_text)
    skills = parser.extract_skills(sample_text)
    
    print("Sections:", sections)
    print("\nExtracted Skills:", skills)
