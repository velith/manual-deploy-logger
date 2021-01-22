# Deploy logger for performance metrics

This repo contains a Github action that logs performance metrics to Google Stackdiver during a deployment workflow. The metrics are deployment frequency and change lead time.

## How it works

It assumes that you are using Github Pull Requests. Use the action during an automated workflow when a pull request is merged. In Stackdriver the logs will have the `resource.type` set to "global".

## Inputs

### `github_api_key`

**Required** The access token to use for calling the Github API. The token must have access to read your repository.

### `github_pull_number`

**Required** The number ID of the pull request that was merged. This can easily be retrieved using the github context `github.event.number`.

### `gcp_sa_key`

**Required** A service account key to use for posting logs to a GCP repository. The project for which the service account belongs to will be used when posting logs.

### `log_name`

**Optional** Name of the log in Google Stackdriver. If not provided it will be named `projects/[GCP_PROJECT]/logs/python_deployment_logger`.

## Example Usage

    uses: velith/deploy-logger@master
    with:
      github_api_key: ${{ secrets.GH_API_KEY }}
      github_pull_number: ${{ github.event.number }}
      gcp_sa_key: ${{ secrets.GCP_SA_KEY }}