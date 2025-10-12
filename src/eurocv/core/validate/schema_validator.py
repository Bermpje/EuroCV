"""Europass schema validation."""

from pathlib import Path
from typing import Any


class SchemaValidator:
    """Validate Europass JSON/XML against official schemas."""

    def __init__(self):
        """Initialize validator."""
        self.schema_dir = Path(__file__).parent.parent.parent / "schemas"

    def validate_json(self, data: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate Europass JSON data.

        Args:
            data: Europass JSON data

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        # Basic structure validation
        if "DocumentInfo" not in data:
            errors.append("Missing required field: DocumentInfo")

        if "LearnerInfo" not in data:
            errors.append("Missing required field: LearnerInfo")
        else:
            learner_info = data["LearnerInfo"]

            # Validate identification if present
            if "Identification" in learner_info:
                id_errors = self._validate_identification(learner_info["Identification"])
                errors.extend(id_errors)

            # Validate work experience if present
            if "WorkExperience" in learner_info:
                for i, exp in enumerate(learner_info["WorkExperience"]):
                    exp_errors = self._validate_work_experience(exp, i)
                    errors.extend(exp_errors)

            # Validate education if present
            if "Education" in learner_info:
                for i, edu in enumerate(learner_info["Education"]):
                    edu_errors = self._validate_education(edu, i)
                    errors.extend(edu_errors)

        is_valid = len(errors) == 0
        return is_valid, errors

    def _validate_identification(self, identification: dict[str, Any]) -> list[str]:
        """Validate Identification section.

        Args:
            identification: Identification data

        Returns:
            List of validation errors
        """
        errors = []

        # PersonName validation
        if "PersonName" in identification:
            person_name = identification["PersonName"]
            if not isinstance(person_name, dict):
                errors.append("Identification.PersonName must be a dictionary")
            elif "Surname" not in person_name and "FirstName" not in person_name:
                errors.append("Identification.PersonName must have at least FirstName or Surname")

        # ContactInfo validation
        if "ContactInfo" in identification:
            contact_info = identification["ContactInfo"]
            if not isinstance(contact_info, dict):
                errors.append("Identification.ContactInfo must be a dictionary")

        return errors

    def _validate_work_experience(self, experience: dict[str, Any], index: int) -> list[str]:
        """Validate work experience entry.

        Args:
            experience: Work experience data
            index: Index of the experience entry

        Returns:
            List of validation errors
        """
        errors = []
        prefix = f"WorkExperience[{index}]"

        # Period validation
        if "Period" in experience:
            period = experience["Period"]
            if "From" not in period:
                errors.append(f"{prefix}.Period must have a 'From' date")

        return errors

    def _validate_education(self, education: dict[str, Any], index: int) -> list[str]:
        """Validate education entry.

        Args:
            education: Education data
            index: Index of the education entry

        Returns:
            List of validation errors
        """
        errors = []
        prefix = f"Education[{index}]"

        # Title is required
        if "Title" not in education:
            errors.append(f"{prefix} must have a Title")

        # Period validation
        if "Period" in education:
            period = education["Period"]
            if "From" not in period:
                errors.append(f"{prefix}.Period must have a 'From' date")

        return errors

    def validate_xml(self, xml_string: str) -> tuple[bool, list[str]]:
        """Validate Europass XML.

        Args:
            xml_string: XML string

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        try:
            from lxml import etree

            # Parse XML
            try:
                root = etree.fromstring(xml_string.encode("utf-8"))
            except etree.XMLSyntaxError as e:
                errors.append(f"XML syntax error: {str(e)}")
                return False, errors

            # Load schema if available
            schema_path = self.schema_dir / "europass_cv_v3.xsd"
            if schema_path.exists():
                try:
                    with open(schema_path, "rb") as f:
                        schema_doc = etree.parse(f)
                        schema = etree.XMLSchema(schema_doc)

                    if not schema.validate(root):
                        for error in schema.error_log:
                            errors.append(f"Line {error.line}: {error.message}")
                except Exception as e:
                    errors.append(f"Schema validation error: {str(e)}")
            else:
                # Basic XML structure check
                if root.tag != "Europass":
                    errors.append("Root element must be 'Europass'")

        except ImportError:
            errors.append("lxml not available for XML validation")

        is_valid = len(errors) == 0
        return is_valid, errors


def convert_to_xml(data: dict[str, Any]) -> str:
    """Convert Europass JSON to XML format.

    Args:
        data: Europass JSON data

    Returns:
        XML string
    """
    try:
        from lxml import etree

        # Create root element
        root = etree.Element(
            "Europass",
            xmlns="http://europass.cedefop.europa.eu/Europass",
            nsmap={"xsi": "http://www.w3.org/2001/XMLSchema-instance"},
        )

        # Add DocumentInfo
        if "DocumentInfo" in data:
            doc_info = etree.SubElement(root, "DocumentInfo")
            for key, value in data["DocumentInfo"].items():
                elem = etree.SubElement(doc_info, key)
                elem.text = str(value)

        # Add LearnerInfo
        if "LearnerInfo" in data:
            learner_info = etree.SubElement(root, "LearnerInfo")
            _dict_to_xml(data["LearnerInfo"], learner_info)

        # Pretty print
        xml_string = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        return xml_string.decode("utf-8")

    except ImportError:
        # Fallback to simple XML generation
        import xmltodict

        xml_dict = {"Europass": data}
        return xmltodict.unparse(xml_dict, pretty=True)


def _dict_to_xml(data: Any, parent: Any) -> None:
    """Recursively convert dict to XML elements.

    Args:
        data: Data to convert
        parent: Parent XML element
    """
    from lxml import etree

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    child = etree.SubElement(parent, key)
                    _dict_to_xml(item, child)
            elif isinstance(value, dict):
                child = etree.SubElement(parent, key)
                _dict_to_xml(value, child)
            else:
                child = etree.SubElement(parent, key)
                child.text = str(value) if value is not None else ""
    else:
        parent.text = str(data) if data is not None else ""
