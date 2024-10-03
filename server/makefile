run-backup-migrations:
	poetry run alembic -x target=backup  upgrade head

create-migration-revision:
	alembic revision --autogenerate -m "default"

.ONESHELL:
create-env:
	@rm -f .env
	touch .env
	echo "POSTGRESQL_DB_URL=$$POSTGRESQL_DB_URL" >>.env
	echo "MYSQL_DB_URL=$$MYSQL_DB_URL" >>.env
	echo "ALLOWED_BOT_USERS=$$ALLOWED_BOT_USERS" >>.env
	echo "BOT_TOKEN=$$BOT_TOKEN" >>.env
	echo "SECRET_KEY=$$SECRET_KEY" >>.env
	echo "STATION_TYPE=$$STATION_TYPE" >>.env
	echo "VERSION=$$VERSION" >>.env
	echo "ENV=$$ENV" >>.env


.ONESHELL:
.PHONY: stop-server
stop-server:
	@rm -f server.err
	rm -f server.log
	SERVER_PID=$(file < .server_pid)
	if [ "$$SERVER_PID" != "" ]; then\
		kill -9 $$SERVER_PID || true;\
	else\
		echo "PID for server not found";\
	fi\

.ONESHELL:
.PHONY: start-server
start-server:
	@rm -f server.log
	rm -f server.err
	/home/admin/.local/bin/poetry run python -u -m app.main > server.log 2> server.err &
	SERVER_PID=$$!
	rm -f .server_pid
	echo "$$SERVER_PID" >>.server_pid
	echo "Server Succesfully deployed"