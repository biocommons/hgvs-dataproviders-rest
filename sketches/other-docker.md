## Another Dockerfile

FROM ubuntu:22.04
RUN apt-get update && \
    apt-get -y install python3-dev python3-pip gcc libpq-dev git
WORKDIR /app
COPY ./setup.cfg ./pyproject.toml /app/
COPY ./src/uta_restapi /app/src/uta_restapi
RUN SETUPTOOLS_SCM_PRETEND_VERSION=1 pip install -e .
RUN --mount=source=.git,target=.git,type=bind pip install -e .
WORKDIR /app/uta_restapi
CMD ["uvicorn", "restapi:app", "--host", "0.0.0.0", "--port", "8000"]

## Build time
90s
