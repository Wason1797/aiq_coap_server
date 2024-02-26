FROM python:3.12-bookworm

ENV PYTHONUNBUFFERED=1

RUN apt-get install build-essential libssl-dev libffi-dev \
    python3-dev cargo pkg-config

RUN pip install poetry==1.7.1

COPY . .

RUN poetry install

CMD poetry run alembic upgrade head

ENTRYPOINT ["bash", "runner.sh"]