# Smart Document Processing Pipeline

An intelligent document processing system that leverages LLMs, RAG (Retrieval Augmented Generation), and MCP (Model Context Protocol) for semantic document search and querying.

## Features

- 📄 Multi-format document processing (PDF, DOCX, TXT, etc.)
- 🔍 Semantic search using vector embeddings
- 🤖 LLM-powered question answering with RAG
- 🔌 Custom MCP server for document operations
- 🚀 RESTful API for easy integration
- ⚡ Async processing with Celery
- 🐘 PostgreSQL with pgvector for efficient vector search

## Tech Stack

- **API**: FastAPI
- **LLM**: Claude API (Anthropic)
- **RAG**: LangChain + pgvector
- **MCP**: Custom Model Context Protocol server
- **Database**: PostgreSQL with pgvector extension
- **Task Queue**: Celery + Redis
- **Embeddings**: Voyage AI / OpenAI

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Anthropic API key
- Voyage AI or OpenAI API key (for embeddings)

## Quick Start

1. **Clone the repository**
```bash
   git clone https://github.com/yourusername/smart-doc-processor.git
   cd smart-doc-processor
```

2. **Set up environment variables**
```bash
   cp .env.example .env
   # Edit .env with your API keys
```

3. **Start services with Docker**
```bash
   docker-compose up -d
```

4. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - MCP Server: http://localhost:3000

## Project Structure
```
smart-doc-processor/
├── api/              # FastAPI application
├── mcp_server/       # Custom MCP server
├── worker/           # Celery tasks
├── database/         # Database migrations
└── storage/          # Document storage
```

## Development Roadmap

- [x] Project setup
- [ ] Basic API endpoints
- [ ] Document processing pipeline
- [ ] RAG implementation
- [ ] MCP server development
- [ ] Testing & documentation
- [ ] Deployment

## Learning Objectives

This project demonstrates:
- Building production-ready LLM applications
- Implementing RAG from scratch
- Creating custom MCP servers
- RESTful API design for AI services
- Async task processing patterns
- Vector database optimization

## License

MIT

## Author

Your Name - [GitHub](https://github.com/yourusername)
```

### **10. Create empty `__init__.py` files**

Create empty files in these locations:
```
api/__init__.py
api/routes/__init__.py
api/models/__init__.py
api/services/__init__.py
mcp_server/__init__.py
mcp_server/tools/__init__.py
worker/__init__.py
tests/__init__.py