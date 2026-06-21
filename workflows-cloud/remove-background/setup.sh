#!/usr/bin/env bash
# setup.sh — remove-background (ComfyUI-RMBG: BiRefNet/RMBG/BEN2/SAM3)
# RunPod/ComfyUI — rode como ROOT:  bash setup.sh
set -Euo pipefail
if   [ -d "${WORKSPACE:-/workspace}/ComfyUI" ]; then COMFY="${WORKSPACE:-/workspace}/ComfyUI"
elif [ -d "/opt/ComfyUI" ];                      then COMFY="/opt/ComfyUI"
else COMFY="${WORKSPACE:-/workspace}/ComfyUI"; fi
echo ">> ComfyUI em: $COMFY"
HF_TOKEN="${HF_TOKEN:-}"; PIP="python -m pip install --no-cache-dir"
WORKFLOW_URL="https://raw.githubusercontent.com/frederico-kluser/comfyui-agent-skills/main/workflows-cloud/remove-background/remove-background.json"

# Os modelos de matting do RMBG baixam sozinhos no 1º uso do nó; SAM3 exige licença no HF.
NODES=(
  "https://github.com/ltdrdata/ComfyUI-Manager"
  "https://github.com/1038lab/ComfyUI-RMBG"
)

setup_tools(){ command -v git >/dev/null 2>&1 || { apt-get update -y && apt-get install -y git git-lfs; }; }
get_nodes(){ mkdir -p "$COMFY/custom_nodes"; for repo in "${NODES[@]}"; do dir="${repo##*/}"; path="$COMFY/custom_nodes/$dir"
  if [ ! -d "$path" ]; then git clone --recursive "$repo" "$path" || continue; else ( cd "$path" && git pull --ff-only || true ); fi
  [ -f "$path/requirements.txt" ] && $PIP -r "$path/requirements.txt" || true; done; }
get_workflow(){ local d="$COMFY/user/default/workflows"; mkdir -p "$d"; wget -nc -P "$d" "$WORKFLOW_URL" || curl -fL --output-dir "$d" --remote-name "$WORKFLOW_URL" || true; }

setup_tools; get_nodes; get_workflow
echo "============================================"
echo " remove-background pronto. Reinicie o ComfyUI."
echo " Modelos RMBG baixam no 1o uso. SAM3: aceite a licenca no HF e exporte HF_TOKEN."
echo "============================================"
