# hgvs-dataproviders-rest

This package exposes UTA and SeqRepo data through a REST API and provides an hgvs-compatible client.

## Run the API

Build and start the container from the repository root:

```sh
docker build -t hgvs-dataproviders-rest .
docker run --rm -p 8000:8000 hgvs-dataproviders-rest
```

The API listens on port 8000. Its OpenAPI schema and interactive docs are available at `/openapi.json` and `/docs`.

For a local development server, install the development environment with `make devready`, then run:

```sh
uv run uvicorn hgvs_dataproviders_rest.restapi:app --reload
```

## Connect from hgvs

The client defaults to the hosted service. Set `UTAREST_URL` to use another service, such as a local API:

```sh
export UTAREST_URL=http://localhost:8000
```

Then use the provider through the package's public API:

```python
import hgvs_dataproviders_rest

hdp = hgvs_dataproviders_rest.connect()
```
