#!/usr/bin/env bash
set -eu
cd -- "$(dirname -- "$0")"
bash ./install.sh
printf '\nPress Return to close this window...'
read -r _
