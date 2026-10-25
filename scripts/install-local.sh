#!/usr/bin/env bash
# Build, install and de-duplicate the theme for VSCodium.
# Stale version folders keep registering the same "Leylah Void" label, which
# makes the editor load an old palette. This removes them after installing.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/build-vsix.py

version=$(python3 -c "import json; print(json.load(open('package.json'))['version'])")
ext_dir="${HOME}/.vscode-oss/extensions"
vsix="dist/leylah-void-${version}.vsix"

codium --install-extension "$vsix" --force

for dir in "${ext_dir}/pushkar7270.leylah-void-"*; do
  [ -d "$dir" ] || continue
  if [ "$(basename "$dir")" != "pushkar7270.leylah-void-${version}" ]; then
    echo "removing stale $(basename "$dir")"
    rm -rf "$dir"
  fi
done

echo "installed ${version} - reload the window (Ctrl+Shift+P -> Developer: Reload Window)"
