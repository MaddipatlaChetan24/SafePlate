FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY recipe_agent ./recipe_agent
RUN pip install --no-cache-dir .
ENV RECIPE_AGENT_HOME=/tmp/recipe_agent PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn recipe_agent.server:app --host 0.0.0.0 --port ${PORT}"]
