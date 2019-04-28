FROM alpine:3.7


WORKDIR /users

COPY . /users

RUN apk add --update \
    python2 \
    python-dev \
    py-pip \
    build-base \
    && pip install --upgrade pip \
    && pip install -r requirements.txt


EXPOSE 80 8080


CMD ["python", "users.py"]

ARG buildtime_variable=default_value
ENV TEAM_ID=$buildtime_variable
