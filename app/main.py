from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db, engine
from app.models import Base, AuditLog
from app.pipeline import ValidationService
from app.logging_config import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title="Medical Data Validator",
    description="GxP-compliant microservice for clinical data validation",
    version="2.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/validate/upload", status_code=status.HTTP_200_OK)
async def validate_upload(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    contents = await file.read()
    service = ValidationService(db)
    
    try:
        result = await service.process_file(contents, file.filename)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error")

@app.get("/audit/logs")
async def get_audit_logs(
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
        )
        logs = result.scalars().all()
        return logs
    except Exception as e:
        logger.error(f"Failed to retrieve audit logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve logs")
