FROM python:3.10 AS builder

COPY . /app

WORKDIR /app

COPY ./devops/scripts/build.sh ./build.sh
COPY ./devops/scripts/fresh-install.sh ./install.sh

RUN bash build.sh
RUN bash install.sh


FROM python:3.10-slim as zengine

RUN groupadd -g 1000 vbuser \
    && useradd -m -d /app -s /bin/bash -g vbuser -u 1000 vbuser

USER vbuser

WORKDIR /app

COPY --chown=vbuser:vbuser --from=builder /app/venv /app/venv

ENV PATH=/app/venv/bin:${PATH}

ENTRYPOINT ["{skeleton}"]
