#!/usr/bin/env bash
set -euo pipefail

time_limit="4:00:00"

BASE_DIR="outputs/llm_scoring"
models=(
  "llama3.1"
  "llama3.1:70b"
  "llama3.3"
  "deepseek-r1"
  "deepseek-r1:8b"
  "deepseek-r1:14b"
)
indexes=( {0..11} )

for mapdir in "$BASE_DIR"/*/; do
  [[ -d "$mapdir" ]] || continue
  mapname=$(basename "$mapdir")

  for model in "${models[@]}"; do
    for idx in "${indexes[@]}"; do
      json_f="$mapdir/${idx}_${model}_out.json"
      csv_f="$mapdir/${idx}_${model}_raw_results.csv"

      if [[ ! -f "$json_f" || ! -f "$csv_f" ]]; then
        echo "$mapname: MISSING $model @ $idx"
      fi
    done
  done
done

