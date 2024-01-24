ENV=local
include ./secrets/$(ENV)/.env
APP_NAME=jentis_tt

ifeq ($(ENV), prod)
	DOMAIN=$(BASE_DOMAIN)
else
	DOMAIN=$(ENV).$(BASE_DOMAIN)
endif

use_secrets:
	cp ./secrets/$(ENV)/.env ./.

down:
	docker-compose down

build: use_secrets
	docker-compose build && docker image prune -f

up: build
	docker-compose up -d

unit:
	pytest tests_unit

integration: up
	docker-compose exec -T backend pytest -s --cov-report term-missing --cov=. ./tests_integration/

deploy: build
	docker save --output ./deploy/files/app $(APP_NAME):latest
	docker save --output ./deploy/files/background $(APP_NAME)_background:latest
	ansible-playbook -i deploy/inventory/$(ENV) deploy/tasks/deploy.yml --extra-vars "server_username=$(SERVER_USERNAME) domain=$(DOMAIN)
	rm ./deploy/files/app
	rm ./deploy/files/background

setup_infrastructure:
	ansible-playbook -i deploy/inventory/$(ENV) deploy/tasks/setup_infrastructure.yml --extra-vars "email=$(EMAIL) server_username=$(SERVER_USERNAME) domain=$(DOMAIN)"
