#!/usr/bin/env bash
set -euo pipefail

patterns=(
  "__pycache__"
  "*pyc"
  ".ruff_cache"
  ".pytest_cache"
  ".mypy_cache"
)

for p in "${patterns[@]}"; do
  echo "Removing matches for pattern: $p"
  find . -name "$p" -exec rm -rf {} +
done

echo "Cleanup complete."
