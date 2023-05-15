#!/bin/bash

pip install -r requirements/requirements-build.txt

python setup.py sdist bdist_wheel
