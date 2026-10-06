#!/usr/bin/env bash
# Merge freshly parsed GPS files (work/new) into the TopRate repo's data/gps (one parquet per file per year) and push.
# Used by TopRate's gps_daily.yml and this repo's gps_backfill.yml. Needs a TopRate checkout at $TOPRATE_DIR (default: toprate) with push rights.
# The first run seeds data/gps from the data store (pipeline/gps_repo.py).
set -euo pipefail
top="${TOPRATE_DIR:-toprate}"
mkdir -p work/new
python pipeline/gps_repo.py update "$top" work/new

cd "$top"
git config user.name "racing-model bot"
git config user.email "racing-model-bot@users.noreply.github.com"
git add data/gps
git diff --cached --quiet && { echo "GPS: no change"; exit 0; }
git commit -q -m "GPS sectionals $(TZ=Australia/Melbourne date +%F\ %H:%M)"
for i in 1 2 3 4 5; do
  git pull -q --rebase origin main && git push -q origin HEAD:main && exit 0
  sleep $((i * 10))
done
exit 1
