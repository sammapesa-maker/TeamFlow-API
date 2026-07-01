FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

WORKDIR /app

# Copy dependency files first (better caching)
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv pip install --system .

# Copy app source
COPY . .

EXPOSE 8000

# Run migrations then start app
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]