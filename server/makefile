run-backup-migrations:
	poetry run alembic -x target=backup  upgrade head

create-migration-revision:
	alembic revision --autogenerate -m "default"

.ONESHELL:
stop-server:
	SERVER_PID=$(file < .server_pid)
	if [ "$$SERVER_PID" != "" ]; then\
		kill -9 $$SERVER_PID;\
	else\
		echo "PID for server not found";\
	fi\

.ONESHELL:
start-server:
	poetry run python -u -m app.main > server.log 2> server.err &
	SERVER_PID=$$!
	rm .server_pid
	echo "$$SERVER_PID" >>.server_pid
	echo "Server Succesfully deployed"