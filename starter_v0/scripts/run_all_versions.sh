#!/usr/bin/env bash
# Run baseline + optimization versions. Usage:
#   cd starter_v0 && source .venv/bin/activate
#   ./scripts/run_all_versions.sh openrouter
set -euo pipefail
PROVIDER="${1:-gemini}"
MODEL="${2:-gemini-2.5-flash-lite}"
DELAY="${3:-13}"
MODEL_FLAG=()
if [[ -n "$MODEL" ]]; then MODEL_FLAG=(--model "$MODEL"); fi

run() {
  local version="$1"
  local prompt="$2"
  local suite="$3"
  local cases="$4"
  echo "=== $version ($suite) ==="
  python run_eval.py --provider "$PROVIDER" "${MODEL_FLAG[@]}" --delay-seconds "$DELAY" \
    --version "$version" --suite "$suite" --system-prompt "$prompt" --eval-cases "$cases"
}

run v0 artifacts/prompts/v0_baseline_system_prompt.md base data/eval_base.json
run v1 artifacts/prompts/v1_system_prompt.md base data/eval_base.json
run v2 artifacts/prompts/v2_system_prompt.md base data/eval_base.json
run v3 artifacts/system_prompt.md base data/eval_base.json
run v3-group artifacts/system_prompt.md group data/eval_group.json

echo "Done. Fill artifacts/version_log.csv from runs/*.json summaries."
