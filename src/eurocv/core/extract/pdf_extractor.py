"""PDF extraction functionality."""

import re
from pathlib import Path
from typing import Optional, Dict, Any, List
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text as pdfminer_extract_text
from pdfminer.layout import LAParams

from eurocv.core.models import Resume, PersonalInfo, WorkExperience, Education, Language, Skill


class PDFExtractor:
    """Extract text and structure from PDF files."""
    
    def __init__(self, use_ocr: bool = False):
        """Initialize extractor.
        
        Args:
            use_ocr: Whether to use OCR for scanned PDFs (requires pytesseract)
        """
        self.use_ocr = use_ocr
    
    def extract(self, file_path: str) -> Resume:
        """Extract resume data from PDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Resume object with extracted data
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        # Try PyMuPDF first (better for most PDFs)
        try:
            text, metadata = self._extract_with_pymupdf(str(path))
        except Exception:
            # Fallback to pdfminer.six
            text, metadata = self._extract_with_pdfminer(str(path))
        
        # Parse the extracted text into structured data
        resume = self._parse_text_to_resume(text, metadata)
        resume.raw_text = text
        resume.metadata.update(metadata)
        
        return resume
    
    def _extract_with_pymupdf(self, file_path: str) -> tuple[str, Dict[str, Any]]:
        """Extract text using PyMuPDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Tuple of (text content, metadata dict)
        """
        doc = fitz.open(file_path)
        text_parts = []
        metadata = {
            "page_count": len(doc),
            "format": "PDF",
            "extractor": "pymupdf",
        }
        
        # Extract metadata
        if doc.metadata:
            metadata.update({
                "title": doc.metadata.get("title"),
                "author": doc.metadata.get("author"),
                "subject": doc.metadata.get("subject"),
                "keywords": doc.metadata.get("keywords"),
            })
        
        # Extract text from each page
        for page_num, page in enumerate(doc, 1):
            # Check if page is likely scanned (no text)
            page_text = page.get_text()
            
            if not page_text.strip() and self.use_ocr:
                # Use OCR for scanned pages
                page_text = self._ocr_page(page)
            
            text_parts.append(page_text)
        
        doc.close()
        
        return "\n\n".join(text_parts), metadata
    
    def _extract_with_pdfminer(self, file_path: str) -> tuple[str, Dict[str, Any]]:
        """Extract text using pdfminer.six.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Tuple of (text content, metadata dict)
        """
        laparams = LAParams(
            line_margin=0.5,
            word_margin=0.1,
            char_margin=2.0,
            boxes_flow=0.5,
        )
        
        text = pdfminer_extract_text(file_path, laparams=laparams)
        
        metadata = {
            "format": "PDF",
            "extractor": "pdfminer",
        }
        
        return text, metadata
    
    def _ocr_page(self, page: fitz.Page) -> str:
        """OCR a page using Tesseract.
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            Extracted text
        """
        try:
            import pytesseract
            from PIL import Image
            import io
            
            # Convert page to image
            pix = page.get_pixmap(dpi=300)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Run OCR
            text = pytesseract.image_to_string(img, lang='eng+nld')
            return text
        except ImportError:
            # OCR dependencies not installed
            return ""
    
    def _parse_text_to_resume(self, text: str, metadata: Dict[str, Any]) -> Resume:
        """Parse extracted text into structured Resume.
        
        This is a heuristic-based parser. For better results, consider:
        - Training a custom NER model
        - Using a pre-trained model for resume parsing
        - Implementing layout analysis
        
        Args:
            text: Extracted text
            metadata: Document metadata
            
        Returns:
            Resume object
        """
        resume = Resume()
        
        # Extract personal info
        resume.personal_info = self._extract_personal_info(text)
        
        # Extract sections
        sections = self._split_into_sections(text)
        
        # Extract work experience
        if "experience" in sections or "work" in sections:
            work_section = sections.get("experience") or sections.get("work", "")
            resume.work_experience = self._extract_work_experience(work_section)
        
        # Extract education
        if "education" in sections:
            resume.education = self._extract_education(sections["education"])
        
        # Extract languages
        if "language" in sections:
            resume.languages = self._extract_languages(sections["language"])
        
        # Extract skills
        if "skill" in sections:
            resume.skills = self._extract_skills(sections["skill"])
        
        # Extract summary
        if "summary" in sections or "profile" in sections:
            resume.summary = sections.get("summary") or sections.get("profile")
        
        return resume
    
    def _extract_personal_info(self, text: str) -> PersonalInfo:
        """Extract personal information from text.
        
        Args:
            text: Resume text
            
        Returns:
            PersonalInfo object
        """
        info = PersonalInfo()
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_matches = re.findall(email_pattern, text)
        if email_matches:
            info.email = email_matches[0]
        
        # Extract phone
        phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
        phone_matches = re.findall(phone_pattern, text[:500])  # Look in first 500 chars
        if phone_matches:
            info.phone = phone_matches[0]
        
        # Extract name (heuristic: first line or lines before contact info)
        lines = text.split('\n')
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line = line.strip()
            if line and len(line.split()) >= 2 and len(line) < 50:
                # Likely a name (2+ words, not too long)
                if not any(char.isdigit() for char in line) and '@' not in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        info.first_name = parts[0]
                        info.last_name = ' '.join(parts[1:])
                        break
        
        return info
    
    def _split_into_sections(self, text: str) -> Dict[str, str]:
        """Split resume text into sections.
        
        Args:
            text: Resume text
            
        Returns:
            Dict mapping section names to content
        """
        sections = {}
        
        # Common section headers
        section_patterns = {
            "summary": r"(?i)(professional\s+summary|profile|summary|objective)",
            "experience": r"(?i)(work\s+experience|professional\s+experience|employment|experience)",
            "education": r"(?i)(education|academic|qualifications)",
            "skill": r"(?i)(skills|competencies|expertise)",
            "language": r"(?i)(languages|language\s+skills)",
        }
        
        # Find section positions
        section_positions = []
        for section_key, pattern in section_patterns.items():
            matches = list(re.finditer(pattern, text))
            for match in matches:
                section_positions.append((match.start(), section_key, match.group()))
        
        # Sort by position
        section_positions.sort()
        
        # Extract section content
        for i, (start, key, header) in enumerate(section_positions):
            # Find end of section (next section or end of text)
            if i + 1 < len(section_positions):
                end = section_positions[i + 1][0]
            else:
                end = len(text)
            
            content = text[start:end].strip()
            # Remove the header line
            content = re.sub(f"^{re.escape(header)}", "", content, flags=re.IGNORECASE).strip()
            
            sections[key] = content
        
        return sections
    
    def _extract_work_experience(self, text: str) -> List[WorkExperience]:
        """Extract work experience entries.
        
        Args:
            text: Work experience section text
            
        Returns:
            List of WorkExperience objects
        """
        experiences = []
        
        # Split into entries (heuristic: look for date patterns)
        date_pattern = r'\b(20\d{2}|19\d{2})\b|\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b'
        
        # For now, create a single entry with all content
        # TODO: Implement better entry splitting
        if text.strip():
            exp = WorkExperience(description=text.strip()[:1000])  # Limit length
            experiences.append(exp)
        
        return experiences
    
    def _extract_education(self, text: str) -> List[Education]:
        """Extract education entries.
        
        Args:
            text: Education section text
            
        Returns:
            List of Education objects
        """
        education_list = []
        
        # For now, create a single entry
        # TODO: Implement better entry splitting
        if text.strip():
            edu = Education(description=text.strip()[:1000])
            education_list.append(edu)
        
        return education_list
    
    def _extract_languages(self, text: str) -> List[Language]:
        """Extract language skills.
        
        Args:
            text: Language section text
            
        Returns:
            List of Language objects
        """
        languages = []
        
        # Common languages
        language_names = [
            "English", "Dutch", "German", "French", "Spanish", "Italian",
            "Portuguese", "Chinese", "Japanese", "Russian", "Arabic"
        ]
        
        # CEFR levels
        cefr_pattern = r'\b([A-C][1-2])\b'
        
        for lang in language_names:
            if re.search(rf'\b{lang}\b', text, re.IGNORECASE):
                language = Language(language=lang)
                
                # Try to find CEFR level near the language name
                context = text[max(0, text.lower().find(lang.lower()) - 50):
                              text.lower().find(lang.lower()) + 100]
                cefr_match = re.search(cefr_pattern, context)
                if cefr_match:
                    level = cefr_match.group(1)
                    language.listening = level
                    language.reading = level
                    language.speaking = level
                    language.writing = level
                
                languages.append(language)
        
        return languages
    
    def _extract_skills(self, text: str) -> List[Skill]:
        """Extract skills.
        
        Args:
            text: Skills section text
            
        Returns:
            List of Skill objects
        """
        skills = []
        
        # Split by common delimiters
        skill_items = re.split(r'[,•\n]', text)
        
        for item in skill_items:
            item = item.strip()
            if item and len(item) > 2 and len(item) < 100:
                skill = Skill(name=item)
                skills.append(skill)
        
        return skills

