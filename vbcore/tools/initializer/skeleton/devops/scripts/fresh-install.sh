#!/bin/bash

python -m venv venv
venv/bin/pip install wheel dist/*.whl
