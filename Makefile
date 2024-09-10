all:
	uv run ./src/app.py

build:
	docker build -t boopt-dev .

test:
	docker run --env-file ./src/prod.env -p 8080:8080 boopt-dev:latest

tag:
	docker tag boopt-dev us-central1-docker.pkg.dev/boopt-dev/boopt-dev/boopt

push:
	docker push us-central1-docker.pkg.dev/boopt-dev/boopt-dev/boopt