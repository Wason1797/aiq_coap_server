poetry run alembic upgrade head
sleep 5

poetry run python -m app.main