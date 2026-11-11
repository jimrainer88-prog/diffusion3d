#!/bin/bash

# Create virtual environment with Python 3.11
python3.11 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install PyTorch for CUDA 12.4
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu121

# Install other requirements
pip install -r requirements.txt

# Clone TripoSR into third_party/
if [ ! -d "third_party/triposr" ]; then
    git clone https://github.com/VAST-AI-Research/TripoSR.git third_party/triposr
    cd third_party/triposr
    pip install -e .
    cd ../../
fi

echo "Setup complete!"