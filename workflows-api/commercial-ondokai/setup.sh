#!/usr/bin/env bash
# setup.sh — commercial-ondokai (comercial ~30s 100% por API: Veo 3.1 + Nano Banana Pro + Kling + Seedance)
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
PROJECT="commercial-ondokai"
WORKFLOW_BASE="https://raw.githubusercontent.com/frederico-kluser/comfyui-agent-skills/main/workflows-api/${PROJECT}"

# Custom nodes que o comercial usa. Kling = partner/CORE (login comfy.org, não instala aqui).
NODES=(
  "https://github.com/ltdrdata/ComfyUI-Manager"
  "https://github.com/gokayfem/ComfyUI-fal-API"        # *_fal: Veo31_fal, NanoBananaPro_fal, Seedance*_fal
  "https://github.com/kijai/ComfyUI-KJNodes"           # ImageResizeKJ, GetImageRangeFromBatch, ColorMatch
  "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite"
)

# Os 19 workflows do comercial (guias + âncora + 9 cenas + ferramenta + moldes + extensões).
WORKFLOWS=(
  "00_LEIA-ME_comece_aqui.json" "01_GUIA_prompts_e_camera.json" "02_GLOSSARIO_configuracoes.json"
  "10_ANCORA_protagonista.json"
  "11_cena01_coldopen.json" "12_cena02_gaiola.json" "13_cena03_faisca.json" "14_cena04_estalo_morph.json"
  "15_cena05_hero.json" "16_cena06_roda_sozinho.json" "17_cena07_santuario.json" "18_cena08_libertacao.json"
  "19_cena09_logo.json"
  "20_FERRAMENTA_rascunho_barato.json"
  "30_MODELO_cena_nova_keyframe_veo.json" "31_MODELO_cena_camera_kling.json"
  "40_ESTENDER_A_veo_handoff.json" "41_ESTENDER_B_kling_nativo.json" "42_ESTENDER_C_seedance_barato.json"
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
echo " commercial-ondokai pronto."
echo " 1) Reinicie o ComfyUI."
echo " 2) Login para os nós Kling: Settings > User > Sign In (platform.comfy.org)."
echo " 3) Workflows em: $COMFY/user/default/workflows/$PROJECT/"
echo " 4) Abra 10_ANCORA_protagonista, troque a frase <<PROTAGONISTA>>, gere a âncora; depois as cenas."
echo "    Nós vermelhos? Manager > Install Missing Custom Nodes."
echo "============================================"
