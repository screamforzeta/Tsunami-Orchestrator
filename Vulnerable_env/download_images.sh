#!/bin/bash

# Set the working directory to the script's location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# List of directories to execute docker compose up
dirs=(
  "vulhub/drupal/CVE-2018-7600"
  "vulhub/jenkins/CVE-2017-1000353"
  "vulhub/elasticsearch/CVE-2015-1427"
  "vulhub/activemq/CVE-2016-3088"
  "vulhub/liferay-portal/CVE-2020-7961"
)

for dir in "${dirs[@]}"; do
  if [ -d "$dir" ]; then
    echo "Executing docker compose up -d inside $dir"
    (cd "$dir" && docker compose up --no-start)
  else
    echo "Directory $dir not found, skipping to the next one..."
  fi
done
