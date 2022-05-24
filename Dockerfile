# pull official base image
# FROM python:3.9.6-buster as builder
FROM python:3.8-slim as builder

# Name of creator of docker image
LABEL MAINTAINER Rajesh Jatav
  
# set working directory
WORKDIR /ingestion-service

# Install dependencies
COPY requirements.txt /ingestion-service/requirements.txt
RUN pip install -r /ingestion-service/requirements.txt

# add app
COPY . /ingestion-service

# Start the second step build
# FROM python:3.9.6-slim-buster
FROM python:3.8-slim 


# COPY data from buider image to anither build image
COPY --from=builder /usr/local /usr/local
COPY --from=builder /ingestion-service /ingestion-service

# Set the working directory
WORKDIR /ingestion-service

# Environment path
ENV PATH=/usr/local:$PATH

# Add username and group for slim image
RUN groupadd -r -g 1000 docker \
    && useradd -u 1000 -r -g docker --shell /bin/bash --create-home docker \
    && mkdir -p /weav-data \
    && mkdir -p /weav-data/ingestion-raw-files \
    && mkdir -p /weav-data/uploaded-raw-files \
    && chown -R docker:docker /weav-data \
    && chmod -R 777 /ingestion-service


VOLUME /weav-data
EXPOSE 7002

# Switch to 'docker'
USER docker

# run server
CMD python -u manage.py run -h 0.0.0.0