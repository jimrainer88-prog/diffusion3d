#!/bin/bash

# Create virtual environment with Python 3.12 (available in system)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install PyTorch for CUDA 12.4 (try to install first, but if that fails, use compatible version)
echo "Attempting to install PyTorch with CUDA 12.1 support..."
pip install torch==2.2.1 torchvision==0.17.1 torchaudio==2.2.1 --index-url https://download.pytorch.org/whl/cu121 || \
    echo "Failed to install with CUDA 12.1, installing CPU version instead" && pip install torch==2.2.1 torchvision==0.17.1 torchaudio==2.2.1

# Install other requirements
pip install -r requirements.txt

# Clone TripoSR into third_party/
if [ ! -d "third_party/triposr" ]; then
    echo "Cloning TripoSR..."
    git clone https://github.com/VAST-AI-Research/TripoSR.git third_party/triposr
fi

echo "Setup complete!"