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
	poetry run python server.py > server.log 2> server.err &
	SERVER_PID=$$!
	rm -f .server_pid
	echo "$$SERVER_PID" >>.server_pid
	echo "Server Succesfully deployed"