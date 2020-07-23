FROM python:3.7-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        cmake \
        build-essential \
        gcc \
        g++ 

COPY ./app/requirements.txt /app
RUN pip install -r requirements.txt

COPY /app /app
COPY /frontend/build /frontend/build

CMD gunicorn --bind 0.0.0.0:$PORT wsgi 