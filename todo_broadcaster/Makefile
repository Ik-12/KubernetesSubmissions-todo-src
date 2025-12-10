ifndef TAG
$(error TAG is not set. Usage: make <target> TAG=x.y)
endif

DOCKER_BUILDER = docker

image := docker.io/iku1/todo_broadcaster:$(TAG)

.PHONY: docker_image
docker_image: 
	$(DOCKER_BUILDER) build --platform linux/amd64 -t $(image) .
	$(DOCKER_BUILDER) push $(image)
