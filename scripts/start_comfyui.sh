#!/bin/zsh
set -euo pipefail

AI_HOME="$HOME/ai"
VENV_PATH="$AI_HOME/comfyui-env"
COMFYUI_PATH="$AI_HOME/ComfyUI"
URL="http://127.0.0.1:8188"

source "$VENV_PATH/bin/activate"
cd "$COMFYUI_PATH"

echo "$URL"
export PYTORCH_ENABLE_MPS_FALLBACK=1

if python -c 'import torch; raise SystemExit(0 if torch.backends.mps.is_available() else 1)'; then
  exec python main.py --listen 127.0.0.1 --port 8188
else
  exec python main.py --listen 127.0.0.1 --port 8188 --cpu
fi
