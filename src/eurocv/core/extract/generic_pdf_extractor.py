"""Generic PDF extraction functionality with multi-language support."""

import re
from datetime import date
from pathlib import Path
from typing import Any, Optional

import fitz  # PyMuPDF
from pdfminer.high_level import extract_text as pdfminer_extract_text
from pdfminer.layout import LAParams

from eurocv.core.extract.base_extractor import ResumeExtractor
from eurocv.core.models import (
    Certification,
    Education,
    Language,
    PersonalInfo,
    Resume,
    Skill,
    WorkExperience,
)


class GenericPDFExtractor(ResumeExtractor):
    """Extract text and structure from PDF files with multi-language support.

    Supports English and Dutch language CVs with various layouts including
    sidebar designs and non-standard formatting.
    """

    # Multi-language section headers
    SECTION_HEADERS = {
        "work": [
            "work experience",
            "experience",
            "employment",
            "ervaring",
            "werkervaring",
            "professional experience",
        ],
        "education": ["education", "academic", "opleiding", "onderwijs", "studies"],
        "skills": [
            "skills",
            "competencies",
            "vaardigheden",
            "competenties",
            "expertise",
        ],
        "languages": ["languages", "talen", "language skills"],
        "certifications": [
            "certifications",
            "certificates",
            "certificaten",
            "licenses",
        ],
        "summary": ["summary", "profile", "about", "samenvatting", "profiel"],
    }

    # Dutch month abbreviations
    DUTCH_MONTHS = {
        "jan": "01",
        "januari": "01",
        "feb": "02",
        "februari": "02",
        "mrt": "03",
        "maart": "03",
        "apr": "04",
        "april": "04",
        "mei": "05",
        "jun": "06",
        "juni": "06",
        "jul": "07",
        "juli": "07",
        "aug": "08",
        "augustus": "08",
        "sep": "09",
        "sept": "09",
        "september": "09",
        "okt": "10",
        "oktober": "10",
        "nov": "11",
        "november": "11",
        "dec": "12",
        "december": "12",
    }

    # Keywords for "present" in multiple languages (A2: Enhanced Dutch support)
    PRESENT_KEYWORDS = [
        "present",
        "current",
        "heden",
        "nu",
        "now",
        "today",
        "ongoing",
        "tot heden",  # until present (Dutch)
        "tot nu",  # until now (Dutch)
        "vanaf",  # from (Dutch)
        "sinds",  # since (Dutch)
    ]

    # Language proficiency mapping
    PROFICIENCY_MAP = {
        "native": "Native",
        "moedertaal": "Native",
        "proficient": "C2",
        "vloeiend": "C2",
        "fluent": "C2",
        "advanced": "C1",
        "gevorderd": "C1",
        "intermediate": "B1",
        "gemiddeld": "B1",
        "basic": "A2",
        "basis": "A2",
        "beginner": "A1",
        "beginner level": "A1",
    }

    def __init__(self, use_ocr: bool = False):
        """Initialize extractor.

        Args:
            use_ocr: Whether to use OCR for scanned PDFs (requires pytesseract)
        """
        self.use_ocr = use_ocr

    @property
    def name(self) -> str:
        """Return extractor name."""
        return "Generic PDF"

    def can_handle(self, file_path: str) -> bool:
        """Check if this extractor can handle the file.

        Generic extractor accepts all PDF files as fallback.

        Args:
            file_path: Path to the file

        Returns:
            True if file is a PDF
        """
        return file_path.lower().endswith(".pdf")

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

    def _extract_with_pymupdf(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text using PyMuPDF.

        Args:
            file_path: Path to PDF file

        Returns:
            Tuple of (text content, metadata dict)
        """
        with fitz.open(file_path) as doc:
            text_parts = []
            metadata = {
                "page_count": len(doc),
                "format": "PDF",
                "extractor": "pymupdf",
            }

            # Extract metadata
            if doc.metadata:
                metadata.update(
                    {
                        "title": doc.metadata.get("title"),
                        "author": doc.metadata.get("author"),
                        "subject": doc.metadata.get("subject"),
                        "keywords": doc.metadata.get("keywords"),
                    }
                )

            # Extract text from each page
            for page_num, page in enumerate(doc, 1):
                # Check if page is likely scanned (no text)
                page_text = page.get_text()

                if not page_text.strip() and self.use_ocr:
                    # Use OCR for scanned pages
                    page_text = self._ocr_page(page)

                text_parts.append(page_text)

        return "\n\n".join(text_parts), metadata

    def _extract_with_pdfminer(self, file_path: str) -> tuple[str, dict[str, Any]]:
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
            import io

            import pytesseract
            from PIL import Image

            # Convert page to image
            pix = page.get_pixmap(dpi=300)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))

            # Run OCR
            text = pytesseract.image_to_string(img, lang="eng+nld")
            return text
        except ImportError:
            # OCR dependencies not installed
            return ""

    def _parse_text_to_resume(self, text: str, metadata: dict[str, Any]) -> Resume:
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
        # Due to PDF column layouts, work experiences may appear in multiple sections
        work_experiences = []
        if "experience" in sections or "work" in sections:
            work_section = sections.get("experience") or sections.get("work", "")
            work_experiences.extend(self._extract_work_experience(work_section))

        # Also check language section (column layout may place work exp there)
        if "language" in sections:
            lang_section = sections["language"]
            # Only extract if it contains job-like entries (has date ranges with positions)
            if re.search(
                r"[A-Z\s]{10,}\n[A-Z\s]{5,}\n(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|Okt)\s+\d{4}\s*[-–—]",
                lang_section,
            ):
                work_experiences.extend(self._extract_work_experience(lang_section))

        resume.work_experience = work_experiences

        # Extract education
        if "education" in sections:
            resume.education = self._extract_education(sections["education"])

        # Extract languages (check section first, then full text)
        if "language" in sections:
            resume.languages = self._extract_languages(sections["language"])
        else:
            # Try extracting from full text (languages might be in sidebar)
            resume.languages = self._extract_languages(text)

        # Extract skills
        if "skill" in sections:
            resume.skills = self._extract_skills(sections["skill"])

        # Extract certifications
        if "certification" in sections:
            resume.certifications = self._extract_certifications(
                sections["certification"]
            )

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
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        email_matches = re.findall(email_pattern, text)
        if email_matches:
            info.email = email_matches[0]

        # Extract phone - look more carefully in header (A3: Enhanced patterns)
        phone_patterns = [
            # International with (0) notation: +31 (0)6 12345678
            r"\+\d{1,3}\s*\(0\)\s*\d{1,3}\s*\d{6,8}",
            # International standard: +31-6-12345678, +31 6 12345678
            r"\+\d{1,3}[-\s]?\d{1,3}[-\s]?\d{6,8}",
            # Dutch mobile: 06-12345678, 0612345678
            r"0\d{1}[-\s]?\d{8}",
            # Dutch landline with area code: (020) 1234567, 020-1234567
            r"\(?\d{2,4}\)?[-\s]?\d{6,7}",
            # US format: (555) 123-4567, +1 (555) 123-4567
            r"\+?1?\s*\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}",
            # UK format: +44 20 1234 5678
            r"\+44\s*\d{2,4}\s*\d{4}\s*\d{4}",
            # Generic international
            r"[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}",
        ]

        # Look in first 2000 chars for phone in header/contact section
        phone_matches = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text[:2000])
            phone_matches.extend(matches)

        if phone_matches:
            # Filter out years (4 digits only) and validate length
            valid_phones = []
            for p in phone_matches:
                clean_phone = (
                    p.replace(" ", "")
                    .replace("-", "")
                    .replace(".", "")
                    .replace("(", "")
                    .replace(")", "")
                )
                # Skip if it's just a 4-digit year
                if re.match(r"^\d{4}$", clean_phone):
                    continue
                # Keep if it's a reasonable phone length (6-15 digits)
                if 6 <= len(re.sub(r"\D", "", clean_phone)) <= 15:
                    valid_phones.append(p)

            if valid_phones:
                info.phone = valid_phones[0]

        # Extract name (improved heuristic)
        info.first_name, info.last_name = self._extract_name(text)

        # Extract location from header
        info.city, info.country = self._extract_location_from_header(text)

        return info

    def _extract_name(self, text: str) -> tuple[str, str]:
        """Extract person name from text using improved heuristics.

        Args:
            text: Resume text

        Returns:
            Tuple of (first_name, last_name)
        """
        lines = text.split("\n")
        candidates = []

        # Common sidebar headings and phrases to skip
        sidebar_headings = [
            "contact",
            "top skills",
            "skills",
            "languages",
            "certifications",
            "certificates",
            "summary",
            "profile",
            "experience",
            "education",
            "expertise",
            "competencies",
            "about",
            "honors",
            "awards",
            "other languages",
            "spoken english",
            "native or",
            "limited working",
        ]

        for i, line in enumerate(lines[:30]):  # Check first 30 lines
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip common section headings
            if line.lower() in sidebar_headings:
                continue

            # Skip lines with URLs or common non-name patterns
            skip_patterns = [
                r"www\.",
                r"http",
                r"\.com",
                r"\.nl",
                r"\.org",
                r"linkedin",
                r"\(.*\)",  # Text in parentheses
                r"@",  # Email
                r"\d{4}",  # Years
                r"page\s+\d+",  # Page numbers
                r"&",  # Ampersands (often in titles)
                r"\|",  # Pipes (often in titles)
            ]

            if any(
                re.search(pattern, line, re.IGNORECASE) for pattern in skip_patterns
            ):
                continue

            # Check if line looks like a name
            words = line.split()

            # Name should be exactly 2-3 words, each capitalized
            if 2 <= len(words) <= 3:
                # Check if all words are title case and mostly alpha
                if all(
                    word[0].isupper()
                    and word.replace("-", "").replace("'", "").isalpha()
                    for word in words
                    if word
                ):
                    # Calculate a score for this candidate
                    score = 0

                    # Strongly prefer exactly 2 words (First Last)
                    if len(words) == 2:
                        score += 10
                    elif len(words) == 3:
                        score += 5

                    # Prefer short words (first and last names are usually short)
                    if all(3 <= len(word) <= 15 for word in words):
                        score += 5

                    # Prefer lines that are standalone (not too much around them)
                    if len(line) < 30:
                        score += 3

                    # STRONGLY prefer lines 20-25 (typical name position in LinkedIn)
                    if 20 <= i <= 25:
                        score += 20  # Strong bonus for likely name position
                    elif i >= 15:
                        score += 4  # Prefer middle section

                    # Check if words look like common first names (heuristic: ends with common suffixes)
                    first_word = words[0]
                    # Common name endings
                    if any(
                        first_word.endswith(suffix)
                        for suffix in ["el", "an", "en", "on", "er", "le", "ie"]
                    ):
                        score += 2

                    # Bonus for credential format (e.g., "Name, MSc")
                    if "," in line and any(
                        cred in line.lower()
                        for cred in ["msc", "bsc", "phd", "ma", "ba", "mba"]
                    ):
                        score += 5

                    candidates.append((score, words, i, line))

        # After checking standard format, try comma-separated format
        if not candidates:
            for i, line in enumerate(lines[:30]):
                line = line.strip()
                # Check for "Firstname Lastname, Credentials" format
                if "," in line and 2 <= len(line.split(",")[0].split()) <= 3:
                    parts = [p.strip() for p in line.split(",")]
                    name_part = parts[0]
                    words = name_part.split()
                    if 2 <= len(words) <= 3 and all(
                        word and word[0].isupper() for word in words
                    ):
                        candidates.append(
                            (10, words, i, line)
                        )  # High score for comma format

        # Sort by score and pick best candidate
        if candidates:
            candidates.sort(reverse=True)
            best_words = candidates[0][1]

            first_name = best_words[0]
            last_name = " ".join(best_words[1:])
            return first_name, last_name

        return None, None

    def _extract_location_from_header(self, text: str) -> tuple[str, str]:
        """Extract location (city, country) from resume header (A4: Enhanced).

        Args:
            text: Resume text

        Returns:
            Tuple of (city, country)
        """
        # Common location patterns in headers
        # Format: "City, Region, Country" or "City, Country"
        lines = text.split("\n")

        # Check first 50 lines for location patterns
        for line in lines[:50]:
            line = line.strip()

            # Skip empty lines and URLs
            if not line or "http" in line.lower() or "@" in line:
                continue

            # Handle "Area" patterns (e.g., "Amsterdam Area", "Greater London")
            area_match = re.search(
                r"([\w\s]+)\s+(Area|Greater|Region)", line, re.IGNORECASE
            )
            if area_match:
                city = area_match.group(1).strip()
                if len(city) > 2 and len(city) < 30:
                    return city, None

            # Handle "Remote -" patterns (e.g., "Remote - Netherlands")
            remote_match = re.search(r"Remote\s*[-–]\s*([\w\s]+)", line, re.IGNORECASE)
            if remote_match:
                location = remote_match.group(1).strip()
                # Could be a country
                countries = [
                    "Netherlands",
                    "Germany",
                    "Belgium",
                    "France",
                    "United Kingdom",
                    "UK",
                    "United States",
                    "USA",
                ]
                for country in countries:
                    if country.lower() in location.lower():
                        return "Remote", country

            # Look for lines with comma-separated location info
            if "," in line:
                # Common country names and variations (A4: Expanded)
                countries = [
                    "Netherlands",
                    "Holland",
                    "Germany",
                    "Belgium",
                    "France",
                    "United Kingdom",
                    "UK",
                    "United States",
                    "USA",
                    "Spain",
                    "Italy",
                    "Portugal",
                    "Poland",
                    "Sweden",
                    "Denmark",
                    "Austria",
                    "Switzerland",
                    "Ireland",
                    "Canada",
                    "Australia",
                ]

                # Check if any country is mentioned
                for country in countries:
                    if country.lower() in line.lower():
                        # Split by comma and extract city
                        parts = [p.strip() for p in line.split(",")]
                        if len(parts) >= 2:
                            city = parts[0]
                            # Verify city looks reasonable (not too long, not just numbers)
                            if len(city) > 2 and len(city) < 30 and not city.isdigit():
                                return city, country

        # Check for standalone city names (A4: Expanded city list)
        major_cities = {
            # Dutch cities
            "Amsterdam": "Netherlands",
            "Rotterdam": "Netherlands",
            "Den Haag": "Netherlands",
            "Utrecht": "Netherlands",
            "Eindhoven": "Netherlands",
            "Groningen": "Netherlands",
            "Tilburg": "Netherlands",
            "Almere": "Netherlands",
            "Breda": "Netherlands",
            "Nijmegen": "Netherlands",
            "Apeldoorn": "Netherlands",
            "Haarlem": "Netherlands",
            "Arnhem": "Netherlands",
            "Enschede": "Netherlands",
            "Amersfoort": "Netherlands",
            "Zwolle": "Netherlands",
            "Leiden": "Netherlands",
            "Maastricht": "Netherlands",
            # International cities
            "London": "United Kingdom",
            "Berlin": "Germany",
            "Paris": "France",
            "Brussels": "Belgium",
            "New York": "USA",
            "San Francisco": "USA",
            "Munich": "Germany",
            "Barcelona": "Spain",
            "Madrid": "Spain",
            "Dublin": "Ireland",
            "Vienna": "Austria",
            "Zurich": "Switzerland",
        }

        for line in lines[:50]:
            line_clean = line.strip()
            for city, country in major_cities.items():
                if city.lower() in line_clean.lower():
                    # Check if this is likely a location (not part of company name)
                    if len(line_clean) < 50:  # Short line = likely just location
                        return city, country

        return None, None

    def _split_into_sections(self, text: str) -> dict[str, str]:
        """Split resume text into sections using multi-language headers.

        Args:
            text: Resume text

        Returns:
            Dict mapping section names to content
        """
        sections = {}

        # Build section patterns from SECTION_HEADERS
        # Match only when keyword is on its own line (section header, not in text)
        section_patterns = {}
        for section_key, keywords in self.SECTION_HEADERS.items():
            # Create a regex pattern that matches keywords as standalone headers
            # Must be at start of line or after newline, and followed by newline/whitespace
            pattern = (
                r"(?im)^[ \t]*("
                + "|".join(re.escape(kw) for kw in keywords)
                + r")[ \t]*$"
            )
            # Map internal keys to consistent names
            if section_key == "work":
                section_patterns["experience"] = pattern
            elif section_key == "certifications":
                section_patterns["certification"] = pattern
            elif section_key == "languages":
                section_patterns["language"] = pattern
            else:
                section_patterns[section_key] = pattern

        # Find section positions (use FIRST match of each section only)
        section_positions = []
        found_sections = set()
        for section_key, pattern in section_patterns.items():
            matches = list(re.finditer(pattern, text))
            if matches and section_key not in found_sections:
                # Take only the FIRST match for each section type
                match = matches[0]
                section_positions.append((match.start(), section_key, match.group()))
                found_sections.add(section_key)

        # Sort by position
        section_positions.sort()

        # Extract section content
        # Special handling: For CV with sidebar layout, ERVARING/experience section shouldn't be
        # truncated by sidebar sections (talen, certificaten, software, contact)
        sidebar_sections = {"language", "certification", "contact"}

        for i, (start, key, header) in enumerate(section_positions):
            # Find end of section (next MAJOR section or end of text)
            end = len(text)
            if i + 1 < len(section_positions):
                # If this is experience section, skip over sidebar sections to find real end
                if key == "experience":
                    for j in range(i + 1, len(section_positions)):
                        next_key = section_positions[j][1]
                        # Stop at major sections but not sidebar sections
                        if next_key not in sidebar_sections:
                            end = section_positions[j][0]
                            break
                else:
                    end = section_positions[i + 1][0]

            content = text[start:end].strip()
            # Remove the header line
            content = re.sub(
                f"^{re.escape(header)}", "", content, flags=re.IGNORECASE
            ).strip()

            sections[key] = content

        return sections

    def _extract_work_experience(self, text: str) -> list[WorkExperience]:
        """Extract work experience entries with multi-language support.

        Args:
            text: Work experience section text

        Returns:
            List of WorkExperience objects
        """
        experiences = []

        # Split text into potential entries by looking for date ranges
        # Pattern: Month YYYY - Month YYYY or Month YYYY - Present/Heden
        # Support both English and Dutch month names
        months_en = r"(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
        months_nl = r"(?:januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december|jan|feb|mrt|apr|mei|jun|jul|aug|sep|okt|nov|dec)"
        present_keywords = r"(?:Present|present|Current|current|Heden|heden|Nu|nu)"

        date_range_pattern = f"((?:{months_en}|{months_nl})\\s+\\d{{4}})\\s*[-–—]\\s*((?:{months_en}|{months_nl})\\s+\\d{{4}}|{present_keywords})"

        entries = re.split(date_range_pattern, text, flags=re.IGNORECASE)

        # Process entries
        # After split by date pattern, we get: [text_before_1, start1, end1, text_after_1, start2, end2, text_after_2, ...]
        # Note: text_after_1 contains both description AND text_before_2
        i = 0
        while i < len(entries):
            # Check if this position starts a date pattern: text, start_date, end_date, content_after
            if i + 3 <= len(entries):
                before_text = entries[i].strip()
                start_date_str = (
                    entries[i + 1].strip() if i + 1 < len(entries) else None
                )
                end_date_str = entries[i + 2].strip() if i + 2 < len(entries) else None
                content_after = entries[i + 3].strip() if i + 3 < len(entries) else ""

                # Check if we have valid date strings
                if start_date_str and end_date_str and before_text:
                    # Validate this looks like a real work entry
                    # Must have some text before dates (position/company)
                    if len(before_text) < 5:
                        i += 1
                        continue

                    exp = WorkExperience()

                    # Parse dates
                    exp.start_date = self._parse_date(start_date_str)
                    if any(
                        keyword in end_date_str.lower()
                        for keyword in ["heden", "present", "current", "nu"]
                    ):
                        exp.current = True
                        exp.end_date = None
                    else:
                        exp.end_date = self._parse_date(end_date_str)

                    # B6: Extract position and employer from text before dates
                    # Handle Dutch patterns like "bij Company" (at Company), "voor Company" (for Company)
                    # Also handle job title patterns like "Senior Developer", "Lead Engineer"

                    # The before_text might contain description from previous entry, so extract last 2-3 lines
                    lines_before = [
                        line.strip() for line in before_text.split("\n") if line.strip()
                    ]

                    # Take the last 1-2 non-empty lines as position/company (they're right before the date)
                    if lines_before:
                        if len(lines_before) >= 2:
                            # Last line is likely company, second-to-last is position
                            potential_position = lines_before[-2]
                            potential_company = lines_before[-1]

                            # B6: Handle "bij Company" or "voor Company" patterns
                            bij_match = re.search(
                                r"(bij|voor|at)\s+(.+)",
                                potential_company,
                                re.IGNORECASE,
                            )
                            if bij_match:
                                # Company is after "bij" or "voor"
                                exp.employer = bij_match.group(2).strip()
                                exp.position = potential_position
                            else:
                                # Standard pattern
                                exp.position = potential_position
                                exp.employer = potential_company

                            # B6: Detect job title patterns and enhance position
                            seniority_levels = [
                                "Senior",
                                "Junior",
                                "Lead",
                                "Principal",
                                "Staff",
                                "Associate",
                                "Head of",
                                "Chief",
                                "Director of",
                                "Medior",
                                "Intern",
                                "Trainee",
                            ]
                            # Note: Could be used for future enhancements
                            _ = any(
                                level.lower() in exp.position.lower()
                                for level in seniority_levels
                            )

                            # B6: Detect contractor/freelance indicators
                            contractor_keywords = [
                                "Freelance",
                                "Contractor",
                                "Consultant",
                                "Zelfstandig",
                                "Zzp",
                                "ZZP",
                            ]
                            is_contractor = any(
                                kw.lower() in exp.position.lower()
                                or (exp.employer and kw.lower() in exp.employer.lower())
                                for kw in contractor_keywords
                            )
                            if is_contractor and exp.description:
                                exp.description = (
                                    f"Contractor/Freelance\n{exp.description}"
                                )
                        else:
                            exp.position = lines_before[-1]

                    # Extract description from content after dates
                    # Stop when we encounter what looks like next job title (uppercase line) or take first few lines
                    content_lines = [
                        line.strip()
                        for line in content_after.split("\n")
                        if line.strip()
                    ]
                    desc_lines = []
                    for line in content_lines[:20]:
                        # Stop if we hit what looks like a new job entry (all uppercase, not a bullet)
                        if (
                            line.isupper()
                            and len(line) > 5
                            and not line.startswith("•")
                        ):
                            break
                        # Include bullet point lines and regular text
                        if line:
                            desc_lines.append(line)

                    if desc_lines:
                        exp.description = "\n".join(desc_lines[:10])

                    experiences.append(exp)
                    # Move to next entry: skip current (text, start, end, content)
                    # Next entry starts at content_after, so move by 3
                    i += 3
                    continue

            i += 1

        # Fallback: if no structured entries found, create one with all text
        if not experiences and text.strip():
            exp = WorkExperience(description=text.strip()[:1000])
            experiences.append(exp)

        return experiences

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string to date object with multi-language support.

        Args:
            date_str: Date string like "January 2020", "Jan 2020", "januari 2020"

        Returns:
            date object or None
        """
        from datetime import datetime

        from dateutil import parser

        try:
            # Try to parse with dateutil
            parsed = parser.parse(date_str, default=datetime(2000, 1, 1))
            return parsed.date()
        except Exception:
            # Try to extract at least year and month
            year_match = re.search(r"\b(19|20)\d{2}\b", date_str)
            if year_match:
                year = int(year_match.group())

                # Combine English and Dutch month names
                month_names = {
                    "jan": 1,
                    "januari": 1,
                    "january": 1,
                    "feb": 2,
                    "februari": 2,
                    "february": 2,
                    "mrt": 3,
                    "maart": 3,
                    "mar": 3,
                    "march": 3,
                    "apr": 4,
                    "april": 4,
                    "mei": 5,
                    "may": 5,
                    "jun": 6,
                    "juni": 6,
                    "june": 6,
                    "jul": 7,
                    "juli": 7,
                    "july": 7,
                    "aug": 8,
                    "augustus": 8,
                    "august": 8,
                    "sep": 9,
                    "sept": 9,
                    "september": 9,
                    "okt": 10,
                    "oct": 10,
                    "oktober": 10,
                    "october": 10,
                    "nov": 11,
                    "november": 11,
                    "dec": 12,
                    "december": 12,
                }

                for month_name, month_num in month_names.items():
                    if month_name in date_str.lower():
                        from datetime import date as date_class

                        return date_class(year, month_num, 1)

                # Just year
                from datetime import date as date_class

                return date_class(year, 1, 1)

        return None

    def _extract_education(self, text: str) -> list[Education]:
        """Extract education entries with improved multi-degree support (B5: Enhanced).

        Args:
            text: Education section text

        Returns:
            List of Education objects
        """
        education_list = []

        # Split by year ranges first to separate entries
        # Pattern: look for lines with 4-digit years (2014-2016, 2008-2011)
        lines = text.split("\n")
        current_entry = []
        current_edu = None

        # B5: Enhanced degree patterns
        degree_patterns = [
            # Full degree patterns with field
            r"(Bachelor|Master|Doctor|PhD|Doctorate)\s+(?:of\s+)?(?:Science|Arts|Engineering|Business|Laws)?\s+(?:in\s+)?(.+)",
            r"(BSc|MSc|MBA|PhD|MA|BA|BEng|MEng|LLB|LLM)\s+(?:in\s+)?(.+)?",
            # Dutch degrees
            r"(HBO|WO|MBO|Doctoraal)\s+(.+)",
        ]

        # B5: Grade patterns
        grade_patterns = [
            r"(cum laude|summa cum laude|magna cum laude)",
            r"(?:with|met)\s+(honors?|onderscheiding)",
            r"GPA[:\s]*([\d\.]+)",
            r"(?:Grade|Cijfer)[:\s]*([\d\.]+)",
        ]

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Check for date range (likely marks new entry boundary)
            date_match = re.search(r"(\d{4})\s*[-–—]\s*(\d{4})", line_stripped)

            # B5: Also check for "afgestudeerd in" (graduated in) patterns
            graduated_match = re.search(
                r"(?:afgestudeerd|graduated)(?:\s+in)?\s+(\d{4})",
                line_stripped,
                re.IGNORECASE,
            )

            if date_match or graduated_match:
                # Save previous entry if exists
                if current_edu:
                    education_list.append(current_edu)

                # Start new entry
                current_edu = Education()
                if date_match:
                    start_year = int(date_match.group(1))
                    end_year = int(date_match.group(2))
                elif graduated_match:
                    end_year = int(graduated_match.group(1))
                    start_year = end_year - 4  # Assume 4-year program

                from datetime import date as date_class

                current_edu.start_date = date_class(start_year, 9, 1)
                current_edu.end_date = date_class(end_year, 6, 30)
                current_entry = [line_stripped]
                continue

            if current_edu:
                current_entry.append(line_stripped)

                # B5: Extract grades/honors
                if not current_edu.description:
                    for grade_pattern in grade_patterns:
                        grade_match = re.search(
                            grade_pattern, line_stripped, re.IGNORECASE
                        )
                        if grade_match:
                            current_edu.description = grade_match.group(0)
                            break

                # Check for organization (university keyword)
                if not current_edu.organization and any(
                    keyword in line_stripped.lower()
                    for keyword in [
                        "universiteit",
                        "university",
                        "hogeschool",
                        "college",
                        "school",
                        "instituut",
                        "institute",
                    ]
                ):
                    current_edu.organization = line_stripped

                # B5: Enhanced degree/field parsing
                elif not current_edu.title:
                    # Try structured degree patterns first
                    for pattern in degree_patterns:
                        deg_match = re.search(pattern, line_stripped, re.IGNORECASE)
                        if deg_match:
                            if (
                                deg_match.lastindex
                                and deg_match.lastindex >= 2
                                and deg_match.group(2)
                            ):
                                # Has field of study - combine into title
                                current_edu.title = f"{deg_match.group(1)} in {deg_match.group(2).strip()}"
                            else:
                                # Just degree
                                current_edu.title = deg_match.group(1)
                            break

                    # Fallback: check for basic degree keywords
                    if not current_edu.title:
                        degree_keywords = [
                            "bachelor",
                            "master",
                            "phd",
                            "doctorate",
                            "msc",
                            "bsc",
                            "mba",
                            "ma",
                            "ba",
                            "hbo",
                            "wo",
                            "mbo",
                            "doctoraal",
                            "sociologie",
                            "hrm",
                            "informatica",
                            "computer science",
                        ]
                        if (
                            any(kw in line_stripped.lower() for kw in degree_keywords)
                            or line_stripped.isupper()
                        ):
                            current_edu.title = line_stripped

        # Don't forget last entry
        if current_edu:
            education_list.append(current_edu)

        return (
            education_list
            if education_list
            else [Education(description=text.strip()[:1000])]
        )

    def _extract_languages(self, text: str) -> list[Language]:
        """Extract language skills with native/foreign language detection (B7: Enhanced).

        Args:
            text: Language section text

        Returns:
            List of Language objects
        """
        languages = []

        # Common languages
        language_names = [
            "English",
            "Dutch",
            "German",
            "French",
            "Spanish",
            "Italian",
            "Portuguese",
            "Chinese",
            "Japanese",
            "Russian",
            "Arabic",
            "Nederlands",
        ]

        # CEFR levels
        cefr_pattern = r"\b([A-C][1-2])\b"

        # B7: Enhanced proficiency inference keywords
        proficiency_levels = {
            # Native/bilingual
            "native": "C2",
            "moedertaal": "C2",
            "mother tongue": "C2",
            "bilingual": "C2",
            "tweetalig": "C2",
            # Fluent
            "fluent": "C2",
            "vloeiend": "C2",
            "excellent": "C2",
            "uitstekend": "C2",
            # Advanced
            "advanced": "C1",
            "gevorderd": "C1",
            "proficient": "C1",
            # Intermediate
            "intermediate": "B1",
            "good": "B1",
            "goed": "B1",
            "conversational": "B1",
            # Basic
            "basic": "A2",
            "elementary": "A2",
            "beginner": "A1",
            "limited": "A2",
            "beperkt": "A2",
        }

        for lang in language_names:
            if re.search(rf"\b{lang}\b", text, re.IGNORECASE):
                language = Language(language=lang)

                # Find context around the language name (100 chars before and after)
                lang_pos = text.lower().find(lang.lower())
                if lang_pos >= 0:
                    context = text[max(0, lang_pos - 100) : lang_pos + 150]

                    # B7: Check if it's a native language first
                    is_native = False
                    native_keywords = [
                        "native",
                        "moedertaal",
                        "mother tongue",
                        "bilingual",
                        "tweetalig",
                    ]
                    for native_keyword in native_keywords:
                        if re.search(rf"\b{native_keyword}\b", context, re.IGNORECASE):
                            language.is_native = True
                            language.listening = "C2"
                            language.reading = "C2"
                            language.speaking = "C2"
                            language.writing = "C2"
                            is_native = True
                            break

                    if not is_native:
                        # Try to find CEFR level
                        cefr_match = re.search(cefr_pattern, context)
                        if cefr_match:
                            level = cefr_match.group(1)
                            language.listening = level
                            language.reading = level
                            language.speaking = level
                            language.writing = level
                        else:
                            # B7: Enhanced proficiency keyword matching
                            # Look for keywords within 50 chars of language name
                            context_near = text[max(0, lang_pos - 50) : lang_pos + 50]
                            found_level = False

                            for prof_keyword, cefr_level in proficiency_levels.items():
                                if re.search(
                                    rf"\b{prof_keyword}\b", context_near, re.IGNORECASE
                                ):
                                    if prof_keyword in [
                                        "native",
                                        "moedertaal",
                                        "mother tongue",
                                        "bilingual",
                                        "tweetalig",
                                    ]:
                                        language.is_native = True
                                    language.listening = cefr_level
                                    language.reading = cefr_level
                                    language.speaking = cefr_level
                                    language.writing = cefr_level
                                    found_level = True
                                    break

                            # B7: Fallback - if no level found, assign default based on context
                            if not found_level:
                                # If it's listed without level, assume intermediate (B1)
                                language.listening = "B1"
                                language.reading = "B1"
                                language.speaking = "B1"
                                language.writing = "B1"

                languages.append(language)

        return languages

    def _extract_skills(self, text: str) -> list[Skill]:
        """Extract skills with improved categorization.

        Args:
            text: Skills section text

        Returns:
            List of Skill objects
        """
        skills = []
        seen_skills = set()  # Track duplicates

        # Split by common delimiters
        skill_items = re.split(r"[,•\n·|]", text)

        # Also try splitting by multiple spaces (common in CVs)
        if len(skill_items) < 3:
            # Try splitting by double space or newline
            skill_items = re.split(r"\s{2,}|\n", text)

        # Expanded noise words to skip (common resume fluff)
        noise_words = {
            "skills",
            "experience",
            "proficient",
            "knowledge",
            "familiar",
            "and",
            "or",
            "including",
            "such as",
            "etc",
            "years",
            "page",
            "vaardigheden",  # Dutch
            "competenties",  # Dutch
            "expertise",
            "competencies",
            "technical",
            "tools",
            "technologies",
            "software",
            "programming",
            "languages",
            "talen",  # Dutch
            "strong",
            "working",
            "understanding",
        }

        # Section header patterns (more strict detection)
        section_header_pattern = re.compile(
            r"^(vaardigheden|skills|competenties|ervaring|experience|"
            r"opleiding|education|talen|languages|certificaten|certifications?)$",
            re.IGNORECASE,
        )

        for item in skill_items:
            item = item.strip()

            # Basic validation - allow longer for compound skills
            if not item or len(item) < 2 or len(item) > 80:
                continue

            # Skip if it's just numbers or dates
            if re.match(r"^[\d\s\-/]+$", item):
                continue

            # Skip page numbers (A1: Fix "Page X" filtering)
            if re.search(r"^page\s+\d+$", item, re.IGNORECASE):
                continue

            # Skip date ranges (common in job descriptions)
            if re.search(r"\d{4}\s*[-–—]\s*\d{4}", item):
                continue
            if re.search(
                r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}", item
            ):
                continue

            # Skip noise words
            if item.lower() in noise_words:
                continue

            # Skip if it's exactly a section header (strict match)
            if section_header_pattern.match(item):
                continue

            # Skip if it looks like a full sentence (job description)
            if len(item.split()) > 10:
                continue

            # Skip if it looks like a job title or description
            if any(
                phrase in item.lower()
                for phrase in [
                    "responsible for",
                    "working with",
                    "experience with",
                    "knowledge of",
                    "verantwoordelijk voor",  # Dutch
                    "ervaring met",  # Dutch
                ]
            ):
                continue

            # Allow compound skills with slashes, hyphens, parentheses
            # e.g., "CI/CD", "REST APIs", "Python (Django)"
            # But skip if it's mostly numbers
            digit_ratio = sum(c.isdigit() for c in item) / len(item) if item else 0
            if digit_ratio > 0.5:
                continue

            # Normalize for duplicate detection (lowercase, remove spaces/punctuation)
            normalized = re.sub(r"[^\w]", "", item.lower())
            if normalized in seen_skills:
                continue

            seen_skills.add(normalized)
            skill = Skill(name=item)
            skills.append(skill)

        return skills

    def _extract_certifications(self, text: str) -> list[Certification]:
        """Extract certifications with improved pattern matching.

        Args:
            text: Certifications section text

        Returns:
            List of Certification objects
        """
        certifications = []
        lines = text.split("\n")

        # Common certification keywords (expanded)
        cert_keywords = [
            "Certified",
            "Certification",
            "Certificate",
            "Foundation",
            "Professional",
            "AWS",
            "Azure",
            "Microsoft",
            "Google",
            "Oracle",
            "Vertrouwenspersoon",
            "Change",
            "Management",
            "Agile",
            "Scrum",
            "Coach",
            "Consultant",
            "Specialist",
            "Diploma",
            "License",
            "Training",
            "Course",
            "Cursus",  # Dutch
            "Opleiding",  # Dutch (when not in education context)
        ]

        # Common certification format patterns
        cert_patterns = [
            r"\b[A-Z]{2,6}\b",  # Acronyms (ISO, ITIL, PMP, etc.)
            r"\b[A-Z][a-z]+\s+v?\d+",  # Name with version (ITIL v4, Angular 12)
            r"\b[A-Z]{2,}\s*\d{3,5}\b",  # ISO standards (ISO 9001, ISO 27001)
            r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+",  # Multi-word capitalized
        ]

        # Issuer patterns
        issuer_patterns = [
            r"(?:from|by|via|issued by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"\(([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\)$",  # (Organization) at end
        ]

        for line in lines:
            line = line.strip()

            # Skip empty lines, very short lines
            if not line or len(line) < 5:
                continue

            # Skip page numbers and section headers
            if re.search(
                r"^page\s+\d+|^certifications?$|^licenses?$|^certificaten$",
                line,
                re.IGNORECASE,
            ):
                continue

            # Check if line looks like a certification
            is_cert = False

            # Check for keywords
            if any(keyword.lower() in line.lower() for keyword in cert_keywords):
                is_cert = True

            # Check for certification patterns
            elif any(re.search(pattern, line) for pattern in cert_patterns):
                is_cert = True

            # Check for capitalized lines (but not all caps or just one word)
            elif (
                len(line.split()) >= 2
                and line[0].isupper()
                and not line.isupper()
                and len(line) > 10
            ):
                is_cert = True

            # Check for credential IDs/numbers
            elif re.search(r"#\d+|ID:\s*\w+|Credential:\s*\w+", line, re.IGNORECASE):
                is_cert = True

            if is_cert:
                cert = Certification(name=line)

                # Try to extract date from the line (support older years)
                year_match = re.search(r"\b(19|20)\d{2}\b", line)
                if year_match:
                    year = int(year_match.group())
                    from datetime import date as date_class

                    cert.date = date_class(year, 1, 1)

                # Try to extract validity period
                validity_match = re.search(
                    r"valid\s+(?:until|through|to)\s+(19|20)\d{2}", line, re.IGNORECASE
                )
                if validity_match:
                    # Could store validity in description or notes
                    pass

                # Try to extract issuer
                for issuer_pattern in issuer_patterns:
                    issuer_match = re.search(issuer_pattern, line, re.IGNORECASE)
                    if issuer_match:
                        # Could store issuer information in description
                        break

                certifications.append(cert)

        return certifications
