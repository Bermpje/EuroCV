"""DOCX extraction functionality."""

import re
from pathlib import Path
from typing import Any

from docx import Document

from eurocv.core.models import (
    Education,
    Language,
    PersonalInfo,
    Resume,
    Skill,
    WorkExperience,
)


class DOCXExtractor:
    """Extract text and structure from DOCX files."""

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
        """Parse extracted text into structured Resume.

        This uses similar heuristics as the PDF extractor.

        Args:
            text: Extracted text
            metadata: Document metadata

        Returns:
            Resume object
        """
        resume = Resume()

        # Extract personal info
        resume.personal_info = self._extract_personal_info(text)

        # If author is in metadata, try to use it
        if metadata.get("author"):
            author_parts = metadata["author"].split()
            if len(author_parts) >= 2:
                resume.personal_info.first_name = author_parts[0]
                resume.personal_info.last_name = " ".join(author_parts[1:])

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
        """Extract personal information from text."""
        info = PersonalInfo()

        # Extract email
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        email_matches = re.findall(email_pattern, text)
        if email_matches:
            info.email = email_matches[0]

        # Extract phone
        phone_pattern = (
            r"[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}"
        )
        phone_matches = re.findall(phone_pattern, text[:500])
        if phone_matches:
            info.phone = phone_matches[0]

        # Extract name (first line or lines before contact info)
        lines = text.split("\n")
        for line in lines[:10]:
            line = line.strip()
            if line and len(line.split()) >= 2 and len(line) < 50:
                if not any(char.isdigit() for char in line) and "@" not in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        info.first_name = parts[0]
                        info.last_name = " ".join(parts[1:])
                        break

        return info

    def _split_into_sections(self, text: str) -> dict[str, str]:
        """Split resume text into sections."""
        sections = {}

        section_patterns = {
            "summary": r"(?i)(professional\s+summary|profile|summary|objective)",
            "experience": r"(?i)(work\s+experience|professional\s+experience|employment|experience)",
            "education": r"(?i)(education|academic|qualifications)",
            "skill": r"(?i)(skills|competencies|expertise)",
            "language": r"(?i)(languages|language\s+skills)",
        }

        section_positions = []
        for section_key, pattern in section_patterns.items():
            matches = list(re.finditer(pattern, text))
            for match in matches:
                section_positions.append((match.start(), section_key, match.group()))

        section_positions.sort()

        for i, (start, key, header) in enumerate(section_positions):
            if i + 1 < len(section_positions):
                end = section_positions[i + 1][0]
            else:
                end = len(text)

            content = text[start:end].strip()
            content = re.sub(f"^{re.escape(header)}", "", content, flags=re.IGNORECASE).strip()
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
        """Extract education entries."""
        education_list = []

        if text.strip():
            edu = Education(description=text.strip()[:1000])
            education_list.append(edu)

        return education_list

    def _extract_languages(self, text: str) -> list[Language]:
        """Extract language skills."""
        languages = []

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
        ]

        cefr_pattern = r"\b([A-C][1-2])\b"

        for lang in language_names:
            if re.search(rf"\b{lang}\b", text, re.IGNORECASE):
                language = Language(language=lang)

                context = text[
                    max(0, text.lower().find(lang.lower()) - 50) : text.lower().find(lang.lower())
                    + 100
                ]
                cefr_match = re.search(cefr_pattern, context)
                if cefr_match:
                    level = cefr_match.group(1)
                    language.listening = level
                    language.reading = level
                    language.speaking = level
                    language.writing = level

                languages.append(language)

        return languages

    def _extract_skills(self, text: str) -> list[Skill]:
        """Extract skills."""
        skills = []

        skill_items = re.split(r"[,•\n]", text)

        for item in skill_items:
            item = item.strip()
            if item and len(item) > 2 and len(item) < 100:
                skill = Skill(name=item)
                skills.append(skill)

        return skills
