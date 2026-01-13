# Clinical Data Validation Pipeline

## Overview
Production-grade GxP-compliant data validation system for pharmaceutical regulatory affairs, demonstrating enterprise-level data integrity and audit trail practices.

## Architecture

### Key Components
- **REST API Microservice**: FastAPI-based architecture for scalable validation
- **Pydantic Schemas**: Type-safe data validation with business rule enforcement
- **Pandera DataFrames**: Schema validation for tabular clinical data
- **PostgreSQL 15**: Robust, ACID-compliant database for audit trails
- **AsyncPG**: High-performance asynchronous database driver
- **Loguru Logging**: Structured logging with rotation and retention policies
- **SHA-256 Hashing**: Data integrity verification at extract and load stages
- **Docker**: Reproducible, validated execution environment (Multi-container)

### Validation Layers
1. **Schema Validation** (Pandera): Column types, ranges, patterns
2. **Business Rules** (Pydantic): Patient ID format, date validation, measurement limits
3. **Clinical Logic**: Cross-field validation (e.g. hypotension vs normal notes)
4. **Data Quality** (Custom): Missing data, duplicates, referential integrity
5. **Integrity Checks**: Cryptographic hashing for tamper detection

## Technologies
Python 3.10 | FastAPI | Uvicorn | Docker | Pandas | Pandera | Pydantic | PostgreSQL | AsyncPG | Loguru | Pytest

## Run Instructions
```bash
docker-compose up --build
```

### Accessing the Application
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Usage**: Send POST requests to `/validate/upload`

## Output
- **Validated Data**: Returned as JSON response from the API
- **Audit Logs**: Queryable via `GET /audit/logs` (stored in PostgreSQL)
- **Logs**: `logs/pipeline.log` - Structured application logs

## Testing
```bash
pytest tests/ -v --cov=app
```

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
