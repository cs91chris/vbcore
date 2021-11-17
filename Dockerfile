FROM python:3.8 AS builder

WORKDIR /tmp

COPY ./vbcore ./vbcore
COPY ./setup.py ./setup.py
COPY ./requirements ./requirements

RUN pip install wheel \
    && python setup.py bdist_wheel


FROM python:3.8-slim as vbcore-38

RUN groupadd -g 1000 vbuser \
    && useradd -m -d /app -s /bin/bash -g vbuser -u 1000 vbuser

USER vbuser

WORKDIR /app

COPY --chown=vbuser:vbuser --from=builder /tmp/dist ./dist

RUN python -m venv venv \
    && venv/bin/pip install wheel dist/* \
    && rm -rf dist

ENV PATH=/app/venv/bin:${PATH}

CMD ["bash"]
