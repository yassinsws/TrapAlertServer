import json

from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from db import engine, Base, get_db
from models import BugReport, Tenant
import uuid
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from transcriber import AiEngine

# Import routers
from routers import auth, reports, tenants, users, integrations

# Create the tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TrapAlert API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(tenants.router)
app.include_router(users.router)
app.include_router(integrations.router)

@app.get("/")
async def root():
    return {"message": "TrapAlert API", "version": "1.0.0"}

@app.post("/feedback")
async def receive_feedback(
    video: UploadFile = File(...),
    dom: str = Form(...),
    metadata: str = Form(...),
    tenantId: str = Form(...),
    description: str = Form(None),
    struggleScore: float = Form(None),
    db: Session = Depends(get_db)
):
    """
    Public endpoint for receiving bug reports from TrapAlert.js SDK
    Authenticates using tenant API key
    """
    # Verify tenant API key
    tenant = db.query(Tenant).filter(Tenant.api_key == tenantId, Tenant.is_active == True).first()
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid tenant API key")
    
    # 0. Read video bytes
    video_bytes = await video.read()
    
    # 1. Upload to Supabase (replaces local compression)
    from video_utils import upload_video_to_supabase
    video_url = upload_video_to_supabase(video_bytes, video.content_type or "video/webm")
    
    # 2. Seek back to 0 for transcription engine
    await video.seek(0)
    
    # 3. Transcribe video
    eng = AiEngine()
    transcript = await eng.transcribe(video) 
    
    # 3. Generate labels
    raw_labels = eng.generate_labels(transcript)
    label_list = [item.strip() for item in raw_labels.split(",")]

    # 4. Create the bug report
    new_report = BugReport(
        tenant_id=tenant.id,
        description=description or transcript,
        struggle_score=struggleScore,
        metadata_json=metadata,
        dom_snapshot=dom,
        label=label_list,
        video_url=video_url,
    )
    
    logger.info(f"DEBUG: Created BugReport with video_url: {video_url}")

    # 5. Save to DB
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    logger.info(f"DEBUG: Saved report ID {new_report.id}")

    return {"status": "success", "id": new_report.id}