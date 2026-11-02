FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN apt-get update && \
	apt-get install --no-install-recommends -y build-essential libpq-dev && \
	rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --extra server --no-dev --no-install-project

FROM python:3.12-slim
RUN apt-get update && \
	apt-get install --no-install-recommends -y libpq5 && \
	rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=build /app/.venv /app/.venv
COPY src/hgvs_dataproviders_rest ./hgvs_dataproviders_rest
ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "hgvs_dataproviders_rest.restapi:app", "--host", "0.0.0.0", "--port", "8000"]
