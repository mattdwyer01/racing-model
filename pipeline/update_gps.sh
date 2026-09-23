#!/usr/bin/env bash
# Merge freshly parsed GPS files (work/new) into the stored copies and upload them.
# Used by both the daily and backfill workflows. Needs GITHUB_TOKEN + GITHUB_REPOSITORY.
set -euo pipefail
mkdir -p store work/new

declare -A KEYS=(
  [rq_gps_runs]="race_code,tab_no"
  [rq_gps_sections]="race_code,tab_no,cum_dist_m"
  [rc_gps_runs]="meet_code,race_no,tab_no"
  [rc_gps_sections]="meet_code,race_no,tab_no,from_m"
)

summary="${GITHUB_STEP_SUMMARY:-/dev/null}"
echo "| file | rows |" >> "$summary"; echo "|---|---|" >> "$summary"

for f in "${!KEYS[@]}"; do
  new=( work/new/$f.parquet work/new/*/$f.parquet )
  have_new=false
  for n in "${new[@]}"; do [ -s "$n" ] && have_new=true; done
  if ! $have_new; then echo "$f: no new rows"; continue; fi
  python pipeline/store.py get "$f.parquet" "store/$f.parquet"
  python pipeline/merge.py "store/$f.parquet" "${KEYS[$f]}" "store/$f.parquet" "${new[@]}"
  python pipeline/store.py put "store/$f.parquet"
  rows=$(python -c "import pandas as pd;print(len(pd.read_parquet('store/$f.parquet')))")
  echo "| $f | $rows |" >> "$summary"
done
