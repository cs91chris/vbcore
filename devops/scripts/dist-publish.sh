#!/bin/bash

if [[ -n "${REPO_URL}" ]]; then
	REPO_OPTS="--repository-url ${REPO_URL}"
fi

# shellcheck disable=SC2086
twine upload --verbose --skip-existing --non-interactive ${REPO_OPTS} dist/*
