# Install uv
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential libpq-dev libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Change the working directory to the `app` directory
WORKDIR /app

# Copy the lockfile and `pyproject.toml` into the image
COPY uv.lock /app/uv.lock
COPY pyproject.toml /app/pyproject.toml

# Install dependencies
RUN uv sync --frozen --no-dev --extra server --no-install-project

# Copy the project into the image
COPY src/hgvs_dataproviders_rest /app/hgvs_dataproviders_rest

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "hgvs_dataproviders_rest.restapi:app", "--host", "0.0.0.0", "--port", "8000"]
