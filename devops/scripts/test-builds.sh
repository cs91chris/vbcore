#!/bin/bash

if [[ -z "${1}" ]]; then
	echo "missing image name argument!"
	exit 1
fi

testing_build() {
	local image_name=${1}
	echo -e "testing build: ${image_name}"
	docker run --rm "${image_name}" version
}

testing_build "${1}"
