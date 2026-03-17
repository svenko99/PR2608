#!/bin/bash
set -euo pipefail

REPO_DIR="/home/sven/Dev/PR268"
SRC_DIR="$REPO_DIR/src"
LOG_FILE="$REPO_DIR/cron.log"

cd "$SRC_DIR"

# Zaženi scraper in shrani izhod
OUTPUT=$(uv run python main.py 2>&1) || {
    echo "[$(date)] NAPAKA pri scrapanju:" >> "$LOG_FILE"
    echo "$OUTPUT" >> "$LOG_FILE"
    exit 1
}

echo "[$(date)] Uspešno:" >> "$LOG_FILE"
echo "$OUTPUT" >> "$LOG_FILE"

# Zadnje tri vrstice so commit message
COMMIT_MSG=$(echo "$OUTPUT" | tail -n 3)

cd "$REPO_DIR"
git pull --rebase
git add data/data.csv data/changes.csv
git commit -m "$COMMIT_MSG"
git push
