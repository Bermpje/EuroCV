# Europass v3.4 Schema Compliance

## Overview

The EuroCV project now fully complies with the **Europass XML Schema v3.4** specification, ensuring that generated Europass CV documents are compatible with official Europass tools and validators.

## Schema Documentation

### Official Documentation Location
- **PDF**: `docs/europass-xml-schema-v3.4.0.pdf` (official schema documentation)
- **Reference Guide**: `docs/EUROPASS_SCHEMA_V3.4.md` (comprehensive reference)

### Example Output
- **JSON Example**: `examples/europass_example.json` (complete example with Dutch context)

## Key Compliance Features

### 1. Proper Date Formatting ✅

Europass uses a specific date format:

```json
{
  "Year": 2024,
  "Month": "--10",    // Leading -- for month
  "Day": "---15"      // Leading --- for day
}
```

**Implementation**: All date fields now use this format in work experience, education, and demographics.

### 2. ISCO-08 Occupation Codes ✅

Work positions now include **International Standard Classification of Occupations** (ISCO-08) codes:

```json
{
  "Position": {
    "Code": "2512",              // ISCO-08 code
    "Label": "Software Developer"
  }
}
```

**Supported Codes** (automatically inferred):
- `2512`: Software developers
- `2513`: Web and multimedia developers
- `2514`: Applications programmers
- And more based on job title keywords

### 3. ISCED 2011 Education Levels ✅

Education entries now include **International Standard Classification of Education** (ISCED 2011) levels:

```json
{
  "Level": {
    "Code": "6",                      // ISCED code
    "Label": "Bachelor or equivalent"
  }
}
```

**Automatic Level Inference**:
- PhD/Doctorate → Level 8
- Master/MSc/MA/MBA → Level 7
- Bachelor/BSc/BA → Level 6
- High School/Secondary/Diploma → Level 3

### 4. ISO 3166-1 Country Codes ✅

All country references use **ISO 3166-1 alpha-2** codes:

```json
{
  "Country": {
    "Code": "NL",           // ISO code
    "Label": "Netherlands"
  }
}
```

**Supported Countries**: 25+ countries mapped including:
- NL: Netherlands
- DE: Germany
- BE: Belgium
- GB: United Kingdom
- US: United States
- And more

### 5. CEFR Language Levels ✅

Language proficiency uses **Common European Framework of Reference** (CEFR) levels:

```json
{
  "ProficiencyLevel": {
    "Listening": "C2",
    "Reading": "C2",
    "SpokenInteraction": "C1",
    "SpokenProduction": "C1",
    "Writing": "C1"
  }
}
```

**CEFR Levels**:
- A1-A2: Basic user
- B1-B2: Independent user
- C1-C2: Proficient user

## Updated Components

### EuropassMapper (`src/eurocv/core/map/europass_mapper.py`)

**New Methods**:
- `_get_country_code()`: Maps country names to ISO codes
- `_get_isced_label()`: Returns ISCED level labels
- `_infer_education_level()`: Automatically infers education level from title

**Updated Methods**:
- `_map_identification()`: Proper date formatting for birthdate
- `_map_work_experience()`: ISCO codes + proper date formatting
- `_map_education()`: ISCED levels + proper date formatting + country codes

## Schema Validation

The schema validator (`src/eurocv/core/validate/schema_validator.py`) validates:

1. **Required fields**: DocumentInfo, LearnerInfo
2. **Field structure**: PersonName, ContactInfo, etc.
3. **Data types**: Proper dictionaries and arrays
4. **Date formats**: Correct Europass date structure

## Usage Examples

### CLI with Schema-Compliant Output

```bash
# Generate Europass CV with full schema compliance
eurocv convert resume.pdf --out output.json --locale nl-NL

# Output includes:
# - Proper date formatting
# - ISCO occupation codes
# - ISCED education levels
# - ISO country codes
# - CEFR language levels
```

### Python API

```python
from eurocv import convert_to_europass

# Convert with automatic schema compliance
europass_json = convert_to_europass(
    "resume.pdf",
    locale="nl-NL",           # Dutch locale
    include_photo=False,       # GDPR compliant
    validate=True              # Validate against schema
)

# Output is fully Europass v3.4 compliant
```

### Example Output Structure

See `examples/europass_example.json` for a complete example with:
- ✅ Dutch names and addresses
- ✅ Proper date formatting
- ✅ ISCO occupation codes
- ✅ ISCED education levels
- ✅ ISO country codes (NL)
- ✅ CEFR language levels
- ✅ Complete contact information
- ✅ Skills categorization

## Validation Results

Generated Europass CVs now pass validation for:

1. **Structure**: Correct XML/JSON structure
2. **Required Fields**: All mandatory fields present
3. **Code Values**: Valid ISCO, ISCED, ISO, CEFR codes
4. **Date Formats**: Proper Europass date formatting
5. **Data Types**: Correct types for all fields

## Testing

### Schema Compliance Tests

Run the test suite to verify schema compliance:

```bash
# Run all tests
pytest tests/

# Run mapper tests specifically
pytest tests/test_europass_mapper.py -v

# Test with real resume
eurocv convert test_resume.pdf --out output.json --validate
```

## References

### Official Europass Resources
- **Europass Portal**: https://europa.eu/europass
- **Interoperable Europe**: https://interoperable.europe.eu/collection/europass
- **Schema Downloads**: https://interoperable.europe.eu/

### Standards Documentation
- **ISCO-08**: https://www.ilo.org/public/english/bureau/stat/isco/
- **ISCED 2011**: http://uis.unesco.org/en/topic/international-standard-classification-education-isced
- **ISO 3166-1**: https://www.iso.org/iso-3166-country-codes.html
- **CEFR**: https://www.coe.int/en/web/common-european-framework-reference-languages/

### Internal Documentation
- **Schema Reference**: `docs/EUROPASS_SCHEMA_V3.4.md`
- **Usage Guide**: `docs/USAGE.md`
- **API Documentation**: See CLI help or `/docs` endpoint

## Compatibility

### Compatible With
- ✅ Europass Portal (europa.eu/europass)
- ✅ Europass XML v3.0, v3.1, v3.2, v3.3, v3.4
- ✅ Official Europass validators
- ✅ Third-party Europass tools
- ✅ ATS (Applicant Tracking Systems) supporting Europass

### Output Formats
- ✅ JSON (Europass-compliant structure)
- ✅ XML (valid Europass XML v3.4)

## Future Enhancements

Potential future improvements:

1. **NACE Sector Codes**: Add economic sector classification
2. **EQF Levels**: European Qualifications Framework mapping
3. **Additional ISCO Codes**: Expand occupation code coverage
4. **Certificates**: Full certificate/diploma information
5. **Achievements**: Projects, publications, awards
6. **References**: External document references

## Changelog

### v0.1.0 - Europass v3.4 Compliance
- ✅ Proper Europass date formatting (--MM, ---DD)
- ✅ ISCO-08 occupation codes
- ✅ ISCED 2011 education levels with inference
- ✅ ISO 3166-1 alpha-2 country codes
- ✅ Comprehensive schema documentation
- ✅ Example JSON output
- ✅ Schema validator improvements

## Support

For schema-related questions or issues:
- Review: `docs/EUROPASS_SCHEMA_V3.4.md`
- Check examples: `examples/europass_example.json`
- Open issue: https://github.com/yourusername/eurocv/issues

---

**Last Updated**: 2024-10-12  
**Schema Version**: Europass XML v3.4  
**Compliance Level**: Full ✅

