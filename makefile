local-prod:
	docker-compose --env-file=.docker.env up

local-dev:
	docker-compose --env-file=.docker.env --profile dev up

local-dev-build:
	docker-compose --env-file=.docker.env --profile dev up --build


local-prod-build:
	docker-compose --env-file=.docker.env up --build
