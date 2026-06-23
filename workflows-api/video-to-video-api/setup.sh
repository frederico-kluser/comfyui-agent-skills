#!/usr/bin/env bash
# setup.sh — video-to-video-api (transforma UM vídeo + descrição → vídeo, 100% por API online)
# Roda LOCAL (8GB ok) ou num pod pequeno — o ComfyUI só orquestra; a geração é na nuvem.
#   FAL_KEY=...  bash setup.sh      (a FAL_KEY vem do AMBIENTE; o script NUNCA a versiona)
set -Euo pipefail

# --- localizar ComfyUI (local ~/ComfyUI, pod /workspace, ou /opt) ---
if   [ -d "${COMFY_HOME:-}" ];                   then COMFY="$COMFY_HOME"
elif [ -d "${WORKSPACE:-/workspace}/ComfyUI" ];  then COMFY="${WORKSPACE:-/workspace}/ComfyUI"
elif [ -d "$HOME/ComfyUI" ];                     then COMFY="$HOME/ComfyUI"
elif [ -d "/opt/ComfyUI" ];                      then COMFY="/opt/ComfyUI"
else COMFY="$HOME/ComfyUI"; fi
echo ">> ComfyUI em: $COMFY"

FAL_KEY="${FAL_KEY:-}"
PROJECT="video-to-video-api"
WORKFLOW_BASE="https://raw.githubusercontent.com/frederico-kluser/comfyui-agent-skills/main/workflows-api/${PROJECT}"

# Custom nodes. Os nós PARTNER (Runway/Kling/Grok/Vidu) são CORE (login comfy.org, não instala aqui).
NODES=(
  "https://github.com/ltdrdata/ComfyUI-Manager"
  "https://github.com/gokayfem/ComfyUI-fal-API"        # *_fal: Wan2214b_animate_*, KlingOmni*, KlingV3*, LoadVideoURL
  "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite"
)

# Workflows (2 guias + 9 modelos de vídeo→vídeo: restyle / motion-transfer / extend).
WORKFLOWS=(
  "00_LEIA-ME_comece_aqui.json" "01_GUIA_modos_e_entrada.json"
  "10_restyle_runway_aleph.json" "11_edit_grok.json" "12_edit_kling_omni.json"
  "20_animate_wan_move.json" "21_animate_wan_replace.json" "22_motion_kling_v3.json"
  "30_extend_grok.json" "31_extend_kling.json" "32_extend_vidu.json"
)

setup_tools(){ command -v git >/dev/null 2>&1 || { apt-get update -y && apt-get install -y git; }; }

get_nodes(){
  mkdir -p "$COMFY/custom_nodes"
  for repo in "${NODES[@]}"; do
    dir="${repo##*/}"; path="$COMFY/custom_nodes/$dir"
    if [ ! -d "$path" ]; then git clone --recursive "$repo" "$path" || continue
    else ( cd "$path" && git pull --ff-only || true ); fi
    [ -f "$path/requirements.txt" ] && python -m pip install --no-cache-dir -r "$path/requirements.txt" || true
  done
}

# Grava a FAL_KEY no config.ini do nó (a PARTIR do ambiente) — nunca embute segredo no repo.
config_fal(){
  local cfg="$COMFY/custom_nodes/ComfyUI-fal-API/config.ini"
  if [ -z "$FAL_KEY" ]; then
    echo ">> FAL_KEY não está no ambiente — pulei o config.ini."
    echo "   Configure depois (uma das opções):"
    echo "     - export FAL_KEY=... no seu ~/ComfyUI/secrets.env (chmod 600, gitignored) e reinicie; OU"
    echo "     - edite $cfg  →  [API]\\n  FAL_KEY = <sua-chave>"
    return 0
  fi
  mkdir -p "$(dirname "$cfg")"
  printf '[API]\nFAL_KEY = %s\n' "$FAL_KEY" > "$cfg"
  chmod 600 "$cfg"
  echo ">> FAL_KEY gravada em $cfg (chmod 600)."
}

get_workflows(){
  local d="$COMFY/user/default/workflows/$PROJECT"; mkdir -p "$d"
  for wf in "${WORKFLOWS[@]}"; do
    wget -nc -P "$d" "$WORKFLOW_BASE/$wf" 2>/dev/null \
      || curl -fsSL --output-dir "$d" --remote-name "$WORKFLOW_BASE/$wf" \
      || echo "   (falhou: $wf — baixe manualmente do repo)"
  done
}

setup_tools; get_nodes; config_fal; get_workflows
echo "============================================"
echo " video-to-video-api pronto."
echo " 1) Reinicie o ComfyUI."
echo " 2) Login p/ os nós partner (Runway/Kling/Grok/Vidu): Settings > User > Sign In (platform.comfy.org)."
echo " 3) Workflows em: $COMFY/user/default/workflows/$PROJECT/"
echo " 4) Abra 00_LEIA-ME, escolha o modo (restyle/animar/estender), Load Video (+ Load Image nos modos B) e Run."
echo "    Nós vermelhos? Manager > Install Missing Custom Nodes."
echo "============================================"
