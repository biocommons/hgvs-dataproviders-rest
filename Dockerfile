FROM ubuntu:22.04
RUN apt-get update && \
    apt-get -y install python3-dev python3-pip gcc libpq-dev

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src/hgvs_dataproviders_rest ./hgvs_dataproviders_rest
CMD ["uvicorn", "hgvs_dataproviders_rest.restapi:app", "--host", "0.0.0.0", "--port", "8000"]