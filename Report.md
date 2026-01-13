Clinical Data Validation Pipeline
Project Explanation and Architecture

Purpose and Use Case

This project demonstrates a modern, GxP-compliant data validation system suitable for pharmaceutical and clinical research environments. Its primary purpose is to automate the quality assurance processes for clinical trial or medical records data: ensuring it is complete, accurate, traceable, and fully auditable for regulatory requirements like 21 CFR Part 11 or ALCOA+ principles.

Pipeline Workflow

The pipeline is designed in four main stages, following best practices for healthcare ETL systems:

Extract: Loads source data from API uploads (CSV) instead of local files.

Validate: Applies multi-layered data validation:

Column schema checks (Pandera)

Record and field-level business logic (Pydantic)

Cross-field Clinical Logic (e.g. Hypertension rules)

Custom rules for missing data, duplicates, and measurement ranges

Transform: Cleans and standardizes data, adding metadata for traceability.

Load: Returns validated data as JSON and commits all actions to a PostgreSQL audit trail using atomic transactions for data integrity.

Concurrency and Performance

The new microservice architecture uses FastAPI and AsyncPG to handle multiple validation requests concurrently. Unlike the previous blocking script, this system can process high-throughput data uploads without stalling, making it suitable for enterprise deployments.

Database

Switching from SQLite to PostgreSQL 15 provides robust, enterprise-grade data integrity. PostgreSQL offers row-level locking, better concurrency control, and strictly ACID-compliant transactions, which are critical for maintaining a GxP-compliant audit trail that cannot be corrupted by race conditions.

Key Libraries and Their Roles

FastAPI: High-performance web framework for building APIs with Python 3.10+, providing automatic Swagger documentation.

pandas: Efficient data loading, manipulation, and initial transformation of tabular health records.

pandera: DataFrame schema validation—declares required columns, types, allowed values, and medical data ranges. Fails records with out-of-range values (e.g., impossible measurements) or missing critical data.

pydantic: Models row-level business rules for each patient record (such as ID formats or date checks), catching mistakes that Pandera’s schema might miss (e.g., Patient IDs must start with 'P').

PostgreSQL & AsyncPG: Persists full audit trail to a robust database, documenting every step and change for later review during audits or regulatory submissions.

loguru: Handles structured and colorful logging of pipeline actions, warnings, and errors—making quality issues obvious for operators and for audit traceability.

Docker: Guarantees a reproducible, validated environment—system dependencies and versions are fixed for both developer and production use.

Quality Checks and Validation Logic

Missing Data: The pipeline counts and flags any essential field (like patient ID, visit date, or measurement) that is absent.

Duplicate Records: Identifies repeated measurements for the same patient and date, which can indicate data entry errors or protocol violations.

Range Validation: Flags measurements (e.g., clinical values) that fall outside biologically credible bounds (e.g., a glucose reading of 250 where normal is 70–200).

Business Rule Validation: Checks via Pydantic that patient IDs conform to required format and dates are ISO-compliant. Also enforces semantic consistency between clinical values and notes.

Audit Trail and Data Integrity: Each pipeline step is logged with timestamp, action, details, and user. Data hashes are computed for output integrity, supporting tamper-evidence and regulatory traceability.

Schema and Modularity

DataFrameSchema (Pandera): Explicitly declares required columns, types, and custom checks. This schema is versioned and can be adapted for new studies or future standards.

Pydantic Model: Defines record-specific checks that are reusable and sharable for other systems or datasets.

Pipeline Modularization: Each step is separated functionally, supporting future expansion: load from different sources (e.g., EDC, APIs), run additional checks, or deploy to production easily.

Outcome

The result is a robust, transparent system that detects and reports all major quality failures automatically, logs every operation, and prepares data and reports for downstream statistical analysis or regulatory submission. This architecture aligns with industry standards for clinical data management and supports operational efficiency, audit readiness, and data integrity.