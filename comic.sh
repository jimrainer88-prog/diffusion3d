#!/usr/bin/env bash
# comic.sh <scene.txt> [panels] [tag]
set -e
cd "$(dirname "$0")"
SRC="$1"
TAG="${3:-$(basename "${SRC%.*}")}"
.venv/bin/python -m local.text_to_panels "$SRC" --n "${2:-4}" --tag "$TAG"
sudo systemctl stop ollama
trap 'sudo systemctl start ollama' EXIT
.venv-img/bin/python -m local.panels2img --tag "$TAG"
.venv/bin/python -m local.letter --tag "$TAG"
echo "-> data/output/strip_$TAG.png"
