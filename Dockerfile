# syntax=docker/dockerfile:1

FROM python:3.10.2-buster

WORKDIR /app
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./app .

CMD ["flask", "run"]