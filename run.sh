#!/usr/bin/env bash
set -e
nix-shell --run "python3 news_to_html.py $*"

deploy.sh
