FROM cimg/python:3.13-node

ENV DEBIAN_FRONTEND noninteractive

USER root
# hadolint ignore=DL3008
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    git \
    rsync \
    shellcheck \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN chown circleci:circleci /app
COPY --chown=circleci:circleci bin bin

USER circleci
COPY --chown=circleci:circleci pyproject.toml poetry.lock ./
# hadolint ignore=DL3013
RUN pip3 install --no-cache-dir poetry
# hadolint ignore=DL3016,DL3059
COPY --chown=circleci:circleci package.json package-lock.json ./
RUN npm install

COPY --chown=circleci:circleci . .
RUN mkdir -p test-results dist

# Install
# hadolint ignore=DL3059
RUN poetry install
