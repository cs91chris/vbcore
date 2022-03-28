#!/bin/bash

PYVER=39
PACKAGE="vbcore"
IMAGE_NAME="voidbrain/${PACKAGE}"
VERSION="$(shell grep 'current_version' .bumpversion.cfg | sed 's/^[^=]*= *//')"


testing_build() {
    local tag=${1}
    echo -e "testing build: ${IMAGE_NAME}:${tag}"
    docker run -it --rm "${IMAGE_NAME}:${tag}" ${PACKAGE} version
}


testing_build "${VERSION}-py${PYVER}"
