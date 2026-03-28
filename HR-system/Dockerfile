FROM python:3.11-slim

WORKDIR /app

COPY src/ /app
COPY credentials.json /app/credentials.json
COPY token.json /app/token.json
COPY gmail_token.json /app/gmail_token.json

RUN pip install --no-cache-dir \
    typing_extensions>=4.8.0 \
    anyio>=4.0.0 \
    fastapi>=0.109.0 \
    uvicorn>=0.27.0 \
    pydantic>=2.6.0 \
    python-dotenv>=1.0.0 \
    requests>=2.31.0 \
    "langchain>=0.2.0,<0.3.0" \
    "langchain-openai>=0.1.0,<0.2.0" \
    PyGithub>=2.1.1 \
    click>=8.1.7 \
    pymongo>=4.6.0 google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

ENV PYTHONUNBUFFERED=1

CMD ["python", "__main__.py", "--host", "0.0.0.0", "--port", "5000"]