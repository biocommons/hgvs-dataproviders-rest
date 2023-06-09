FROM ubuntu:22.04
RUN apt-get update && \
    apt-get -y install python3-dev python3-pip gcc libpq-dev

WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r /app/requirements.txt
COPY ./src/uta_restapi /app/uta_restapi
WORKDIR /app/uta_restapi
CMD ["uvicorn", "restapi:app", "--host", "0.0.0.0", "--port", "8000"]