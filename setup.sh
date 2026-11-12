#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

PY=$(command -v python3.12 || command -v python3)
"$PY" -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel setuptools

# PyTorch with CUDA 12.4: fails loudly instead of falling back to CPU
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124

pip install -r requirements.txt

if [ ! -d third_party/triposr ]; then
  git clone https://github.com/VAST-AI-Research/TripoSR.git third_party/triposr
fi
# TripoSR deps, incl. torchmcubes (compiled against the torch installed above)
pip install scikit-build-core cmake ninja pybind11
pip install --no-build-isolation git+https://github.com/tatsy/torchmcubes.git
pip install -r <(grep -v torchmcubes third_party/triposr/requirements.txt)

python - <<'PYEOF'
import torch
print("torch", torch.__version__, "| CUDA available:", torch.cuda.is_available())
assert torch.cuda.is_available(), "CUDA not available: check the NVIDIA driver"
PYEOF
echo "Setup complete"