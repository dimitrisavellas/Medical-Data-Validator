import pytest
import pandas as pd
from app.pipeline import ClinicalDataValidator
from app.clinical_schema import ClinicalRecord

def test_clinical_record_validation():
    """Test Pydantic schema validation"""
    valid_record = {
        "patient_id": "P001",
        "visit_date": "2024-01-15",
        "measurement": 98.5,
        "lab_test": "blood_pressure",
        "notes": "normal"
    }
    record = ClinicalRecord(**valid_record)
    assert record.patient_id == "P001"

def test_invalid_patient_id():
    """Test that invalid patient IDs are rejected"""
    with pytest.raises(ValueError):
        ClinicalRecord(
            patient_id="X001",
            visit_date="2024-01-15",
            measurement=98.5,
            lab_test="blood_pressure"
        )

def test_measurement_range():
    """Test measurement range validation"""
    with pytest.raises(ValueError):
        ClinicalRecord(
            patient_id="P001",
            visit_date="2024-01-15",
            measurement=300,  # Out of range
            lab_test="blood_pressure"
        )
