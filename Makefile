all:
	"./.venv/Scripts/activate"& cd ./src& python ./app.py

build:
	docker build -t vela-lite .

test:
	docker run --env-file ./src/prod.env -p 8080:8080 vela-lite:latest

tag:
	docker tag vela-lite us-central1-docker.pkg.dev/boopt-dev/boopt-dev/vela-lite

push:
	docker push us-central1-docker.pkg.dev/boopt-dev/boopt-dev/vela-lite