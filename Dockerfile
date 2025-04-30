# hadolint ignore=DL3007
FROM nikolaik/python-nodejs:latest

ENV DEBIAN_FRONTEND noninteractive

# hadolint ignore=DL3008
RUN apt-get update \
  && apt-get upgrade -y \
  && apt-get install -y --no-install-recommends \
    python3-pip \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /
COPY --chown=circleci:circleci bin bin

# hadolint ignore=DL3059,DL3013
RUN pip3 install --no-cache-dir -U bochord
CMD ["bochord", "-h"]
