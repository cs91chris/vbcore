#!/bin/sh

SONAR_SCANNER_IMAGE="sonarsource/sonar-scanner-cli"

docker run --rm \
    -v "${PWD}:${PWD}" \
    -e SONAR_SCANNER_OPTS="${SONAR_SCANNER_OPTS}" \
    -e SONAR_HOST_URL="${SONAR_HOST_URL}" \
    ${SONAR_SCANNER_IMAGE} \
    -D sonar.projectBaseDir="${PWD}" \
    -D sonar.projectVersion="${VERSION}" \
    -D sonar.login="${SONAR_LOGIN}"
