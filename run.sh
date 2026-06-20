#!/usr/bin/env bash
set -e

if [[ "$(uname)" == "Darwin" ]]; then
  NIX_SHELL="/nix/var/nix/profiles/default/bin/nix-shell"
else
  NIX_SHELL="$HOME/.nix-profile/bin/nix-shell"
fi

"$NIX_SHELL" --run "python3 news_to_html.py $*"
