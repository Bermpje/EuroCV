"""Map Resume to Europass format."""

import base64
import re
from datetime import datetime
from typing import Any, Optional

from eurocv.core.models import EuropassCV, Resume


class EuropassMapper:
    """Map intermediate Resume model to Europass format."""

    def __init__(self, locale: str = "en-US", include_photo: bool = True):
        """Initialize mapper.

        Args:
            locale: Locale for date/number formatting (e.g., 'nl-NL', 'en-US')
            include_photo: Whether to include photo in output (GDPR consideration)
        """
        self.locale = locale
        self.include_photo = include_photo

    def map(self, resume: Resume) -> EuropassCV:
        """Map Resume to Europass format.

        Args:
            resume: Resume object

        Returns:
            EuropassCV object
        """
        europass = EuropassCV()

        # Document info
        europass.DocumentInfo = {
            "DocumentType": "Europass CV",
            "CreationDate": datetime.utcnow().isoformat(),
            "Generator": "EuroCV",
            "XSDVersion": "V3.3",
        }

        # Learner info
        learner_info: dict[str, Any] = {}

        # Identification
        identification = self._map_identification(resume)
        if identification:
            learner_info["Identification"] = identification

        # Headline (summary)
        if resume.summary:
            learner_info["Headline"] = {
                "Type": {"Code": "preferred", "Label": "Headline"},
                "Description": {"Label": resume.summary[:500]},
            }

        # Work experience
        if resume.work_experience:
            learner_info["WorkExperience"] = [
                self._map_work_experience(exp) for exp in resume.work_experience
            ]

        # Education
        if resume.education:
            learner_info["Education"] = [
                self._map_education(edu) for edu in resume.education
            ]

        # Skills (includes languages via _map_skills)
        skills = self._map_skills(resume)
        if skills:
            learner_info["Skills"] = skills

        # Certifications (map to Achievement)
        if resume.certifications:
            learner_info["Achievement"] = [
                self._map_certification(cert) for cert in resume.certifications
            ]

        europass.LearnerInfo = learner_info

        return europass

    def _map_identification(self, resume: Resume) -> Optional[dict[str, Any]]:
        """Map personal information to Europass Identification.

        Args:
            resume: Resume object

        Returns:
            Identification dict or None
        """
        pi = resume.personal_info

        identification: dict[str, Any] = {}

        # PersonName
        if pi.first_name or pi.last_name:
            person_name = {}
            if pi.first_name:
                person_name["FirstName"] = pi.first_name
            if pi.last_name:
                person_name["Surname"] = pi.last_name
            identification["PersonName"] = person_name

        # ContactInfo
        contact_info: dict[str, Any] = {}

        # Address
        if any([pi.address, pi.city, pi.postal_code, pi.country]):
            address: dict[str, Any] = {"Contact": {}}
            address_line = []
            if pi.address:
                address_line.append(pi.address)
            if pi.city:
                address["Contact"]["Municipality"] = pi.city
            if pi.postal_code:
                address["Contact"]["PostalCode"] = pi.postal_code
            if pi.country:
                address["Contact"]["Country"] = {
                    "Code": pi.country,
                    "Label": pi.country,
                }
            if address_line:
                address["Contact"]["AddressLine"] = " ".join(address_line)
            contact_info["Address"] = address

        # Email
        if pi.email:
            contact_info["Email"] = {"Contact": str(pi.email)}

        # Telephone
        if pi.phone:
            contact_info["Telephone"] = [{"Contact": pi.phone}]

        if contact_info:
            identification["ContactInfo"] = contact_info

        # Demographics
        demographics = {}
        if pi.date_of_birth:
            # Clean integer format for JSON
            birthdate: dict[str, Any] = {"Year": pi.date_of_birth.year}
            if pi.date_of_birth.month:
                birthdate["Month"] = pi.date_of_birth.month
            if pi.date_of_birth.day and pi.date_of_birth.day != 1:
                birthdate["Day"] = pi.date_of_birth.day
            demographics["Birthdate"] = birthdate

        if pi.nationality:
            demographics["Nationality"] = [
                {"Code": pi.nationality, "Label": pi.nationality}
            ]  # type: ignore[assignment]

        if demographics:
            identification["Demographics"] = demographics

        # Photo
        if self.include_photo and pi.photo:
            try:
                photo_b64 = base64.b64encode(pi.photo).decode("utf-8")
                identification["Photo"] = {"MimeType": "image/jpeg", "Data": photo_b64}
            except Exception:
                pass

        return identification if identification else None

    def _map_work_experience(self, exp: Any) -> dict[str, Any]:
        """Map work experience to Europass format.

        Args:
            exp: WorkExperience object

        Returns:
            Europass work experience dict
        """
        work_exp: dict[str, Any] = {}

        # Period (using clean integer format for JSON)
        period: dict[str, Any] = {}
        if exp.start_date:
            from_date: dict[str, Any] = {"Year": exp.start_date.year}
            # Only include month if we have meaningful month data (not just default day 1)
            if exp.start_date.month:
                from_date["Month"] = exp.start_date.month
            # Only include day if it's meaningful (not just default day 1 from month-only data)
            if exp.start_date.day and exp.start_date.day != 1:
                from_date["Day"] = exp.start_date.day
            period["From"] = from_date

        if exp.end_date:
            to_date: dict[str, Any] = {"Year": exp.end_date.year}
            if exp.end_date.month:
                to_date["Month"] = exp.end_date.month
            if exp.end_date.day and exp.end_date.day != 1:
                to_date["Day"] = exp.end_date.day
            period["To"] = to_date
        elif exp.current:
            period["Current"] = True

        if period:
            work_exp["Period"] = period

        # Position (with ISCO code if available)
        if exp.position:
            position = {"Label": exp.position}
            # Add ISCO-08 code if it can be inferred (default to software developer)
            if any(
                keyword in exp.position.lower()
                for keyword in ["developer", "programmer", "software", "engineer"]
            ):
                position["Code"] = "2512"  # Software developers
            work_exp["Position"] = position

        # Activities and responsibilities
        if exp.description:
            work_exp["Activities"] = exp.description
        elif exp.activities:
            work_exp["Activities"] = "\n".join(exp.activities)

        # Employer
        employer = {}
        if exp.employer:
            employer["Name"] = exp.employer

        if exp.city or exp.country:
            employer["ContactInfo"] = {"Address": {"Contact": {}}}
            if exp.city:
                employer["ContactInfo"]["Address"]["Contact"]["Municipality"] = exp.city
            if exp.country:
                # Use ISO country code if possible
                country_code = self._get_country_code(exp.country)
                employer["ContactInfo"]["Address"]["Contact"]["Country"] = {
                    "Code": country_code,
                    "Label": exp.country,
                }

        if employer:
            work_exp["Employer"] = employer

        return work_exp

    def _map_education(self, edu: Any) -> dict[str, Any]:
        """Map education to Europass format.

        Args:
            edu: Education object

        Returns:
            Europass education dict
        """
        education: dict[str, Any] = {}

        # Period (using clean integer format for JSON)
        period: dict[str, Any] = {}
        if edu.start_date:
            from_date: dict[str, Any] = {"Year": edu.start_date.year}
            if edu.start_date.month:
                from_date["Month"] = edu.start_date.month
            if edu.start_date.day and edu.start_date.day != 1:
                from_date["Day"] = edu.start_date.day
            period["From"] = from_date

        if edu.end_date:
            to_date: dict[str, Any] = {"Year": edu.end_date.year}
            if edu.end_date.month:
                to_date["Month"] = edu.end_date.month
            if edu.end_date.day and edu.end_date.day != 1:
                to_date["Day"] = edu.end_date.day
            period["To"] = to_date
        elif edu.current:
            period["Current"] = True

        if period:
            education["Period"] = period

        # Title
        if edu.title:
            education["Title"] = edu.title
        elif edu.description:
            # Use first line of description as title
            first_line = edu.description.split("\n")[0][:100]
            education["Title"] = first_line

        # Skills acquired (description)
        if edu.description:
            education["Skills"] = edu.description

        # Organization
        organization = {}
        if edu.organization:
            organization["Name"] = edu.organization

        if edu.city or edu.country:
            organization["ContactInfo"] = {"Address": {"Contact": {}}}
            if edu.city:
                organization["ContactInfo"]["Address"]["Contact"]["Municipality"] = (
                    edu.city
                )
            if edu.country:
                country_code = self._get_country_code(edu.country)
                organization["ContactInfo"]["Address"]["Contact"]["Country"] = {
                    "Code": country_code,
                    "Label": edu.country,
                }

        if organization:
            education["Organisation"] = organization

        # Level (ISCED 2011)
        if edu.level:
            education["Level"] = {
                "Code": edu.level,
                "Label": self._get_isced_label(edu.level),
            }
        else:
            # Try to infer level from title
            level = self._infer_education_level(edu.title or "")
            if level:
                education["Level"] = level

        return education

    def _map_certification(self, cert: Any) -> dict[str, Any]:
        """Map certification to Europass Achievement format.

        Args:
            cert: Certification object

        Returns:
            Europass achievement dict
        """
        achievement: dict[str, Any] = {}

        # Title
        if cert.name:
            achievement["Title"] = {"Label": cert.name}

        # Date (if available)
        if cert.date:
            achievement["Date"] = {"Year": cert.date.year}
            if cert.date.month:
                achievement["Date"]["Month"] = cert.date.month
            if cert.date.day and cert.date.day != 1:
                achievement["Date"]["Day"] = cert.date.day

        # Issuer (if available)
        if hasattr(cert, "issuer") and cert.issuer:
            achievement["IssuedBy"] = cert.issuer

        return achievement

    def _map_skills(self, resume: Resume) -> Optional[dict[str, Any]]:
        """Map skills to Europass format.

        Args:
            resume: Resume object

        Returns:
            Skills dict or None
        """
        skills: dict[str, Any] = {}

        # Communication/linguistic skills (languages)
        if resume.languages:
            linguistic: dict[str, Any] = {"MotherTongue": [], "ForeignLanguage": []}

            for lang in resume.languages:
                if lang.is_native:
                    linguistic["MotherTongue"].append(
                        {"Description": {"Label": lang.language}}
                    )
                else:
                    foreign_lang: dict[str, Any] = {
                        "Description": {"Label": lang.language}
                    }

                    # CEFR levels
                    if any([lang.listening, lang.reading, lang.speaking, lang.writing]):
                        proficiency = {}
                        if lang.listening:
                            proficiency["Listening"] = lang.listening
                        if lang.reading:
                            proficiency["Reading"] = lang.reading
                        if lang.speaking:
                            proficiency["SpokenInteraction"] = lang.speaking
                            proficiency["SpokenProduction"] = lang.speaking
                        if lang.writing:
                            proficiency["Writing"] = lang.writing

                        foreign_lang["ProficiencyLevel"] = proficiency

                    linguistic["ForeignLanguage"].append(foreign_lang)

            skills["Linguistic"] = linguistic

        # Other skills
        if resume.skills:
            # Categorize skills
            computer_keywords = [
                "python",
                "java",
                "javascript",
                "sql",
                "html",
                "css",
                "git",
                "docker",
                "kubernetes",
                "aws",
                "azure",
                "linux",
                "windows",
            ]

            computer_skills = []
            other_skills = []

            for skill in resume.skills:
                skill_lower = skill.name.lower()
                if any(kw in skill_lower for kw in computer_keywords):
                    computer_skills.append(skill.name)
                else:
                    other_skills.append(skill.name)

            if computer_skills:
                skills["Computer"] = {"Description": ", ".join(computer_skills)}

            if other_skills:
                skills["Other"] = {"Description": ", ".join(other_skills)}

        return skills if skills else None

    def _get_country_code(self, country_name: str) -> str:
        """Get ISO 3166-1 alpha-2 country code.

        Args:
            country_name: Country name

        Returns:
            ISO country code
        """
        # Common country mappings
        country_map = {
            "netherlands": "NL",
            "germany": "DE",
            "belgium": "BE",
            "france": "FR",
            "united kingdom": "GB",
            "uk": "GB",
            "united states": "US",
            "usa": "US",
            "spain": "ES",
            "italy": "IT",
            "portugal": "PT",
            "poland": "PL",
            "sweden": "SE",
            "denmark": "DK",
            "norway": "NO",
            "finland": "FI",
            "austria": "AT",
            "switzerland": "CH",
            "ireland": "IE",
            "greece": "GR",
            "czech republic": "CZ",
            "hungary": "HU",
            "romania": "RO",
            "bulgaria": "BG",
        }

        country_lower = country_name.lower().strip()
        return country_map.get(country_lower, country_name[:2].upper())

    def _get_isced_label(self, code: str) -> str:
        """Get ISCED 2011 level label.

        Args:
            code: ISCED level code

        Returns:
            Level label
        """
        isced_labels = {
            "0": "Early childhood education",
            "1": "Primary education",
            "2": "Lower secondary education",
            "3": "Upper secondary education",
            "4": "Post-secondary non-tertiary education",
            "5": "Short-cycle tertiary education",
            "6": "Bachelor or equivalent",
            "7": "Master or equivalent",
            "8": "Doctoral or equivalent",
        }
        return isced_labels.get(code, f"Level {code}")

    def _infer_education_level(self, title: str) -> Optional[dict[str, str]]:
        """Infer ISCED level from education title.

        Args:
            title: Education title

        Returns:
            Dict with Code and Label, or None
        """
        if not title:
            return None

        title_lower = title.lower()

        # Doctoral (ISCED 8)
        if any(
            word in title_lower
            for word in ["phd", "ph.d", "doctorate", "doctoral", "doctor"]
        ):
            return {"Code": "8", "Label": "Doctoral or equivalent"}

        # Master (ISCED 7) - check BEFORE bachelor to avoid false matches
        # Use word boundaries to avoid matching 'ma' in 'informatica'
        master_patterns = [
            r"\bmaster\b",
            r"\bmaster's\b",
            r"\bmsc\b",
            r"\bm\.?sc\b",
            r"\bma\b",
            r"\bm\.?a\b",
            r"\bmba\b",
        ]
        if any(re.search(pattern, title_lower) for pattern in master_patterns):
            return {"Code": "7", "Label": "Master or equivalent"}

        # Premaster is still master level
        if "premaster" in title_lower:
            return {"Code": "7", "Label": "Master or equivalent"}

        # Bachelor (ISCED 6) - now more specific
        # Use word boundaries to avoid matching 'ba' in random words
        bachelor_patterns = [
            r"\bbachelor\b",
            r"\bbachelor's\b",
            r"\bbsc\b",
            r"\bb\.?sc\b",
            r"\bba\b",
            r"\bb\.?a\b",
            r"\bbs\b",
            r"\bb\.?s\b",
            r"\bbict\b",
            r"\bb\.?ict\b",
        ]
        if any(re.search(pattern, title_lower) for pattern in bachelor_patterns):
            # Make sure it's not "bachelor of" in a master's context
            if not re.search(r"\bmaster\b", title_lower):
                return {"Code": "6", "Label": "Bachelor or equivalent"}

        # Short-cycle tertiary (ISCED 5) - HBO, Associate
        if any(word in title_lower for word in ["hbo", "associate", "hogeschool"]):
            # But if it says Bachelor, it's level 6
            if "bachelor" in title_lower:
                return {"Code": "6", "Label": "Bachelor or equivalent"}
            return {"Code": "5", "Label": "Short-cycle tertiary education"}

        # Upper secondary (ISCED 3)
        if any(
            word in title_lower
            for word in [
                "high school",
                "secondary",
                "diploma",
                "havo",
                "vwo",
                "gymnasium",
            ]
        ):
            return {"Code": "3", "Label": "Upper secondary education"}

        # Vocational secondary (ISCED 3/4)
        if any(
            word in title_lower for word in ["mbo", "vocational", "technical college"]
        ):
            return {"Code": "3", "Label": "Upper secondary education"}

        return None
