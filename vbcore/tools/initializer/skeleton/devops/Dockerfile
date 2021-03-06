FROM python:3.9 AS builder

WORKDIR /tmp

COPY ./{skeleton} ./{skeleton}
COPY ./setup.py ./setup.py
COPY ./requirements ./requirements
COPY ./devops/scripts/build.sh ./build.sh

RUN bash build.sh


FROM python:3.9-slim as {skeleton}

RUN groupadd -g 1000 vbuser \
    && useradd -m -d /app -s /bin/bash -g vbuser -u 1000 vbuser

USER vbuser

WORKDIR /app

COPY --chown=vbuser:vbuser --from=builder /tmp/dist ./dist
COPY ./devops/scripts/fresh-install.sh /tmp/install.sh

RUN bash /tmp/install.sh && rm -rf dist

ENV PATH=/app/venv/bin:${PATH}

CMD ["bash"]
ENTRYPOINT ["{skeleton}"]
