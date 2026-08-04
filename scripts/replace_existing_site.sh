#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${1:-}"

if [[ -z "$TARGET_DIR" ]]; then
  echo "Usage: bash scripts/replace_existing_site.sh /path/to/mhnamdar.github.io"
  exit 1
fi
if [[ ! -d "$TARGET_DIR/.git" ]]; then
  echo "Error: $TARGET_DIR is not a Git repository."
  exit 1
fi
if [[ -n "$(git -C "$TARGET_DIR" status --porcelain)" ]]; then
  echo "Error: the target repository has uncommitted changes. Commit or stash them first."
  exit 1
fi

CURRENT_BRANCH="$(git -C "$TARGET_DIR" branch --show-current)"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_BRANCH="archive-before-redesign-$STAMP"

echo "Creating local backup branch: $BACKUP_BRANCH"
git -C "$TARGET_DIR" branch "$BACKUP_BRANCH"

echo "Replacing old site files while preserving .git …"
rsync -a --delete \
  --exclude='.git/' \
  --exclude='dist/' \
  --exclude='previews/' \
  --exclude='__pycache__/' \
  "$SOURCE_DIR/" "$TARGET_DIR/"

cd "$TARGET_DIR"
python3 scripts/check.py
python3 scripts/build.py

echo
echo "Done. Review the site locally with:"
echo "  python3 scripts/dev.py"
echo
echo "Then publish with:"
echo "  git add -A"
echo "  git commit -m 'Launch redesigned academic website'"
echo "  git push origin $CURRENT_BRANCH"
echo
echo "Optional: preserve the backup remotely:"
echo "  git push origin $BACKUP_BRANCH"
