import google.cloud.logging
import json
import logging
import os
import math
import requests

from datetime import datetime

API_KEY         = "GITHUB_API_KEY"
PR_NUMBER       = "GITHUB_PR_NUMBER"
REPO            = "GITHUB_REPO"
REPO_OWNER      = "GITHUB_REPO_OWNER"
LOG_NAME        = "DEPLOY_LOG_NAME"

API_URL = "https://api.github.com"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

def check_env_vars(vars):
  for var in vars:
    if not os.environ[var]:
      logging.exception(f"Required env var '{var}' not set")
      exit(1)

def call_github_api(url):
  headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {os.environ[API_KEY]}"
  }

  return requests.get(url, headers=headers).json()

def get_change_sets(commits):
  change_sets = []
  for commit in commits:
    metadata = {
      "message": commit["commit"]["message"],
      "author": commit["commit"]["author"]["name"],
      "timestamp": commit["commit"]["author"]["date"]
    }
    change_sets.append(metadata)

  return change_sets

def get_pull_request_data(owner, repo, pr_nbr):
  pullsUrl = f"{API_URL}/repos/{owner}/{repo}/pulls/{pr_nbr}"

  pull_request = call_github_api(pullsUrl)
  try:
    target_branch = pull_request["base"]["ref"]
  except KeyError:
    logging.exception(f"Pull request not found: {pull_request}")
    exit(2)
  time_delta = datetime.now() - datetime.strptime(pull_request["created_at"], DATE_FORMAT)

  commits = call_github_api(f"{pullsUrl}/commits")
  change_sets = get_change_sets(commits)

  return {
    "repo": repo,
    "pullRequest": pr_nbr,
    "branch": target_branch,
    "changeSets": change_sets,
    "leadTimeMinutes": math.floor(time_delta.total_seconds() / 60)
  }

def log_metrics(request):
  check_env_vars([API_KEY, REPO, REPO_OWNER])

  client = google.cloud.logging.Client()
  log_name = os.environ[LOG_NAME] if LOG_NAME in os.environ else "python_deployment_logger"
  cloud_logger = client.logger(log_name)

  owner = os.environ[REPO_OWNER]
  repo = os.environ[REPO]
  pr = os.environ[PR_NUMBER]

  build_data = get_pull_request_data(owner, repo, pr)

  print('payload='+json.dumps(build_data, indent=2, sort_keys=False))
  cloud_logger.log_struct(build_data, severity="INFO")

if __name__ == "__main__":
    log_metrics(None)
