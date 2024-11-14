# PG Vector Demo: Document Management System with Vector Search

This project demonstrates two implementations of vector similarity search using PostgreSQL with pgvector extension:
1. Raw pgvector implementation
2. LangChain integration with pgvector

## 🚀 Features

- Document processing and embedding generation for:
  - PDF files
  - Word documents (.docx)
  - Text files
  - PowerPoint presentations
  - Videos (MP4)
  - Images (JPG, PNG)
  - YouTube URLs
- Dual vector similarity search implementations
- Document categorization and metadata management
- Permission-based access control
- Interactive web interface using Streamlit

## 🛠️ Setup

### 1. PostgreSQL with pgvector

#### Option A: Local Installation

1. Ensure C++ support in Visual Studio is installed
2. Set up Visual Studio environment:

```bash
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
```

3. Build and install pgvector:

```bash
set "PGROOT=C:\Program Files\PostgreSQL\16"
cd %TEMP%
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
nmake /F Makefile.win
nmake /F Makefile.win install
```

#### Option B: Docker Installation

```bash
docker run --name pgvector-container \
  -e POSTGRES_USER=langchain \
  -e POSTGRES_PASSWORD=langchain \
  -e POSTGRES_DB=langchain \
  -p 6024:5432 \
  -d pgvector/pgvector:pg16
```

### 2. Database Configuration

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Verify installation:
```sql
SELECT * FROM pg_extension;
```

### 3. Environment Variables

Create a `.env` file with:
```
DB_NAME=langchain
DB_USERNAME=langchain
DB_PASSWORD=langchain
DB_PORT=6024
DB_HOST=localhost
OPENAI_API_KEY=your_openai_api_key
```

## 📱 Web Interface (app.py)

The Streamlit application provides two main functionalities:

### 1. Document Upload (📤 Upload Document)
- File upload support for multiple formats
- YouTube URL processing
- Document categorization with:
  - Sections
  - Subsections
  - Categories
  - Learning Types
  - Permission Levels
- Real-time processing status
- Detailed processing results including:
  - Document summary
  - Processing costs
  - Token usage
  - Additional metadata (resolution for images, duration for videos)

### 2. Document Search (🔍 Get Recommendations)
- Dual search implementation comparison:
  - Raw pgvector implementation (DocumentRetriever)
  - LangChain integration
- Advanced filtering options:
  - Result limit
  - Resource ID
  - Permissions
  - Categories
  - Subsections
  - Learning Types
- Performance metrics for both search implementations
- Side-by-side result comparison

## 🔍 Vector Search Implementations

### 1. Raw pgvector (DocumentRetriever)
- Direct PostgreSQL integration using pgvector
- Custom SQL queries for similarity search
- Metadata filtering support
- Performance optimized for specific use cases

### 2. LangChain Integration
- Simplified vector store implementation
- Built-in document processing
- Automatic embedding generation
- Easy-to-use similarity search interface
- Additional features like MMR search

## 📚 Project Structure

```
📁 Project Root
├── 📁 src/
│   ├── 📁 db/
│   │   ├── __init__.py
│   │   ├── config.py          # Database configuration and connection setup
│   │   ├── db_manager.py      # Database operations and management
│   │   └── models.py          # SQLAlchemy models and table definitions
│   │
│   ├── 📁 docs/              # Document storage directory
│   │   └── .gitignore        # Ignores all files except .gitignore
│   │
│   ├── 📁 pg_vector_test/    # PGVector testing implementations
│   │   ├── docs_pg_vector.py  # PGVector document testing
│   │   └── init_pgvector.py   # PGVector initialization
│   │
│   ├── document_loader.py     # Universal document processing
│   ├── document_processor.py  # Document processing and storage
│   ├── document_retriever.py  # Document search and retrieval
│   └── langchain_processor.py # LangChain integration
│
├── 📁 venv/                   # Virtual environment (not tracked)
├── .env                       # Environment variables (not tracked)
├── .gitignore                # Git ignore configuration
├── README.md                 # Project documentation
├── app.py                    # Streamlit web application
└── requirements.txt          # Project dependencies
```

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
