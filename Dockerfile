FROM python:3.8-slim

WORKDIR /app

COPY ./requirements.txt /app/

RUN apt update && apt install --no-install-recommends -y \
        tini &&\
    rm -rf /var/lib/apt/lists/* &&\
    pip install --upgrade pip setuptools wheel &&\
    pip install --no-cache-dir -r requirements.txt &&\
    rm -rf requirements.txt

ENTRYPOINT ["/usr/bin/tini", "--", "flask", "run", "--host=0.0.0.0", "--port=5000", "--reload"]
