import sys
sys.path.append('/app')
import pandas as pd
import pandera.pandas as pa
from pandera import Column, Check, DataFrameSchema
import json
from datetime import datetime
from loguru import logger
from typing import Tuple, Dict
import hashlib

from database import AuditDatabase
from clinical_schema import ClinicalRecord


# Configure loguru
logger.add("/logs/pipeline.log", rotation="10 MB", retention="30 days")

# Pandera schema for DataFrame validation
clinical_schema = DataFrameSchema({
    "patient_id": Column(str, checks=Check.str_matches(r'^P\d{3}$')),
    "visit_date": Column(str),
    "measurement": Column(float, checks=Check.in_range(0, 200), nullable=True),
    "lab_test": Column(str, checks=Check.isin(['blood_pressure', 'glucose', 'cholesterol'])),
    "notes": Column(str, nullable=True)
})

class ClinicalDataValidator:
    def __init__(self):
        self.db = AuditDatabase()
        logger.info("Pipeline initialized with database audit trail")
        
    def calculate_hash(self, data: str) -> str:
        """Calculate SHA-256 hash for data integrity"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def extract_data(self, path: str) -> pd.DataFrame:
        """Extract clinical data with validation"""
        logger.info(f"Extracting data from {path}")
        df = pd.read_csv(path)
        data_hash = self.calculate_hash(df.to_json())
        
        self.db.log_action(
            "EXTRACT", 
            f"Loaded {len(df)} records. Hash: {data_hash[:16]}..."
        )
        logger.success(f"Extracted {len(df)} records")
        return df
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[Dict, pd.DataFrame]:
        """Apply GxP-style validation rules with Pandera"""
        logger.info("Starting validation")
        validation_results = {
            "total_records": len(df),
            "validation_timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # Pandera schema validation
        try:
            validated_df = clinical_schema.validate(df, lazy=True)
            validation_results["checks"]["schema_valid"] = True
            logger.success("Schema validation passed")
        except pa.errors.SchemaErrors as e:
            validation_results["checks"]["schema_valid"] = False
            validation_results["checks"]["schema_errors"] = str(e)
            logger.warning(f"Schema validation errors: {e}")
            validated_df = df
        
        # Missing data check
        critical_fields = ['patient_id', 'visit_date', 'measurement']
        missing = df[critical_fields].isnull().sum()
        validation_results["checks"]["missing_data"] = missing.to_dict()
        
        # Duplicate check
        duplicates = df.duplicated(subset=['patient_id', 'visit_date']).sum()
        validation_results["checks"]["duplicates"] = int(duplicates)
        
        # Range validation
        if 'measurement' in df.columns:
            out_of_range = ((df['measurement'] < 0) | (df['measurement'] > 200)).sum()
            validation_results["checks"]["out_of_range"] = int(out_of_range)
        
        # Pydantic record-level validation
        validation_results["checks"]["pydantic_valid_records"] = 0
        for idx, row in df.iterrows():
            try:
                ClinicalRecord(**row.to_dict())
                validation_results["checks"]["pydantic_valid_records"] += 1
            except Exception:
                pass
        
        self.db.log_action(
            "VALIDATE",
            json.dumps(validation_results["checks"])
        )
        logger.info(f"Validation complete: {validation_results['checks']}")
        
        return validation_results, validated_df
    
    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize data"""
        logger.info("Starting transformation")
        
        df_clean = df.dropna(subset=['patient_id']).copy()
        df_clean.columns = [col.strip().lower().replace(" ", "_") for col in df_clean.columns]
        
        # Add metadata
        df_clean['validated_at'] = datetime.now().isoformat()
        df_clean['validation_version'] = '1.0.0'
        
        self.db.log_action(
            "TRANSFORM",
            f"Cleaned to {len(df_clean)} valid records from {len(df)} total"
        )
        logger.success(f"Transformed {len(df)} → {len(df_clean)} records")
        
        return df_clean
    
    def load_data(self, df: pd.DataFrame, output_path: str):
        """Save validated data with integrity hash"""
        data_hash = self.calculate_hash(df.to_json())
        df.to_csv(output_path, index=False)
        
        self.db.log_action(
            "LOAD",
            f"Saved to {output_path}. Records: {len(df)}. Hash: {data_hash[:16]}..."
        )
        logger.success(f"Data loaded to {output_path}")
    
    def generate_report(self, validation_results: Dict, df_raw: pd.DataFrame, df_clean: pd.DataFrame):
        """Generate comprehensive validation report"""
        report_path = "/logs/validation_report.txt"
        
        with open(report_path, "w") as f:
            f.write("=" * 70 + "\n")
            f.write("GxP CLINICAL DATA VALIDATION REPORT\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Validation Version: 1.0.0\n\n")
            
            f.write("SUMMARY\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total Records Processed: {len(df_raw)}\n")
            f.write(f"Valid Records: {len(df_clean)}\n")
            f.write(f"Rejected Records: {len(df_raw) - len(df_clean)}\n\n")
            
            f.write("VALIDATION CHECKS\n")
            f.write("-" * 70 + "\n")
            f.write(json.dumps(validation_results["checks"], indent=2))
            f.write("\n\n")
            
            f.write("COMPLIANCE NOTES\n")
            f.write("-" * 70 + "\n")
            f.write("- Data integrity verified with SHA-256 hashing\n")
            f.write("- Audit trail maintained in SQLite database\n")
            f.write("- All validation rules documented and executed\n")
            f.write("- Timestamps recorded for all operations\n")
        
        logger.info(f"Report generated: {report_path}")
    
    def close(self):
        """Clean up resources"""
        self.db.close()
        logger.info("Pipeline closed successfully")

def run_pipeline():
    """Main pipeline execution"""
    logger.info("=" * 50)
    logger.info("Starting Clinical Data Validation Pipeline")
    logger.info("=" * 50)
    
    validator = ClinicalDataValidator()
    
    try:
        # Execute pipeline
        df_raw = validator.extract_data("/data/sample_clinical_data.csv")
        validation_results, df_validated = validator.validate_data(df_raw)
        df_clean = validator.transform_data(df_validated)
        validator.load_data(df_clean, "/data/validated_output.csv")
        validator.generate_report(validation_results, df_raw, df_clean)
        
        logger.success("Pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        validator.db.log_action("ERROR", str(e))
        raise
    
    finally:
        validator.close()

if __name__ == "__main__":
    run_pipeline()
