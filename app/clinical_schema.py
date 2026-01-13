from pydantic import BaseModel, Field, field_validator, model_validator
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

    @model_validator(mode='after')
    def validate_clinical_logic(self):
        lab_test = self.lab_test.lower() if self.lab_test else ""
        measurement = self.measurement
        notes = self.notes.lower() if self.notes else ""

        if lab_test == "blood_pressure" and measurement is not None:
            # Hypotension Rule
            if measurement < 90 and "normal" in notes:
                raise ValueError(
                    f"Clinical Mismatch: BP of {measurement} indicates Hypotension but notes say 'Normal'"
                )
            # Hypertension Rule
            if measurement > 140 and "normal" in notes:
                raise ValueError(
                    f"Clinical Mismatch: BP of {measurement} indicates Hypertension but notes say 'Normal'"
                )
            # Conflict Rule: Normal range but marked Abnormal
            # Assuming normal range is [90, 120] based on the prompt's Conflict Rule description
            if 90 <= measurement <= 120 and "abnormal" in notes:
                raise ValueError(
                    f"Clinical Mismatch: BP of {measurement} is within normal range (90-120) but notes say 'Abnormal'"
                )

        return self

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

# Pandera schema for DataFrame validation
import pandera as pa
from pandera import Column, Check, DataFrameSchema

clinical_schema = DataFrameSchema({
    "patient_id": Column(str, checks=Check.str_matches(r'^P\d{3}$')),
    "visit_date": Column(str),
    "measurement": Column(float, checks=Check.in_range(0, 200), nullable=True),
    "lab_test": Column(str, checks=Check.isin(['blood_pressure', 'glucose', 'cholesterol'])),
    "notes": Column(str, nullable=True)
}, coerce=True)
