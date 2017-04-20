FROM python:2.7
WORKDIR /recast-rest-api
COPY . /recast-rest-api/
RUN pip install -e . --process-dependency-links
