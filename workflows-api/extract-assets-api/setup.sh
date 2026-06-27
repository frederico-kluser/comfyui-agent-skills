#!/usr/bin/env bash
# setup.sh — extract-assets-api (separar assets de uma UI gerada por IA → PNG transparente, por API)
# Roda LOCAL (8GB ok) ou no pod. Geração por API:
#   - Nano Banana Pro = fal  → precisa de FAL_KEY
#   - Recraft Remove Background = nó partner (core) → precisa de LOGIN em platform.comfy.org (créditos), SEM chave
#   FAL_KEY=...  bash setup.sh
set -Euo pipefail

if   [ -d "${COMFY_HOME:-}" ];                   then COMFY="$COMFY_HOME"
elif [ -d "${WORKSPACE:-/workspace}/ComfyUI" ];  then COMFY="${WORKSPACE:-/workspace}/ComfyUI"
elif [ -d "$HOME/ComfyUI" ];                     then COMFY="$HOME/ComfyUI"
elif [ -d "/opt/ComfyUI" ];                      then COMFY="/opt/ComfyUI"
else COMFY="$HOME/ComfyUI"; fi
echo ">> ComfyUI em: $COMFY"

FAL_KEY="${FAL_KEY:-}"
PROJECT="extract-assets-api"
WORKFLOW_BASE="https://raw.githubusercontent.com/frederico-kluser/comfyui-agent-skills/main/workflows-api/${PROJECT}"

# Recraft Remove Background é nó CORE (comfy_api_nodes) → nada a instalar além do fal-API.
NODES=(
  "https://github.com/ltdrdata/ComfyUI-Manager"
  "https://github.com/gokayfem/ComfyUI-fal-API"   # NanoBananaPro_fal
)
# baixados juntos (o extract_assets.py procura o .api.json na mesma pasta)
FILES=(
  "extract-assets-api.json"
  "extract-assets-api.api.json"
  "extract_assets.py"
)

setup_tools(){ command -v git >/dev/null 2>&1 || { apt-get update -y && apt-get install -y git; }; }
get_nodes(){ mkdir -p "$COMFY/custom_nodes"; for repo in "${NODES[@]}"; do dir="${repo##*/}"; path="$COMFY/custom_nodes/$dir"
  if [ ! -d "$path" ]; then git clone --recursive "$repo" "$path" || continue; else ( cd "$path" && git pull --ff-only || true ); fi
  [ -f "$path/requirements.txt" ] && python -m pip install --no-cache-dir -r "$path/requirements.txt" || true; done; }
config_fal(){ local cfg="$COMFY/custom_nodes/ComfyUI-fal-API/config.ini"
  [ -z "$FAL_KEY" ] && { echo ">> FAL_KEY não setada — necessária p/ o Nano Banana Pro. Configure em $cfg ou ~/ComfyUI/secrets.env."; return 0; }
  mkdir -p "$(dirname "$cfg")"; printf '[API]\nFAL_KEY = %s\n' "$FAL_KEY" > "$cfg"; chmod 600 "$cfg"; echo ">> FAL_KEY gravada (chmod 600)."; }
get_files(){ local d="$COMFY/user/default/workflows/$PROJECT"; mkdir -p "$d"
  for wf in "${FILES[@]}"; do wget -nc -P "$d" "$WORKFLOW_BASE/$wf" 2>/dev/null \
    || curl -fsSL --output-dir "$d" --remote-name "$WORKFLOW_BASE/$wf" || echo "   (falhou: $wf)"; done; }

setup_tools; get_nodes; config_fal; get_files
echo "============================================"
echo " extract-assets-api pronto. Reinicie o ComfyUI."
echo " Nós vermelhos? Manager > Install Missing (fal-API). Recraft é nó CORE (atualize o ComfyUI se faltar)."
echo " IMPORTANTE: faça LOGIN em https://platform.comfy.org (créditos do Recraft Remove Background)."
echo " Workflow visual + script em: $COMFY/user/default/workflows/$PROJECT/"
echo " Lote por terminal:  python $COMFY/user/default/workflows/$PROJECT/extract_assets.py ui.png \"the logo\" \"the avatar\""
echo "============================================"
