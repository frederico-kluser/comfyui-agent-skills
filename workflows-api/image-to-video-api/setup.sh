#!/usr/bin/env bash
# setup.sh — image-to-video-api (anima UMA imagem + descrição → vídeo, 100% por API online)
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
PROJECT="image-to-video-api"
WORKFLOW_BASE="https://raw.githubusercontent.com/frederico-kluser/comfyui-agent-skills/main/workflows-api/${PROJECT}"

# Custom nodes. Os nós PARTNER (Kling/Grok/ByteDance) são CORE (login comfy.org, não instala aqui).
NODES=(
  "https://github.com/ltdrdata/ComfyUI-Manager"
  "https://github.com/gokayfem/ComfyUI-fal-API"        # *_fal: Veo31_fal, Seedance*_fal, Kling*_fal, LoadVideoURL
  "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite"
)

# Workflows (2 guias + 8 modelos de imagem→vídeo).
WORKFLOWS=(
  "00_LEIA-ME_comece_aqui.json" "01_GUIA_prompt_e_modelos.json"
  "10_veo31_premium.json" "11_veo31_fast.json"
  "12_seedance_rascunho_480p.json" "13_seedance15_1080p_audio.json" "14_seedance_pro_morph.json"
  "15_kling25_movimento.json" "16_kling26_audio.json" "18_grok_imagine.json"
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
echo " image-to-video-api pronto."
echo " 1) Reinicie o ComfyUI."
echo " 2) Login p/ os nós partner (Kling/Grok/ByteDance): Settings > User > Sign In (platform.comfy.org)."
echo " 3) Workflows em: $COMFY/user/default/workflows/$PROJECT/"
echo " 4) Abra 00_LEIA-ME, escolha um modelo, faça Load Image, ajuste o prompt e Run."
echo "    Nós vermelhos? Manager > Install Missing Custom Nodes."
echo "============================================"
