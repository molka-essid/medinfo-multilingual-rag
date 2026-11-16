FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
COPY app ./app
COPY static ./static
COPY data/chroma ./data/chroma
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir .
ENV CHROMA_DIR=/app/data/chroma
EXPOSE 8000
CMD ["python","-m","uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
