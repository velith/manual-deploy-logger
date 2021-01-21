#!/usr/bin/env bash

if [ -n "${GITHUB_API_KEY}" ]; then
  export GITHUB_API_KEY="${GITHUB_API_KEY}"
else
  echo "Input github_api_key cannot be empty"
  exit 1
fi

if [ -n "${GCP_SA_KEY}" ]; then
  echo "${GCP_SA_KEY}" > /opt/gcp_key.json
  export GOOGLE_APPLICATION_CREDENTIALS=/opt/gcp_key.json
else
  echo "Input gcp_sa_key cannot be empty"
  exit 1
fi

if [ -z "${GITHUB_REPOSITORY}" ]; then
  echo "env GITHUB_REPOSITORY cannot be empty"
  exit 1
fi

if [ "${LOG_NAME}" != "" ]; then
  export DEPLOY_LOG_NAME="${LOG_NAME}"
fi
export GITHUB_PR_NUMBER="${GITHUB_PULL_NUMBER}"
export GITHUB_REPO="${GITHUB_REPOSITORY##*/}"
export GITHUB_REPO_OWNER="${GITHUB_REPOSITORY%%/*}"

output=$(python logger.py ${*} 2>&1)
exitCode=${?}

echo "${output}"
exit ${exitCode}