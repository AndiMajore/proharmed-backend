# ProHarMeD-web Backend service

Django based backend service for the ProHarMeD web-app.

## Setup

Pull all docker images from dockerhub

`docker-compose pull`

## Rebuild

Build local docker images

`docker-compose build`

## Deployment

Create containers for all images defined in docker-compose.yml file and run detached

`docker-compose up -d`

## Development hints

Show running docker containers:

`docker ps`

Follow log of selected container:

`docker logs -f $container_name`

