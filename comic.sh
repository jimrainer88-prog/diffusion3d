#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
.venv/bin/python -m local.text_to_panels "$1" --n "${2:-4}"
sudo systemctl stop ollama
trap 'sudo systemctl start ollama' EXIT
.venv-img/bin/python -m local.panels2img
.venv/bin/python -m local.letter
