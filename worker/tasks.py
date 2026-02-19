"""Background tasks for document processing"""

from celery import Task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from worker.celery_app import celery_app
from api.services.document_processor import DocumentProcessor, TextChunker
from api.services.embeddings import EmbeddingService
from api.models.database import Document, DocumentChunk
from api.config import get_settings

settings = get_settings()

# Create database session for worker
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)


class DatabaseTask(Task):
    """Base task with database session management"""

    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()


@celery_app.task(base=DatabaseTask, bind=True)
def process_document_task(self, document_id: int):
    """
    Process uploaded document: extract text, chunk, embed, store

    Args:
        document_id: ID of document in database
    """
    print(f"🔄 Processing document {document_id}...")

    # Get document from database
    document = self.db.query(Document).filter(Document.id == document_id).first()

    if not document:
        print(f"❌ Document {document_id} not found")
        return {"error": "Document not found"}

    try:
        # Step 1: Extract text from document
        print(f"📄 Extracting text from {document.filename}...")
        file_path = os.path.join(settings.upload_dir, document.filename)

        processor = DocumentProcessor()
        full_text = processor.extract_text(file_path)

        if not full_text or len(full_text.strip()) < 10:
            raise ValueError("No text extracted from document")

        print(f"✅ Extracted {len(full_text)} characters")

        # Step 2: Chunk the text
        print(f"✂️  Chunking text...")
        chunker = TextChunker(
            chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
        )
        chunks = chunker.chunk_text(full_text)

        print(f"✅ Created {len(chunks)} chunks")

        # Step 3: Generate embeddings
        print(f"🧮 Generating embeddings...")
        embedding_service = EmbeddingService(api_key=settings.voyage_api_key)

        # Extract just the text content for embedding
        chunk_texts = [chunk["content"] for chunk in chunks]
        embeddings = embedding_service.embed_batch(chunk_texts)

        print(f"✅ Generated {len(embeddings)} embeddings")

        # Step 4: Store chunks in database
        print(f"💾 Storing chunks in database...")
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            db_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=chunk["index"],
                content=chunk["content"],
                embedding=embedding,
                metadata_=chunk["metadata"],
            )
            self.db.add(db_chunk)

        # Mark document as processed
        document.processed = True
        self.db.commit()

        print(f"✅ Document {document_id} processed successfully!")

        return {
            "document_id": document_id,
            "chunks_created": len(chunks),
            "status": "success",
        }

    except Exception as e:
        print(f"❌ Error processing document {document_id}: {str(e)}")
        self.db.rollback()

        # Update document with error
        document.processed = False
        document.metadata_ = document.metadata_ or {}
        document.metadata_["error"] = str(e)
        self.db.commit()

        return {"document_id": document_id, "status": "error", "error": str(e)}
