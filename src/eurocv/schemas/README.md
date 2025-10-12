# Europass Schemas

This directory should contain the official Europass XML/JSON schemas for validation.

## Schema Files

The following schema files are recommended:

- `europass_cv_v3.xsd` - Europass CV XML Schema (Version 3.3)
- `europass_cv_v3.json` - Europass CV JSON Schema

## Downloading Schemas

Official Europass schemas can be downloaded from:

- **Europass Interoperable Europe**: https://interoperable.europe.eu/collection/europass
- **GitHub (Europass)**: https://github.com/europass
- **Official Documentation**: https://europa.eu/europass/en/europass-tools/developers

## Usage

The `SchemaValidator` class in `eurocv.core.validate.schema_validator` will automatically
look for schema files in this directory to perform validation.

## License

Europass schemas are provided by the European Union and are subject to their licensing terms.
Please refer to the official Europass documentation for license information.

## Note

Schema files are not included in this repository due to licensing and size considerations.
Users should download them separately if schema validation is required.

For basic validation without schemas, EuroCV performs structural validation against the
known Europass format requirements.

