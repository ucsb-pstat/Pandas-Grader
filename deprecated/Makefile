placeholder:
	@echo "You can't run make by itself, pass in a target"

build:
	docker build --no-cache -t wwhuang/jhub-gofer -f Worker.Dockerfile .

push: build
	docker push wwhuang/jhub-gofer:latest

format:
	isort *.py
	black .
