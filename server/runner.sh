sleep 5
poetry run alembic -x target=local upgrade head
sleep 5
poetry run alembic -x target=backup upgrade head

poetry run python -m app.main
