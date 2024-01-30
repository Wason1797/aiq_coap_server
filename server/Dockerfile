FROM python:3.12-bookworm

ENV PYTHONUNBUFFERED=1

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable
ENV PATH="/root/.cargo/bin:$PATH"

RUN pip install poetry==1.7.1

COPY . .

RUN poetry install

CMD poetry run alembic upgrade head

ENTRYPOINT ["bash", "runner.sh"]