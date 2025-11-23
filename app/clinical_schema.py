from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

class ClinicalRecord(BaseModel):
    """Pydantic model for clinical data validation"""
    patient_id: str = Field(..., min_length=1, description="Patient identifier")
    visit_date: str = Field(..., description="Visit date in ISO format")
    measurement: Optional[float] = Field(None, ge=0, le=200, description="Clinical measurement")
    lab_test: str = Field(..., description="Type of lab test")
    notes: Optional[str] = None

    @field_validator('patient_id')
    @classmethod
    def validate_patient_id(cls, v):
        if not v.startswith('P'):
            raise ValueError('Patient ID must start with P')
        return v

    @field_validator('visit_date')
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError('Date must be in ISO format (YYYY-MM-DD)')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": "P001",
                "visit_date": "2024-01-15",
                "measurement": 98.5,
                "lab_test": "blood_pressure",
                "notes": "normal"
            }
        }
    }
