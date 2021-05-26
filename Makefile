#!make

# Config can be parametrized, example: `make config=".env.prod" run`
config ?= .env
include $(config)
export $(shell sed 's/=.*//' $(config))

build:
	docker-compose build

build-nc:
	docker-compose build --no-cache

volume:
	docker volume create --name=links-references-prediction-data

run: build volume
	docker-compose -p ${APP_NAME} up

crawl: build volume
	docker run --rm --env-file ./${config} \
		--name ${APP_NAME}-crawl \
		-p 4040:4040 \
		-v links-references-prediction-data:/workspace/data \
		links-references-prediction \
		spark-submit \
		--conf "spark.driver.cores=${SPARK_DRIVER_CORES}" \
		--conf "spark.driver.memory=${SPARK_DRIVER_MEMORY}" \
		src/scripts/crawl.py -u $(URLS) -d $(DEPTH)

train: build volume
	docker run --rm --env-file ./${config} \
		--name ${APP_NAME}-train \
		-p 4040:4040 \
		-v links-references-prediction-data:/workspace/data \
		links-references-prediction \
		spark-submit \
		--conf "spark.driver.cores=${SPARK_DRIVER_CORES}" \
		--conf "spark.driver.memory=${SPARK_DRIVER_MEMORY}" \
		src/scripts/train.py \
		-n ${RF_NUM_TREES} \
		-d ${RF_MAX_DEPTH}

test: build
	docker run -it --rm --env-file=./$(config) \
		--name $(APP_NAME)-test \
		-p 4040:4040 \
		links-references-prediction \
		 pytest -sv

# bash for debugging
bash: build
	docker run -it --rm --env-file ./${config} \
		--name ${APP_NAME}-bash \
		-v links-references-prediction-data:/workspace/data \
		links-references-prediction \
		bash
