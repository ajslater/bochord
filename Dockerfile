FROM nikolaik/python-nodejs:python3.15-nodejs26

# Lint tools devenv's bin/ scripts run, unpinned on purpose.
COPY --from=koalaman/shellcheck:stable /bin/shellcheck /usr/local/bin/
COPY --from=mvdan/shfmt:latest /bin/shfmt /usr/local/bin/
COPY --from=hadolint/hadolint:latest /bin/hadolint /usr/local/bin/
COPY --from=rhysd/actionlint:latest /usr/local/bin/actionlint /usr/local/bin/
COPY --from=ghcr.io/reteps/dockerfmt:latest /ko-app/dockerfmt /usr/local/bin/
ADD https://github.com/anordal/shellharden/releases/latest/download/shellharden-x86_64-unknown-linux-musl.tar.gz /tmp/shellharden.tar.gz
RUN tar -xzf /tmp/shellharden.tar.gz -C /usr/local/bin shellharden && rm /tmp/shellharden.tar.gz

WORKDIR /app

COPY . .
RUN mkdir -p test-results dist

# Install
# hadolint ignore=DL3059
RUN uv sync --all-groups --all-extras