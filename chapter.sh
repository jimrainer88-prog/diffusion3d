#!/usr/bin/env bash
# chapter.sh <chapter.txt> [scenes] [panels-per-page]
# Scripts are written with Ollama up, then SDXL loads ONCE for every page.
set -e
cd "$(dirname "$0")"
CH="$1"; SCENES="${2:-4}"; PANELS="${3:-4}"
STEM=$(basename "${CH%.*}")

.venv/bin/python -m local.split_scenes "$CH" --n "$SCENES"
TAGS=()
for f in data/prompts/${STEM}_scene*.txt; do
  T=$(basename "${f%.*}")
  .venv/bin/python -m local.text_to_panels "$f" --n "$PANELS" --tag "$T"
  TAGS+=(--tag "$T")
done

sudo systemctl stop ollama
trap 'sudo systemctl start ollama' EXIT
.venv-img/bin/python -m local.panels2img "${TAGS[@]}"
trap - EXIT
sudo systemctl start ollama

for f in data/prompts/${STEM}_scene*.txt; do
  .venv/bin/python -m local.letter --tag "$(basename "${f%.*}")"
done
