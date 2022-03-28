#!/bin/sh

print_usage() {
    printf "Usage %s [pending|success|failure|error]" "$(basename "$0")"
    printf "Required environment variables:"
    printf "\t- GIT_URL"
    printf "\t- GIT_COMMIT"
    printf "\t- BUILD_URL"
    printf "\t- GITHUB_USER"
    printf "\t- GITHUB_TOKEN"
}

github_state_data() {
    printf '{
    "state": "%s",
    "description": "Jenkins",
    "target_url": "%s/console",
    "context": "continuous-integration/jenkins"
}' "${1}" "${2}"
}

BUILD_STATE=${1}

case ${BUILD_STATE} in
pending | success | failure | error) ;;
-h | help) print_usage ;;
*)
    print_usage
    exit 1
    ;;
esac

[ -z "${GIT_URL}" ] && print_usage
[ -z "${GIT_COMMIT}" ] && print_usage
[ -z "${BUILD_URL}" ] && print_usage
[ -z "${GITHUB_USER}" ] && print_usage
[ -z "${GITHUB_TOKEN}" ] && print_usage

GITHUB_OWNER_REPO=$(echo "${GIT_URL}" | sed 's/.*github.com.//;s/\.git$//;')

curl -X POST -s -o /dev/null \
    -u "${GITHUB_USER}:${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/${GITHUB_OWNER_REPO}/statuses/${GIT_COMMIT}" \
    -d "$(github_state_data "${BUILD_STATE}" "${BUILD_URL}")"
