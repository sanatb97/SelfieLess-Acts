docker system prune -a
docker image ls
docker container ls
docker container stop <containerID>
docker container rm <containerID>
docker pull mvertes/alpine-mongo
docker run -d --name mongo -p 27017:27017 mvertes/alpine-mongo
docker network inspect bridge
docker build --tag=users --build-arg buildtime_variable=CC_319_339_340_367 .
docker run -p 8080:80 users
docker build --tag=acts --build-arg buildtime_variable=CC_319_339_340_367 .
docker run -p 8000:80 acts