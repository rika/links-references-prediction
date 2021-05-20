# Config can be parametrized, example: `make config="config.prod" run`

config ?= config.dev
include $(config)
export $(shell sed 's/=.*//' $(config))

build:
	docker build -t $(APP_NAME) .

build-nc:
	docker build --no-cache -t $(APP_NAME) .

test: build
	docker run  -it --rm --env-file=./$(config) --name="$(APP_NAME)" $(APP_NAME) pytest

test-local:
	pytest
