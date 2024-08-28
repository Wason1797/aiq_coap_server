sleep 5
poetry run alembic upgrade head -x target=local
sleep 5
poetry run alembic upgrade head -x target=backup

poetry run python -m app.main