FROM python:3.8 AS builder-38

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

COPY --chown=vbuser:vbuser --from=builder-38 /tmp/dist ./dist

RUN python -m venv venv \
    && venv/bin/pip install wheel dist/* \
    && rm -rf dist

ENV PATH=/app/venv/bin:${PATH}

CMD ["bash"]


FROM python:3.9 AS builder-39

WORKDIR /tmp

COPY ./vbcore ./vbcore
COPY ./setup.py ./setup.py
COPY ./requirements ./requirements

RUN pip install wheel \
    && python setup.py bdist_wheel


FROM python:3.9-slim as vbcore-39

RUN groupadd -g 1000 vbuser \
    && useradd -m -d /app -s /bin/bash -g vbuser -u 1000 vbuser

USER vbuser

WORKDIR /app

COPY --chown=vbuser:vbuser --from=builder-39 /tmp/dist ./dist

RUN python -m venv venv \
    && venv/bin/pip install wheel dist/* \
    && rm -rf dist

ENV PATH=/app/venv/bin:${PATH}

CMD ["bash"]


FROM python:3.10 AS builder-310

WORKDIR /tmp

COPY ./vbcore ./vbcore
COPY ./setup.py ./setup.py
COPY ./requirements ./requirements

RUN pip install wheel \
    && python setup.py bdist_wheel


FROM python:3.10-slim as vbcore-310

RUN groupadd -g 1000 vbuser \
    && useradd -m -d /app -s /bin/bash -g vbuser -u 1000 vbuser

USER vbuser

WORKDIR /app

COPY --chown=vbuser:vbuser --from=builder-310 /tmp/dist ./dist

RUN python -m venv venv \
    && venv/bin/pip install wheel dist/* \
    && rm -rf dist

ENV PATH=/app/venv/bin:${PATH}

CMD ["bash"]
