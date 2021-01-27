import google.cloud.logging
import json
import logging
import os
import math
import requests
import time

from datetime import datetime
from datetime import timedelta

API_KEY         = "GITHUB_API_KEY"
BRANCH          = "GITHUB_BRANCH"
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
    "Accept": "application/vnd.github.groot-preview+json",
    "Authorization": f"token {os.environ[API_KEY]}"
  }

  return requests.get(url, headers=headers).json()

def get_latest_tag(tagsUrl):
  try:
    tags = call_github_api(tagsUrl)
    return tags[1]["name"]
  except KeyError:
    logging.exception(f"Malformed response from tags: {tags}")
    exit(2)

def get_previous_release_timestamp(commitsUrl, latest_tag):
  try:
    commit = call_github_api(f"{commitsUrl}/{latest_tag}")
    return commit["commit"]["author"]["date"]
  except KeyError:
    logging.exception(f"Commit not found for {latest_tag}: {commit}")
    exit(2)

def get_all_commits(commitsUrl, branch, since):
  page = 1
  commits = call_github_api(f"{commitsUrl}?per_page=100&page={page}&sha={branch}&since={since}")
  
  while True:
    time.sleep(0.05)
    page += 1
    commit_page = call_github_api(f"{commitsUrl}?per_page=100&page={page}&sha={branch}&since={since}")
    if len(commit_page) > 0:
      commits.append(commit_page)
    else:
      break
  
  return commits

def get_commits_data(owner, repo, branch):
  tagsUrl = f"{API_URL}/repos/{owner}/{repo}/tags"
  commitsUrl = f"{API_URL}/repos/{owner}/{repo}/commits"

  latest_tag = get_latest_tag(tagsUrl)

  since = get_previous_release_timestamp(commitsUrl, latest_tag)

  commits = get_all_commits(commitsUrl, branch, since)

  pull_request_lead_times = dict()
  change_sets = []
  now = datetime.now()

  for commit in commits:
    commit_sha = commit["sha"]
    pull_requests = call_github_api(f"{API_URL}/repos/{owner}/{repo}/commits/{commit_sha}/pulls")
    for pull_request in pull_requests:
      pr_nbr = pull_request["number"]
      lead_time_minutes = math.floor((now - datetime.strptime(pull_request["created_at"], DATE_FORMAT)).total_seconds() / 60)
      pull_request_lead_times[pr_nbr] = lead_time_minutes

    metadata = {
      "message": commit["commit"]["message"],
      "author": commit["commit"]["author"]["name"],
      "timestamp": commit["commit"]["author"]["date"]
    }
    change_sets.append(metadata)
    time.sleep(0.05)

  average_lead_time_minutes = math.floor(sum(list(pull_request_lead_times.values())) / len(pull_request_lead_times))

  return {
    "repo": repo,
    "release": branch.replace("release/", ""),
    "changeSets": change_sets,
    "leadTimeMinutes": average_lead_time_minutes
  }

def log_metrics(request):
  check_env_vars([API_KEY, REPO, REPO_OWNER])

  client = google.cloud.logging.Client()
  log_name = os.environ[LOG_NAME] if LOG_NAME in os.environ else "python_deployment_logger"
  cloud_logger = client.logger(log_name)

  owner = os.environ[REPO_OWNER]
  repo = os.environ[REPO]
  branch = os.environ[BRANCH]

  build_data = get_commits_data(owner, repo, branch)

  print('payload='+json.dumps(build_data, indent=2, sort_keys=False))
  cloud_logger.log_struct(build_data, severity="INFO")

if __name__ == "__main__":
    log_metrics(None)
