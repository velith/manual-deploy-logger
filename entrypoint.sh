#!/usr/bin/env bash

if [ -n "${INPUT_GITHUB_API_KEY}" ]; then
  export GITHUB_API_KEY="${INPUT_GITHUB_API_KEY}"
else
  echo "Input github_api_key cannot be empty"
  exit 1
fi

if [ -n "${INPUT_GCP_SA_KEY}" ]; then
  echo "${INPUT_GCP_SA_KEY}" > /opt/gcp_key.json
  export GOOGLE_APPLICATION_CREDENTIALS=/opt/gcp_key.json
else
  echo "Input gcp_sa_key cannot be empty"
  exit 1
fi

if [ -z "${GITHUB_REPOSITORY}" ]; then
  echo "env GITHUB_REPOSITORY cannot be empty"
  exit 1
fi

if [ "${INPUT_LOG_NAME}" != "" ]; then
  export DEPLOY_LOG_NAME="${INPUT_LOG_NAME}"
fi
export GITHUB_PR_NUMBER="${INPUT_GITHUB_PULL_NUMBER}"
export GITHUB_REPO="${GITHUB_REPOSITORY##*/}"
export GITHUB_REPO_OWNER="${GITHUB_REPOSITORY%%/*}"

output=$(python /code/src/logger.py ${*} 2>&1)
exitCode=${?}

echo "${output}"
exit ${exitCode}