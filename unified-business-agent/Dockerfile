# Unified Business Agent - Dockerfile
# Team Sleepyhead - Nasiko Hackathon 2026

FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update -o Acquire::Retries=5 -o Acquire::http::Timeout=30 && apt-get install -y --no-install-recommends \
    ca-certificates \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    fastapi>=0.109.0 \
    uvicorn>=0.27.0 \
    pydantic>=2.6.0 \
    python-dotenv>=1.0.0 \
    "langchain>=0.2.0,<0.3.0" \
    "langchain-core>=0.2.0,<0.3.0" \
    langchain-groq>=0.1.0 \
    groq>=0.4.0 \
    pymongo>=4.6.0 \
    pandas>=2.0.0 \
    openpyxl>=3.1.0 \
    numpy>=1.24.0 \
    google-auth>=2.27.0 \
    google-auth-oauthlib>=1.2.0 \
    google-auth-httplib2>=0.2.0 \
    google-api-python-client>=2.115.0 \
    pytesseract>=0.3.10 \
    Pillow>=10.0.0 \
    PyPDF2>=3.0.0 \
    pdf2image>=1.16.3 \
    requests>=2.31.0 \
    click>=8.1.7 \
    python-dateutil>=2.8.2 \
    pytz>=2024.1

# Copy application code
COPY src/ ./src/
COPY AgentCard.json ./

# Copy credentials directory (will be empty, populated at runtime)
COPY credentials/ ./credentials/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/uploads

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run the agent
CMD ["python", "-m", "src"]
