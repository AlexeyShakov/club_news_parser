FROM python:3.10

RUN mkdir /parser_app

WORKDIR  /parser_app

COPY requirements.txt /parser_app

ENV PYTHONUNBUFFERED 1

RUN apt update && apt install -y gettext
RUN pip install --upgrade pip

RUN pip install -r /parser_app/requirements.txt

COPY . .

RUN pip install -e ./services/grpc_translations/




