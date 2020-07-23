FROM python:3.7-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    cmake \
    build-essential \
    gcc \
    curl \
    g++

RUN curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs

WORKDIR /frontend
COPY ./frontend /frontend

RUN npm run build

WORKDIR /app

COPY ./app/requirements.txt /app
RUN pip install -r requirements.txt

COPY /app /app

CMD gunicorn --bind 0.0.0.0:$PORT wsgi 