FROM debian:bullseye as base

ENV PYTHONUNBUFFERED=1

RUN apt update && apt upgrade -y && \
apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev

RUN wget https://www.python.org/ftp/python/3.11.8/Python-3.11.8.tgz && \
tar -xvf Python-3.11.8.tgz

RUN cd Python-3.11.8 && ./configure --enable-optimizations && make -j 2 && make altinstall
RUN apt-get install -y python3-pip


RUN pip3 install --upgrade pip
RUN pip3 install poetry==1.8.1

FROM base

COPY . .

RUN poetry install --only main

EXPOSE 5683/udp

ENTRYPOINT ["bash", "runner.sh"]