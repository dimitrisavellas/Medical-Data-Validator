import hashlib
import json
import pandas as pd
import pandera.pandas as pa
from datetime import datetime
from typing import Tuple, Dict, Optional
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.clinical_schema import ClinicalRecord, clinical_schema
from app.models import AuditLog

class ValidationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def calculate_hash(self, data: str) -> str:
        """Calculate SHA-256 hash for data integrity"""
        return hashlib.sha256(data.encode()).hexdigest()

    async def log_audit(self, action: str, details: str, record_hash: Optional[str] = None):
        """Log action to audit trail with strict transaction handling"""
        try:
            audit_entry = AuditLog(
                action=action,
                details=details,
                record_hash=record_hash
            )
            self.db.add(audit_entry)
            await self.db.commit() # Ensure atomicity at the log level if needed immediately, or let caller handle commit
            # In a service pattern, usually we might let the UOW handle commit, but for audit logs we often want them immediate.
            # However, sharing the session means we should be careful.
            # Let's assume we commit here for the audit log specifically to ensure it's written.
            # But if the main transaction fails, we might want to ANYWAY log the failure.
            # For now, we use the passed session.
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
            # If logging fails, we might want to alert, but not crash the whole request?
            # GxP requirements usually say if audit fails, everything must fail.
            raise e

    async def process_file(self, content: bytes, filename: str) -> Dict:
        """Process and validate uploaded file"""
        logger.info(f"Processing file: {filename}")
        
        # 1. EXTRACT
        try:
            df = pd.read_csv(pd.io.common.BytesIO(content))
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")

        raw_json = df.to_json()
        input_hash = self.calculate_hash(raw_json)
        
        await self.log_audit(
            action="EXTRACT",
            details=f"Received file {filename}. Records: {len(df)}",
            record_hash=input_hash
        )

        # 2. VALIDATE
        validation_results, df_validated = self._validate_dataframe(df)
        
        await self.log_audit(
            action="VALIDATE",
            details=json.dumps(validation_results),
            record_hash=input_hash # Link validation to input hash
        )

        # 3. TRANSFORM
        df_clean = self._transform_dataframe(df_validated)
        
        output_json = df_clean.to_json()
        output_hash = self.calculate_hash(output_json)

        await self.log_audit(
            action="TRANSFORM",
            details=f"Cleaned records: {len(df_clean)}",
            record_hash=output_hash
        )
        
        return {
            "filename": filename,
            "validation_results": validation_results,
            "processed_records": len(df_clean),
            "input_hash": input_hash,
            "output_hash": output_hash,
            "cleaned_data": df_clean.to_dict(orient="records")
        }

    def _validate_dataframe(self, df: pd.DataFrame) -> Tuple[Dict, pd.DataFrame]:
        """Internal validation logic"""
        results = {
            "valid": True,
            "timestamp": datetime.utcnow().isoformat(),
            "errors": []
        }
        
        # Pandera Schema Validation
        try:
            validated_df = clinical_schema.validate(df, lazy=True)
        except pa.errors.SchemaErrors as e:
            results["valid"] = False
            # Serializable error structure
            results["errors"].append({"type": "schema", "details": str(e)})
            validated_df = df # Continue with raw data if schema fails, to flag specific rows? 
            # Or usually we might stop. Original code continued.

        # Pydantic Row Validation
        invalid_rows = 0
        for idx, row in df.iterrows():
            try:
                ClinicalRecord(**row.to_dict())
            except Exception as e:
                invalid_rows += 1
                # We could log specific row errors here if detailed reporting is needed
        
        results["pydantic_invalid_count"] = invalid_rows
        if invalid_rows > 0:
             results["valid"] = False
        
        return results, validated_df

    def _transform_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize"""
        df_clean = df.copy()
        # Drop rows where critical ID is missing
        if 'patient_id' in df_clean.columns:
            df_clean = df_clean.dropna(subset=['patient_id'])
        
        # Standardize columns
        df_clean.columns = [str(col).strip().lower().replace(" ", "_") for col in df_clean.columns]
        
        return df_clean
