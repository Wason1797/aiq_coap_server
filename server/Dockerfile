FROM ubuntu:22.04 as base

ENV PYTHONUNBUFFERED=1

RUN apt update && apt upgrade -y && apt-get install software-properties-common -y && add-apt-repository ppa:deadsnakes/ppa

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install python3.11-full build-essential libssl-dev libffi-dev \
    python3.11-dev python3-pip cargo pkg-config -y


RUN pip3 install --upgrade pip
RUN pip3 install poetry==1.7.1

FROM base

COPY . .

RUN poetry install --only main


ENTRYPOINT ["bash", "runner.sh"]