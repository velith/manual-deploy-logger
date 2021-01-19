# Deploy logger for performance metrics

This repo contains a function that logs performance metrics to Google Stackdiver during a deployment. The metrics are deployment frequency and change lead time.

## How it works

It assumes that you are using Github Pull Requests. Call the script `logger.py` during your automated pipeline that is triggered when a pull request is merged. Some environment variables has to be set for it to work

    GITHUB_API_KEY       # A provided access token to use for calling Gitub API
    GITHUB_PR_NUMBER     # The pull request number for the PR that was merged
    GITHUB_REPO          # Name of the Github repository
    GITHUB_REPO_OWNER    # Owner/Org of the repository
    DEPLOY_LOG_NAME      # Optional name for the logger

For the log to Stackdriver to work you need to have an environment during the build that has `gcloud` CLI tool set up with a GCP project you wish to send the logs to. Also need credentials for a service account that are allowed to post logs.