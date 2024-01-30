FROM python:3.12-bullseye

ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

RUN pip install poetry==1.7.1

COPY . .

RUN poetry install

CMD poetry run alembic upgrade head

ENTRYPOINT ["bash", "runner.sh"]