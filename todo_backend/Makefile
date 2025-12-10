ifndef TAG
$(error TAG is not set. Usage: make <target> TAG=x.y)
endif

DOCKER_BUILDER = docker

todo_backend_image := docker.io/iku1/todo_backend:$(TAG)

.PHONY: log_reader_api
log_reader_api: 
	$(DOCKER_BUILDER) build --platform linux/amd64 -t $(todo_backend_image) .
	$(DOCKER_BUILDER) push $(todo_backend_image)
