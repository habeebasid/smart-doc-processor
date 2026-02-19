"""Extract text from different document types"""

import os
from pathlib import Path
from typing import Optional

from pypdf import PdfReader
from docx import Document as DocxDocument


class DocumentProcessor:
    """Handles text extraction from various document formats"""

    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extract text from document based on file extension

        Args:
            file_path: Path to the document file

        Returns:
            Extracted text as string
        """
        file_ext = Path(file_path).suffix.lower()

        if file_ext == ".pdf":
            return DocumentProcessor._extract_from_pdf(file_path)
        elif file_ext == ".docx":
            return DocumentProcessor._extract_from_docx(file_path)
        elif file_ext in [".txt", ".md"]:
            return DocumentProcessor._extract_from_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        text = []
        reader = PdfReader(file_path)

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)

        return "\n\n".join(text)

    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        doc = DocxDocument(file_path)
        text = []

        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)

        return "\n\n".join(text)

    @staticmethod
    def _extract_from_text(file_path: str) -> str:
        """Extract text from plain text or markdown files"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()


class TextChunker:
    """Splits text into overlapping chunks for RAG"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> list[dict]:
        """
        Split text into overlapping chunks - SIMPLIFIED VERSION
        """
        if not text or not text.strip():
            return []

        chunks = []
        words = text.split()

        # Approximate words per chunk (assuming avg 5 chars per word)
        words_per_chunk = self.chunk_size // 5
        overlap_words = self.chunk_overlap // 5

        start_idx = 0
        chunk_index = 0

        while start_idx < len(words):
            # Get chunk worth of words
            end_idx = start_idx + words_per_chunk
            chunk_words = words[start_idx:end_idx]
            chunk_text = " ".join(chunk_words)

            if chunk_text.strip():
                chunks.append(
                    {
                        "index": chunk_index,
                        "content": chunk_text,
                        "metadata": {
                            "word_start": start_idx,
                            "word_end": end_idx,
                            "length": len(chunk_text),
                        },
                    }
                )
                chunk_index += 1

            # Move forward with overlap
            start_idx = end_idx - overlap_words

            # Safety check - prevent infinite loop
            if start_idx >= len(words) - overlap_words:
                break

        print(f"✅ Chunked into {len(chunks)} pieces")
        return chunks
