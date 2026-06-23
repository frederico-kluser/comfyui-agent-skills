#!/usr/bin/env bash
# setup.sh — replace-pose (trocar a POSE de uma pessoa, por foto de referência OU por texto, via API)
# Roda LOCAL (8GB ok). Geração na fal (Nano Banana Pro / Flux Pro Kontext Multi) = FAL_KEY.
#   FAL_KEY=...  bash setup.sh
set -Euo pipefail

if   [ -d "${COMFY_HOME:-}" ];                   then COMFY="$COMFY_HOME"
elif [ -d "${WORKSPACE:-/workspace}/ComfyUI" ];  then COMFY="${WORKSPACE:-/workspace}/ComfyUI"
elif [ -d "$HOME/ComfyUI" ];                     then COMFY="$HOME/ComfyUI"
elif [ -d "/opt/ComfyUI" ];                      then COMFY="/opt/ComfyUI"
else COMFY="$HOME/ComfyUI"; fi
echo ">> ComfyUI em: $COMFY"

FAL_KEY="${FAL_KEY:-}"
PROJECT="replace-pose"
WORKFLOW_BASE="https://raw.githubusercontent.com/frederico-kluser/comfyui-agent-skills/main/workflows-api/${PROJECT}"

NODES=(
  "https://github.com/ltdrdata/ComfyUI-Manager"
  "https://github.com/gokayfem/ComfyUI-fal-API"   # NanoBananaPro_fal + FluxProKontextMulti_fal
  "https://github.com/kijai/ComfyUI-KJNodes"      # ImageResizeKJ
)
WORKFLOWS=(
  "00_LEIA-ME_comece_aqui.json" "01_referencia_nanobanana.json" "02_referencia_kontext.json"
  "03_texto_nanobanana.json" "04_texto_kontext.json"
)

setup_tools(){ command -v git >/dev/null 2>&1 || { apt-get update -y && apt-get install -y git; }; }
get_nodes(){ mkdir -p "$COMFY/custom_nodes"; for repo in "${NODES[@]}"; do dir="${repo##*/}"; path="$COMFY/custom_nodes/$dir"
  if [ ! -d "$path" ]; then git clone --recursive "$repo" "$path" || continue; else ( cd "$path" && git pull --ff-only || true ); fi
  [ -f "$path/requirements.txt" ] && python -m pip install --no-cache-dir -r "$path/requirements.txt" || true; done; }
config_fal(){ local cfg="$COMFY/custom_nodes/ComfyUI-fal-API/config.ini"
  [ -z "$FAL_KEY" ] && { echo ">> FAL_KEY não setada — necessária p/ todos os workflows. Configure em $cfg ou ~/ComfyUI/secrets.env."; return 0; }
  mkdir -p "$(dirname "$cfg")"; printf '[API]\nFAL_KEY = %s\n' "$FAL_KEY" > "$cfg"; chmod 600 "$cfg"; echo ">> FAL_KEY gravada (chmod 600)."; }
get_workflows(){ local d="$COMFY/user/default/workflows/$PROJECT"; mkdir -p "$d"
  for wf in "${WORKFLOWS[@]}"; do wget -nc -P "$d" "$WORKFLOW_BASE/$wf" 2>/dev/null \
    || curl -fsSL --output-dir "$d" --remote-name "$WORKFLOW_BASE/$wf" || echo "   (falhou: $wf)"; done; }

setup_tools; get_nodes; config_fal; get_workflows
echo "============================================"
echo " replace-pose pronto. Reinicie o ComfyUI."
echo " Nós vermelhos? Manager > Install Missing (fal-API, KJNodes)."
echo " Referência: suba BASE + a foto da POSE. Texto: suba só a BASE e descreva a pose no prompt."
echo " Workflows em: $COMFY/user/default/workflows/$PROJECT/"
echo "============================================"
