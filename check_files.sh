#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 [--submit]"
  echo
  echo "  --submit   actually sbatch any missing model@prompt combos"
  exit 1
}

# parse flag
SUBMIT=false
if [[ "${1:-}" == "--submit" ]]; then
  SUBMIT=true
elif [[ "${1:-}" != "" ]]; then
  usage
fi

BASE_DIR="outputs/llm_scoring"

# the models
models=(
  "llama3.1"
  "llama3.1:70b"
  "llama3.3"
  "deepseek-r1"
  "deepseek-r1:8b"
  "deepseek-r1:14b"
  "deepseek-r1:32b"
  "deepseek-r1:70b"
)

# the prompt indexes
indexes=( {0..11} )

# remember which (model,idx) combos we've already queued
declare -A submitted=()

for mapdir in "$BASE_DIR"/*/; do
  [[ -d "$mapdir" ]] || continue
  mapname=$(basename "$mapdir")

  for model in "${models[@]}"; do
    for idx in "${indexes[@]}"; do
      json_f="$mapdir/${idx}_${model}_out.json"
      csv_f="$mapdir/${idx}_${model}_raw_results.csv"

      if [[ ! -f "$json_f" || ! -f "$csv_f" ]]; then
        combo="${model}__${idx}"
        # always print the missing report
        echo "$mapname: MISSING $model @ $idx"

        # then optionally submit (once per combo)
        if $SUBMIT && [[ -z "${submitted[$combo]:-}" ]]; then
          echo "  → submitting rerun for $model @ $idx"
          sbatch --export=MODEL_NAME="$model",PROMPT_INDEX="$idx" benchmark_single_big.sh
          submitted[$combo]=1
        fi
      fi
    done
  done
done

if ! $SUBMIT; then
  echo
  echo "Run with --submit to automatically resubmit any missing jobs."
fi
