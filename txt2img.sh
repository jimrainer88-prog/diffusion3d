#!/usr/bin/env bash
# SDXL needs the whole 12 GB, so park Ollama for the duration and always bring it back.
set -e
cd "$(dirname "$0")"
sudo systemctl stop ollama
trap 'sudo systemctl start ollama' EXIT
source .venv-img/bin/activate
python -m local.txt2img "$@"
