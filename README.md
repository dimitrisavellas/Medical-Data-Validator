# Clinical Data Validation Pipeline

## Overview
Production-grade GxP-compliant data validation system for pharmaceutical regulatory affairs, demonstrating enterprise-level data integrity and audit trail practices.

## Architecture

### Key Components
- **Pydantic Schemas**: Type-safe data validation with business rule enforcement
- **Pandera DataFrames**: Schema validation for tabular clinical data
- **SQLAlchemy Audit Database**: Persistent, queryable audit trail (21 CFR Part 11)
- **Loguru Logging**: Structured logging with rotation and retention policies
- **SHA-256 Hashing**: Data integrity verification at extract and load stages
- **Docker**: Reproducible, validated execution environment

### Validation Layers
1. **Schema Validation** (Pandera): Column types, ranges, patterns
2. **Business Rules** (Pydantic): Patient ID format, date validation, measurement limits
3. **Data Quality** (Custom): Missing data, duplicates, referential integrity
4. **Integrity Checks**: Cryptographic hashing for tamper detection

## Technologies
Python 3.10 | Docker | Pandas | Pandera | Pydantic | SQLAlchemy | Loguru | Pytest

## Run Instructions
docker-compose up --build

## Output
- data/validated_output.csv - Validated clinical data with metadata
- logs/audit_trail.db - SQLite database with complete audit trail
- logs/pipeline.log - Structured application logs with rotation
- logs/validation_report.txt - Comprehensive validation summary

## Testing
pytest tests/ -v --cov=app

## GxP Compliance Features
✅ **Data Integrity (ALCOA+)**
- Attributable: User tracking in audit log
- Legible: Structured logs and reports
- Contemporaneous: Real-time timestamping
- Original: Source data hash verification
- Accurate: Multi-layer validation

✅ **21 CFR Part 11 Concepts**
- Audit trail with timestamps
- Data integrity checks
- System validation documentation
- Access controls (user field)

✅ **Computer System Validation**
- Automated testing (pytest)
- Reproducible environment (Docker)
- Version-controlled validation logic
- Documented validation rules

## Relevance to Pharmaceutical IT
This project demonstrates practical understanding of:
- GxP-compliant system design
- Regulatory data requirements
- Validation and testing practices
- Audit trail implementation
- Data integrity principles
- Quality assurance automation
