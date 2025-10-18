"""DOCX extraction functionality with multi-language support."""

import re
from datetime import date
from pathlib import Path
from typing import Any

from docx import Document

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


class DOCXExtractor(ResumeExtractor):
    """Extract text and structure from DOCX files with multi-language support.

    Reuses extraction logic from GenericPDFExtractor for consistency.
    """

    # Multi-language section headers (same as GenericPDFExtractor)
    SECTION_HEADERS = {
        "work_experience": [
            "work experience",
            "professional experience",
            "employment history",
            "experience",
            "werkervaring",  # Dutch
            "work history",
            "career",
        ],
        "education": [
            "education",
            "academic background",
            "opleidingen",  # Dutch
            "academic",
            "qualifications",
            "degrees",
        ],
        "skills": [
            "skills",
            "technical skills",
            "vaardigheden",  # Dutch
            "software kennis",  # Dutch: software knowledge
            "competencies",
            "expertise",
        ],
        "languages": [
            "languages",
            "language skills",
            "talen",  # Dutch
        ],
        "certifications": [
            "certifications",
            "certificates",
            "training",
            "professional development",
            "training en certificering",  # Dutch
            "certificaten",  # Dutch
        ],
        "summary": ["summary", "profile", "about", "samenvatting", "profiel"],
    }

    # Dutch month names
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
        "september": "09",
        "okt": "10",
        "oktober": "10",
        "nov": "11",
        "november": "11",
        "dec": "12",
        "december": "12",
    }

    # Present keywords (multiple languages)
    PRESENT_KEYWORDS = [
        "present",
        "current",
        "heden",
        "nu",
        "now",
        "today",
        "ongoing",
        "tot heden",
        "tot nu",
        "vanaf",
        "sinds",
    ]

    @property
    def name(self) -> str:
        """Return extractor name."""
        return "DOCX"

    def can_handle(self, file_path: str) -> bool:
        """Check if this extractor can handle the file.

        Args:
            file_path: Path to the file

        Returns:
            True if file is a DOCX file
        """
        return file_path.lower().endswith((".docx", ".doc"))

    def extract(self, file_path: str) -> Resume:
        """Extract resume data from DOCX.

        Args:
            file_path: Path to DOCX file

        Returns:
            Resume object with extracted data
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"DOCX file not found: {file_path}")

        doc = Document(str(path))

        # Extract all text
        full_text = "\n".join([para.text for para in doc.paragraphs])

        # Extract metadata
        metadata = self._extract_metadata(doc)

        # Parse the text into structured data
        resume = self._parse_text_to_resume(full_text, metadata)
        resume.raw_text = full_text
        resume.metadata.update(metadata)

        return resume

    def _extract_metadata(self, doc: Document) -> dict[str, Any]:
        """Extract document metadata.

        Args:
            doc: python-docx Document object

        Returns:
            Metadata dictionary
        """
        metadata = {
            "format": "DOCX",
            "extractor": "python-docx",
        }

        try:
            core_props = doc.core_properties
            metadata.update(
                {
                    "title": core_props.title,
                    "author": core_props.author,
                    "subject": core_props.subject,
                    "keywords": core_props.keywords,
                    "created": core_props.created,
                    "modified": core_props.modified,
                }
            )
        except Exception:
            pass

        return metadata

    def _parse_text_to_resume(self, text: str, metadata: dict[str, Any]) -> Resume:
        """Parse extracted text into structured Resume with multi-language support.

        Args:
            text: Extracted text
            metadata: Document metadata

        Returns:
            Resume object
        """
        resume = Resume()

        # Extract personal info
        resume.personal_info = self._extract_personal_info(text)

        # Override with metadata author ONLY if we didn't extract a name from text
        if metadata.get("author") and not resume.personal_info.first_name:
            author_parts = metadata["author"].split()
            if len(author_parts) >= 2:
                resume.personal_info.first_name = author_parts[0]
                resume.personal_info.last_name = " ".join(author_parts[1:])

        # Extract sections (now with Dutch support)
        sections = self._split_into_sections(text)

        # Extract work experience
        if "work_experience" in sections:
            resume.work_experience = self._extract_work_experience(
                sections["work_experience"]
            )

        # Extract education
        if "education" in sections:
            resume.education = self._extract_education(sections["education"])

        # Extract certifications
        if "certifications" in sections:
            resume.certifications = self._extract_certifications(
                sections["certifications"]
            )

        # Extract languages
        if "languages" in sections:
            resume.languages = self._extract_languages(sections["languages"])

        # Extract skills
        if "skills" in sections:
            resume.skills = self._extract_skills(sections["skills"])

        # Extract summary
        if "summary" in sections:
            resume.summary = sections["summary"]

        return resume

    def _extract_personal_info(self, text: str) -> PersonalInfo:
        """Extract personal information from text with enhanced patterns.

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

        # Extract phone - enhanced patterns (same as GenericPDFExtractor)
        phone_patterns = [
            r"\+\d{1,3}\s*\(0\)\s*\d{1,3}\s*\d{6,8}",  # +31 (0)6 12345678
            r"\+\d{1,3}\s+\d{1,2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}",  # +31 6 53 75 43 72
            r"\+\d{1,3}[-\s]?\d{1,3}[-\s]?\d{6,8}",  # +31-6-12345678
            r"0\d{1}[-\s]?\d{8}",  # 06-12345678
            r"\(?\d{2,4}\)?[-\s]?\d{6,7}",  # (020) 1234567
            r"\+?1?\s*\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}",  # US
            r"\+44\s*\d{2,4}\s*\d{4}\s*\d{4}",  # UK
            r"[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}",
        ]

        phone_matches = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text[:2000])
            phone_matches.extend(matches)

        if phone_matches:
            # Filter out years and validate
            valid_phones = []
            for p in phone_matches:
                clean_phone = (
                    p.replace(" ", "")
                    .replace("-", "")
                    .replace(".", "")
                    .replace("(", "")
                    .replace(")", "")
                )
                if re.match(r"^\d{4}$", clean_phone):
                    continue
                if 6 <= len(re.sub(r"\D", "", clean_phone)) <= 15:
                    valid_phones.append(p)

            if valid_phones:
                info.phone = valid_phones[0]

        # Extract name - look for "Naam:" pattern or first line
        name_patterns = [
            # Dutch/English "Name:" pattern - stop at newline to avoid capturing next field
            r"(?i)(?:naam|name)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+?)(?=\s*\n|\s*$)",
            # Title + Name pattern (drs. ing. Emiel Kremers)
            r"(?:drs\.|ir\.|ing\.|dr\.|prof\.)\s+(?:drs\.|ir\.|ing\.|dr\.|prof\.\s+)?([A-Z][a-z]+\s+[A-Z][a-z]+)(?=\s*\n|\s*$)",
            # CV header with name (Curriculum Vitae Name)
            r"(?i)curriculum\s+vitae\s+(?:drs\.|ir\.|ing\.|dr\.|prof\.\s+)?([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?=\s*\n|\s*$)",
            # Standalone capitalized name
            r"^([A-Z][a-z]+\s+[A-Z][a-z]+)$",
        ]

        for pattern in name_patterns:
            name_match = re.search(pattern, text[:800], re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip()
                parts = name.split()
                if len(parts) >= 2:
                    info.first_name = parts[0]
                    info.last_name = " ".join(parts[1:])
                    break

        # If still no name, try first non-empty line
        if not info.first_name:
            lines = text.split("\n")
            for line in lines[:10]:
                line = line.strip()
                # Skip "Curriculum Vitae" and similar
                if (
                    line
                    and "curriculum" not in line.lower()
                    and "vitae" not in line.lower()
                ):
                    if len(line.split()) >= 2 and len(line) < 50:
                        if not any(char.isdigit() for char in line) and "@" not in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                info.first_name = parts[0]
                                info.last_name = " ".join(parts[1:])
                                break

        # Extract location - look for city/country
        location_patterns = [
            # Dutch address format: postal code + city (country)
            r"\d{4}\s*[A-Z]{2}\s+([A-Z][a-z]+)\s*\(([^)]+)\)",  # 4702 GK Roosendaal (Nederland)
            # Address line with city (country)
            r"(?i)(?:adres|address)[\s:]+.*?([A-Z][a-z]+)\s+\(([A-Z][a-z]+)\)",
            # Simple city, country
            r"([A-Z][a-z]+),\s*([A-Z][a-z]+)",
        ]

        for pattern in location_patterns:
            loc_match = re.search(pattern, text[:1500])
            if loc_match:
                info.city = loc_match.group(1)
                country = loc_match.group(2)
                # Translate common Dutch country names
                country_map = {
                    "nederland": "Netherlands",
                    "netherlands": "Netherlands",
                    "duitsland": "Germany",
                    "belgië": "Belgium",
                    "frankrijk": "France",
                }
                info.country = country_map.get(country.lower(), country)
                break

        return info

    def _split_into_sections(self, text: str) -> dict[str, str]:
        """Split resume text into sections using multi-language headers.

        Args:
            text: Resume text

        Returns:
            Dict mapping section names to content
        """
        sections = {}

        # Build patterns for each section type
        section_positions = []
        for section_key, headers in self.SECTION_HEADERS.items():
            # Create regex pattern for all headers of this section
            pattern = r"(?i)\b(" + "|".join(re.escape(h) for h in headers) + r")[\s:]*"
            matches = list(re.finditer(pattern, text))
            for match in matches:
                section_positions.append((match.start(), section_key, match.group()))

        # Sort by position in text
        section_positions.sort()

        # Extract content between headers
        for i, (start, key, header) in enumerate(section_positions):
            if i + 1 < len(section_positions):
                end = section_positions[i + 1][0]
            else:
                end = len(text)

            content = text[start:end].strip()
            # Remove the header itself
            content = re.sub(
                f"^{re.escape(header)}", "", content, flags=re.IGNORECASE
            ).strip()
            # Remove any colons after the header
            content = re.sub(r"^:\s*", "", content).strip()
            sections[key] = content

        return sections

    def _extract_work_experience(self, text: str) -> list[WorkExperience]:
        """Extract work experience entries."""
        experiences = []

        if text.strip():
            exp = WorkExperience(description=text.strip()[:1000])
            experiences.append(exp)

        return experiences

    def _extract_education(self, text: str) -> list[Education]:
        """Extract education entries with multi-year range support.

        Args:
            text: Education section text

        Returns:
            List of Education objects
        """
        education_list = []
        lines = text.split("\n")

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped or len(line_stripped) < 10:
                continue

            # Look for year ranges: 2013 – 2015
            date_match = re.search(r"(\d{4})\s*[–—-]\s*(\d{4})", line_stripped)

            if date_match:
                edu = Education()
                start_year = int(date_match.group(1))
                end_year = int(date_match.group(2))

                edu.start_date = date(start_year, 9, 1)
                edu.end_date = date(end_year, 6, 30)

                # Rest of line is title/organization
                remaining = line_stripped[date_match.end() :].strip()
                # Remove leading tab/space chars
                remaining = re.sub(r"^\s+", "", remaining)

                if remaining:
                    # Try to split by comma or "at"
                    if "," in remaining:
                        parts = remaining.split(",", 1)
                        edu.title = parts[0].strip()
                        if len(parts) > 1:
                            edu.organization = parts[1].strip()
                    else:
                        edu.title = remaining

                education_list.append(edu)

        return education_list if education_list else []

    def _extract_certifications(self, text: str) -> list[Certification]:
        """Extract certification entries.

        Args:
            text: Certifications section text

        Returns:
            List of Certification objects
        """
        certifications = []
        lines = text.split("\n")

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped or len(line_stripped) < 5:
                continue

            # Skip section headers and noise
            if line_stripped.lower() in [
                "training",
                "certificering",
                "certifications",
                "certificates",
            ] or re.match(r"^en\s+certificering:?$", line_stripped, re.IGNORECASE):
                continue

            # Extract year at the start: 2020\tCertification Name
            year_match = re.match(r"^(\d{4})\s+(.+)$", line_stripped)
            if year_match:
                year = int(year_match.group(1))
                cert_name = year_match.group(2).strip()
                if cert_name:  # Only create if we have a name
                    # Create certification with optional date
                    try:
                        cert = Certification(name=cert_name, date=date(year, 1, 1))
                    except Exception:
                        # Fallback without date if validation fails
                        cert = Certification(name=cert_name)
                    certifications.append(cert)
            else:
                # No year found, just use the line as name
                if line_stripped:
                    cert = Certification(name=line_stripped)
                    certifications.append(cert)

        return certifications

    def _extract_languages(self, text: str) -> list[Language]:
        """Extract language skills with proficiency inference.

        Args:
            text: Languages section text

        Returns:
            List of Language objects
        """
        languages = []

        language_names = [
            "English",
            "Engels",  # Dutch for English
            "Dutch",
            "Nederlands",
            "German",
            "Duits",  # Dutch
            "French",
            "Frans",  # Dutch
            "Spanish",
            "Spaans",  # Dutch
            "Italian",
            "Italiaans",  # Dutch
            "Portuguese",
            "Chinese",
            "Japanese",
            "Russian",
            "Arabic",
        ]

        # CEFR levels
        cefr_pattern = r"\b([A-C][1-2])\b"

        # Language name normalization (Dutch to English)
        language_normalize = {
            "engels": "English",
            "nederlands": "Dutch",
            "duits": "German",
            "frans": "French",
            "spaans": "Spanish",
            "italiaans": "Italian",
        }

        # Proficiency keywords
        proficiency_map = {
            "native": "C2",
            "moedertaal": "C2",
            "mother tongue": "C2",
            "bilingual": "C2",
            "fluent": "C2",
            "vloeiend": "C2",
            "zeer goed": "C1",  # very good
            "goed": "B2",  # good
            "redelijk": "B1",  # reasonable
            "basic": "A2",
            "elementary": "A1",
        }

        for lang in language_names:
            if re.search(rf"\b{lang}\b", text, re.IGNORECASE):
                # Normalize language name to English
                lang_normalized = language_normalize.get(lang.lower(), lang)
                language = Language(language=lang_normalized)

                # Find context around language name
                lang_pos = text.lower().find(lang.lower())
                if lang_pos >= 0:
                    context = text[max(0, lang_pos - 50) : lang_pos + 150]

                    # Check for native language
                    is_native = False
                    for keyword in ["native", "moedertaal", "mother tongue"]:
                        if keyword in context.lower():
                            language.is_native = True
                            language.listening = "C2"
                            language.reading = "C2"
                            language.speaking = "C2"
                            language.writing = "C2"
                            is_native = True
                            break

                    if not is_native:
                        # Try CEFR level
                        cefr_match = re.search(cefr_pattern, context)
                        if cefr_match:
                            level = cefr_match.group(1)
                            language.listening = level
                            language.reading = level
                            language.speaking = level
                            language.writing = level
                        else:
                            # Try proficiency keywords
                            for keyword, level in proficiency_map.items():
                                if keyword in context.lower():
                                    if keyword in [
                                        "native",
                                        "moedertaal",
                                        "mother tongue",
                                    ]:
                                        language.is_native = True
                                    language.listening = level
                                    language.reading = level
                                    language.speaking = level
                                    language.writing = level
                                    break

                languages.append(language)

        return languages

    def _extract_skills(self, text: str) -> list[Skill]:
        """Extract skills with filtering.

        Args:
            text: Skills section text

        Returns:
            List of Skill objects
        """
        skills = []
        seen_skills = set()

        # Split by common delimiters
        skill_items = re.split(r"[,•\n·|]", text)

        # Noise words to skip
        noise_words = {
            "skills",
            "expertise",
            "software",
            "kennis",  # Dutch: knowledge
            "vaardigheden",  # Dutch: skills
            "and",
            "or",
            "including",
            "etc",
        }

        for item in skill_items:
            item = item.strip()
            if not item or len(item) < 2 or len(item) > 80:
                continue

            # Skip if just numbers
            if re.match(r"^[\d\s\-/]+$", item):
                continue

            # Skip noise words
            if item.lower() in noise_words:
                continue

            # Skip page numbers
            if re.search(r"^page\s+\d+$", item, re.IGNORECASE):
                continue

            # Normalize for duplicate detection
            normalized = re.sub(r"[^\w]", "", item.lower())
            if normalized in seen_skills:
                continue

            seen_skills.add(normalized)
            skill = Skill(name=item)
            skills.append(skill)

        return skills
