from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path

from api.models import get_db, init_db
from api.models.database import Document
from api.models.schemas import DocumentUploadResponse, DocumentOut
from api.config import get_settings

# 🆕 NEW IMPORT: Import the background processing task
from worker.tasks import process_document_task

# Initialize FastAPI app
app = FastAPI(
    title="Smart Document Processor",
    description="LLM-powered document processing with RAG",
    version="1.0.0",
)

# CORS middleware (allows frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = get_settings()

# Create upload directory if it doesn't exist
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Runs when API starts"""
    print("🚀 Starting Smart Document Processor API...")
    init_db()  # Create tables if they don't exist
    print("✅ Database initialized")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "Smart Document Processor API",
        "version": "1.0.0",
    }


@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a document for processing

    - Saves file to storage
    - Creates database record
    - Triggers background processing  # 🆕 NEW: Now triggers Celery task
    - Returns document ID for tracking
    """

    # Validate file type
    allowed_extensions = {".pdf", ".docx", ".txt", ".md"}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed: {allowed_extensions}",
        )

    # Check file size
    file.file.seek(0, 2)  # Move to end of file
    file_size = file.file.tell()  # Get position (= size)
    file.file.seek(0)  # Reset to beginning

    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_file_size / 1024 / 1024}MB",
        )

    # Save file to storage
    file_path = os.path.join(settings.upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create database record
    db_document = Document(
        filename=file.filename,
        file_type=file_ext.replace(".", ""),
        file_size=file_size,
        processed=False,
        metadata_={"original_path": file_path},
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # 🆕 NEW: TRIGGER BACKGROUND PROCESSING
    # process_document_task.delay() sends the task to Celery queue
    # .delay() is non-blocking - API returns immediately
    # Processing happens asynchronously in the worker
    # User gets instant response while document processes in background
    process_document_task.delay(db_document.id)

    return DocumentUploadResponse(
        id=db_document.id,
        filename=db_document.filename,
        file_size=db_document.file_size,
        message="Document uploaded successfully. Processing started in background.",  # 🆕 UPDATED MESSAGE
    )


@app.get("/documents", response_model=list[DocumentOut])
async def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents"""
    documents = db.query(Document).all()
    return documents


@app.get("/documents/{document_id}", response_model=DocumentOut)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a specific document by ID"""
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document
