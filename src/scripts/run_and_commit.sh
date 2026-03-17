#!/bin/bash
set -euo pipefail
REPO_DIR="/home/sven/Dev/PR268"
SRC_DIR="$REPO_DIR/src"
LOG_FILE="$REPO_DIR/cron.log"

# Pull pred scraperjem
cd "$REPO_DIR"
git pull --rebase

cd "$SRC_DIR"
OUTPUT=$(/home/sven/.local/bin/uv run python main.py 2>&1) || {
    echo "[$(date)] NAPAKA pri scrapanju:" >> "$LOG_FILE"
    echo "$OUTPUT" >> "$LOG_FILE"
    exit 1
}
echo "[$(date)] Uspešno:" >> "$LOG_FILE"
echo "$OUTPUT" >> "$LOG_FILE"

COMMIT_MSG=$(echo "$OUTPUT" | tail -n 3)
cd "$REPO_DIR"
git add data/data.csv data/changes.csv
git commit -m "$COMMIT_MSG"
git push
