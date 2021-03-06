#!/bin/bash

if [[ -n "${REPO_URL}" ]]; then
	REPO_OPTS="--repository-url ${REPO_URL}"
fi

TWINE_OPTS="--verbose --skip-existing --non-interactive"

# upload to gitlab
# shellcheck disable=SC2086
twine upload ${TWINE_OPTS} ${REPO_OPTS} dist/*
