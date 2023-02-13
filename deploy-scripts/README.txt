Make sure you run all of these scripts from the Team3 directory so the references are correct

initializeCD - builds the main and proxy server containers
deploy - Runs the main server container (no build)
deploy_canary - Runs the proxy server with a main and canary server
release_abort - Reverts the server back to using the old main server
release_approve - Replaces the main server with the canary then runs 'deploy'

Running deploy or deploy_canary will remove and replace the currently running containers