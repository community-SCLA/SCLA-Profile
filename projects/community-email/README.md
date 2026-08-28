# Community email generator

Write in Notion; GitHub Actions runs the conversion using the saved SCLA design.

- [Setup and writing guide](docs/setup.md)
- [Cloud workflow](../../.github/workflows/community-email.yml)
- [Reusable MJML template](config/weekly-community.mjml)

The live connection is not activated. Code tests do not prove Notion access or a working button.

Run repository checks with `bash scripts/lint-refs.sh` from the repository root. Only synthetic examples belong in tests; this public repository is not an email archive.
