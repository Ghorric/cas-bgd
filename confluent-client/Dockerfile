FROM python:3.7-slim

RUN apt-get update
RUN apt install -y vim redis-tools iputils-ping procps wget curl jq kafkacat

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -U -r /tmp/requirements.txt

RUN useradd -rm -d /home/appuser -s /bin/bash -g root -G sudo -u 1001 appuser
RUN chown -R appuser:root /home/appuser
RUN chmod -R 755 /home/appuser

USER appuser
WORKDIR /home/appuser

COPY common ./common
COPY mapstore ./mapstore
COPY streaming ./streaming
COPY *.py .

ENV REDIS_HOST 127.0.0.1
ENV REDIS_PORT 6379

ENV PYTHONPATH "${PYTHONPATH}:/home/appuser"