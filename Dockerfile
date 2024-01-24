FROM python:3.8.5-alpine3.12

RUN apk add --no-cache bash
RUN apk add build-base
RUN apk add --update musl-dev gcc libffi-dev python3-dev

RUN mkdir /app
WORKDIR /app

EXPOSE 8000

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT gunicorn -w 4 -b:8000 --access-logfile '-' app:app
