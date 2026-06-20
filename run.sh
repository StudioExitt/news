#!/usr/bin/env bash
set -e
~/.nix-profile/bin/nix-shell --run "python3 news_to_html.py $*"
