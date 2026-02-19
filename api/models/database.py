from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class Document(Base):
    """Stores metadata about uploaded documents"""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50))  # pdf, docx, txt, etc
    file_size = Column(Integer)  # in bytes
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)  # has it been chunked/embedded?
    metadata_ = Column(JSON)  # extra info like author, page count, etc

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename})>"


class DocumentChunk(Base):
    """Stores individual chunks of documents with their embeddings"""

    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False)  # which document this belongs to
    chunk_index = Column(Integer, nullable=False)  # order of chunk in document
    content = Column(Text, nullable=False)  # the actual text
    embedding = Column(Vector(1024))  # vector representation (Voyage AI = 1024 dims)
    metadata_ = Column(JSON)  # page number, section, etc
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Chunk(id={self.id}, doc_id={self.document_id}, index={self.chunk_index})>"
