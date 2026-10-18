FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY safeplate ./safeplate
RUN pip install --no-cache-dir .
ENV SAFEPLATE_HOME=/tmp/safeplate PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn safeplate.server:app --host 0.0.0.0 --port ${PORT}"]
