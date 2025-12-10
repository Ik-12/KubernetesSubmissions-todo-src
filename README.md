# Exercise 4.10

## Separate source and configuration repositories

The project source and configuration are in separate repositories:

- configuration: The (old) main repository at https://github.com/Ik-12/KubernetesSubmissions
- source: New repository forked from the old one at https://github.com/Ik-12/KubernetesSubmissions-todo-src

## CI/CD Pipelines

The CI/CD pipeline is also separated between the repositories:

- CI: the source repository contains the CI process that builds the docker images and pushes them to GCP Artifact repository. In addition, it uses kustomize to set image tags on the configuration repository, and pushes changes related to this to the config repository. This automatically trigges the CD process like any other change to the configuration repository.
- CD: the configuration repository contains the CD process that deploys the project to GKE and updates the staging and production branches watched by Argo CD on the local cluster. The image tags are set in the_project/overlays/ kustomization files by the CI pipeline.
