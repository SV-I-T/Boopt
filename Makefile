dev: 
	cd ./src &uv run app.py

build:
	docker build -t boopt-dev .

test:
	docker run --env-file ./src/prod.env -p 8080:8080 boopt-dev:latest

deploy: docker-tag
	docker push us-central1-docker.pkg.dev/boopt-dev/boopt-dev/boopt

docker-tag:
	docker tag boopt-dev us-central1-docker.pkg.dev/boopt-dev/boopt-dev/boopt
