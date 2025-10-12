"""Map Resume to Europass format."""

from datetime import datetime
from typing import Dict, Any, Optional
import base64

from eurocv.core.models import Resume, EuropassCV


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
            "XSDVersion": "V3.3"
        }
        
        # Learner info
        learner_info: Dict[str, Any] = {}
        
        # Identification
        identification = self._map_identification(resume)
        if identification:
            learner_info["Identification"] = identification
        
        # Headline (summary)
        if resume.summary:
            learner_info["Headline"] = {
                "Type": {"Code": "preferred", "Label": "Headline"},
                "Description": {"Label": resume.summary[:500]}
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
        
        # Skills
        skills = self._map_skills(resume)
        if skills:
            learner_info["Skills"] = skills
        
        # Languages (add to existing Skills section if present)
        if resume.languages:
            if "Skills" not in learner_info:
                learner_info["Skills"] = {}
            if "Linguistic" not in learner_info["Skills"]:
                learner_info["Skills"]["Linguistic"] = {
                    "MotherTongue": [],
                    "ForeignLanguage": []
                }
            
            for lang in resume.languages:
                # If proficiency is C2/Native, consider it mother tongue
                if lang.listening and lang.listening.upper() == 'C2':
                    learner_info["Skills"]["Linguistic"]["MotherTongue"].append({
                        "Description": {"Label": lang.language}
                    })
                else:
                    foreign_lang = {"Description": {"Label": lang.language}}
                    
                    # Add CEFR proficiency levels if available
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
                    
                    learner_info["Skills"]["Linguistic"]["ForeignLanguage"].append(foreign_lang)
        
        europass.LearnerInfo = learner_info
        
        return europass
    
    def _map_identification(self, resume: Resume) -> Optional[Dict[str, Any]]:
        """Map personal information to Europass Identification.
        
        Args:
            resume: Resume object
            
        Returns:
            Identification dict or None
        """
        pi = resume.personal_info
        
        identification: Dict[str, Any] = {}
        
        # PersonName
        if pi.first_name or pi.last_name:
            person_name = {}
            if pi.first_name:
                person_name["FirstName"] = pi.first_name
            if pi.last_name:
                person_name["Surname"] = pi.last_name
            identification["PersonName"] = person_name
        
        # ContactInfo
        contact_info: Dict[str, Any] = {}
        
        # Address
        if any([pi.address, pi.city, pi.postal_code, pi.country]):
            address = {"Contact": {}}
            address_line = []
            if pi.address:
                address_line.append(pi.address)
            if pi.city:
                address["Contact"]["Municipality"] = pi.city
            if pi.postal_code:
                address["Contact"]["PostalCode"] = pi.postal_code
            if pi.country:
                address["Contact"]["Country"] = {"Code": pi.country, "Label": pi.country}
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
            # Europass format for dates
            demographics["Birthdate"] = {
                "Year": pi.date_of_birth.year,
                "Month": f"--{pi.date_of_birth.month:02d}",
                "Day": f"---{pi.date_of_birth.day:02d}"
            }
        
        if pi.nationality:
            demographics["Nationality"] = [{"Code": pi.nationality, "Label": pi.nationality}]
        
        if demographics:
            identification["Demographics"] = demographics
        
        # Photo
        if self.include_photo and pi.photo:
            try:
                photo_b64 = base64.b64encode(pi.photo).decode('utf-8')
                identification["Photo"] = {
                    "MimeType": "image/jpeg",
                    "Data": photo_b64
                }
            except Exception:
                pass
        
        return identification if identification else None
    
    def _map_work_experience(self, exp: Any) -> Dict[str, Any]:
        """Map work experience to Europass format.
        
        Args:
            exp: WorkExperience object
            
        Returns:
            Europass work experience dict
        """
        work_exp: Dict[str, Any] = {}
        
        # Period (using proper Europass date format)
        period: Dict[str, Any] = {}
        if exp.start_date:
            period["From"] = {
                "Year": exp.start_date.year,
                "Month": f"--{exp.start_date.month:02d}",  # Europass format: --MM
                "Day": f"---{exp.start_date.day:02d}"      # Europass format: ---DD
            }
        
        if exp.end_date:
            period["To"] = {
                "Year": exp.end_date.year,
                "Month": f"--{exp.end_date.month:02d}",
                "Day": f"---{exp.end_date.day:02d}"
            }
        elif exp.current:
            period["Current"] = True
        
        if period:
            work_exp["Period"] = period
        
        # Position (with ISCO code if available)
        if exp.position:
            position = {"Label": exp.position}
            # Add ISCO-08 code if it can be inferred (default to software developer)
            if any(keyword in exp.position.lower() for keyword in ['developer', 'programmer', 'software', 'engineer']):
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
                    "Label": exp.country
                }
        
        if employer:
            work_exp["Employer"] = employer
        
        return work_exp
    
    def _map_education(self, edu: Any) -> Dict[str, Any]:
        """Map education to Europass format.
        
        Args:
            edu: Education object
            
        Returns:
            Europass education dict
        """
        education: Dict[str, Any] = {}
        
        # Period (using proper Europass date format)
        period: Dict[str, Any] = {}
        if edu.start_date:
            period["From"] = {
                "Year": edu.start_date.year,
                "Month": f"--{edu.start_date.month:02d}",
                "Day": f"---{edu.start_date.day:02d}"
            }
        
        if edu.end_date:
            period["To"] = {
                "Year": edu.end_date.year,
                "Month": f"--{edu.end_date.month:02d}",
                "Day": f"---{edu.end_date.day:02d}"
            }
        elif edu.current:
            period["Current"] = True
        
        if period:
            education["Period"] = period
        
        # Title
        if edu.title:
            education["Title"] = edu.title
        elif edu.description:
            # Use first line of description as title
            first_line = edu.description.split('\n')[0][:100]
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
                organization["ContactInfo"]["Address"]["Contact"]["Municipality"] = edu.city
            if edu.country:
                country_code = self._get_country_code(edu.country)
                organization["ContactInfo"]["Address"]["Contact"]["Country"] = {
                    "Code": country_code,
                    "Label": edu.country
                }
        
        if organization:
            education["Organisation"] = organization
        
        # Level (ISCED 2011)
        if edu.level:
            education["Level"] = {"Code": edu.level, "Label": self._get_isced_label(edu.level)}
        else:
            # Try to infer level from title
            level = self._infer_education_level(edu.title or "")
            if level:
                education["Level"] = level
        
        return education
    
    def _map_skills(self, resume: Resume) -> Optional[Dict[str, Any]]:
        """Map skills to Europass format.
        
        Args:
            resume: Resume object
            
        Returns:
            Skills dict or None
        """
        skills: Dict[str, Any] = {}
        
        # Communication/linguistic skills (languages)
        if resume.languages:
            linguistic: Dict[str, Any] = {"MotherTongue": [], "ForeignLanguage": []}
            
            for lang in resume.languages:
                if lang.is_native:
                    linguistic["MotherTongue"].append({"Description": {"Label": lang.language}})
                else:
                    foreign_lang: Dict[str, Any] = {"Description": {"Label": lang.language}}
                    
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
            computer_keywords = ['python', 'java', 'javascript', 'sql', 'html', 'css', 'git',
                                'docker', 'kubernetes', 'aws', 'azure', 'linux', 'windows']
            
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
            "8": "Doctoral or equivalent"
        }
        return isced_labels.get(code, f"Level {code}")
    
    def _infer_education_level(self, title: str) -> Optional[Dict[str, str]]:
        """Infer ISCED level from education title.
        
        Args:
            title: Education title
            
        Returns:
            Dict with Code and Label, or None
        """
        if not title:
            return None
        
        title_lower = title.lower()
        
        # Doctoral
        if any(word in title_lower for word in ['phd', 'doctorate', 'doctoral']):
            return {"Code": "8", "Label": "Doctoral or equivalent"}
        
        # Master
        if any(word in title_lower for word in ['master', 'msc', 'ma', 'mba']):
            return {"Code": "7", "Label": "Master or equivalent"}
        
        # Bachelor
        if any(word in title_lower for word in ['bachelor', 'bsc', 'ba', 'bs']):
            return {"Code": "6", "Label": "Bachelor or equivalent"}
        
        # Secondary
        if any(word in title_lower for word in ['high school', 'secondary', 'diploma', 'havo', 'vwo', 'mbo']):
            return {"Code": "3", "Label": "Upper secondary education"}
        
        return None

