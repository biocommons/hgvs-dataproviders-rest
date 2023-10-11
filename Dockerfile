# docker build . -t biocommons/hgvs-dataproviders-rest:0.0.2

FROM ubuntu:22.04
RUN apt-get update && \
    apt-get -y install python3-dev python3-pip gcc libpq-dev

WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r /app/requirements.txt
COPY ./src/hgvs_dataproviders_rest /app/hgvs_dataproviders_rest
WORKDIR /app/hgvs_dataproviders_rest
CMD ["uvicorn", "restapi:app", "--host", "0.0.0.0", "--port", "8000"]
