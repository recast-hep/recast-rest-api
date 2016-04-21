FROM python:2.7

# Copy source code
WORKDIR /recast-rest-api
COPY . /recast-rest-api/

RUN pip install -e . --process-dependency-links

# Add user
RUN groupadd -r recast && useradd -r -g recast recast

EXPOSE 5000
USER recast

CMD ["recast-api", "server"]