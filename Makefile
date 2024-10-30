export project   = titan
export env       = prod
export service   = api
domain           = api.punkerside.io
aws_route53_zone = punkerside.io

export AWS_DEFAULT_REGION=us-east-1
export DOCKER_BUILDKIT=0

DOCKER_UID  = $(shell id -u)
DOCKER_GID  = $(shell id -g)
DOCKER_USER = $(shell whoami)

base:
	docker build -t ${project}-${env}-${service}:build -f Dockerfile .

up:
	@docker compose up

down:
	@docker compose down

init:
	cd terraform/ && terraform init -backend-config=config.remote.tfbackend

apply:
	cd terraform/ && terraform apply -var="project=${project}" -var="env=${env}" -var="service=${service}"