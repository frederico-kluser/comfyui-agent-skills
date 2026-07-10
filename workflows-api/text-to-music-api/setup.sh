#!/usr/bin/env bash
# setup.sh — text-to-music-api (gera trilhas instrumentais/ambient por API de nuvem: ACE-Step no fal/Replicate)
# Roda LOCAL (8GB ok) — a geracao na nuvem NAO usa sua GPU. O caminho local (ComfyUI nativo) e opcional/bonus.
#   REPLICATE_API_TOKEN=r8_...  FAL_KEY=...  bash setup.sh
#   DOWNLOAD_CHECKPOINT=1       bash setup.sh   # tambem baixa o modelo ~3.5GB p/ o caminho LOCAL (ComfyUI)
# As chaves vem do AMBIENTE; o script NUNCA as versiona.
set -Euo pipefail

# --- localizar ComfyUI (local ~/ComfyUI, pod /workspace, ou /opt) ---
if   [ -d "${COMFY_HOME:-}" ];                   then COMFY="$COMFY_HOME"
elif [ -d "${WORKSPACE:-/workspace}/ComfyUI" ];  then COMFY="${WORKSPACE:-/workspace}/ComfyUI"
elif [ -d "$HOME/ComfyUI" ];                     then COMFY="$HOME/ComfyUI"
elif [ -d "/opt/ComfyUI" ];                      then COMFY="/opt/ComfyUI"
else COMFY="$HOME/ComfyUI"; fi
echo ">> ComfyUI em: $COMFY"

PROJECT="text-to-music-api"
DEST="$COMFY/user/default/workflows/$PROJECT"
WORKFLOW_BASE="https://raw.githubusercontent.com/frederico-kluser/comfyui-agent-skills/main/workflows-api/${PROJECT}"
SECRETS="$COMFY/secrets.env"

# arquivos de runtime do bundle (script de lote + presets + workflow LOCAL do ComfyUI)
FILES=(
  "gerar_trilhas.mjs"
  "presets.json"
  "text-to-music-local.json"
)

get_files(){
  mkdir -p "$DEST"
  for f in "${FILES[@]}"; do
    # se rodando de dentro do repo, copia; senao baixa do repo publico
    if [ -f "$(dirname "$0")/$f" ]; then cp -f "$(dirname "$0")/$f" "$DEST/$f"
    else wget -nc -P "$DEST" "$WORKFLOW_BASE/$f" 2>/dev/null \
      || curl -fsSL --output-dir "$DEST" --remote-name "$WORKFLOW_BASE/$f" \
      || echo "   (falhou baixar: $f — pegue manualmente do repo)"; fi
  done
}

# deps do script de nuvem (Node): replicate + @fal-ai/client
node_deps(){
  if ! command -v npm >/dev/null 2>&1; then
    echo ">> npm nao encontrado. Instale Node.js 18+ (https://nodejs.org) e rode de novo, OU use so o caminho LOCAL (ComfyUI)."
    return 0
  fi
  ( cd "$DEST" && [ -f package.json ] || printf '{\n  "name": "text-to-music-api",\n  "private": true,\n  "type": "module"\n}\n' > package.json )
  ( cd "$DEST" && npm install --no-audit --no-fund replicate @fal-ai/client ) \
    && echo ">> deps Node instaladas em $DEST/node_modules" \
    || echo ">> falha no npm install (rode manualmente:  cd \"$DEST\" && npm i replicate @fal-ai/client )"
}

# grava chaves do AMBIENTE em secrets.env (nunca embute segredo no repo)
config_keys(){
  local wrote=0
  [ -n "${FAL_KEY:-}" ]              && { grep -q '^export FAL_KEY='              "$SECRETS" 2>/dev/null || printf 'export FAL_KEY=%s\n' "$FAL_KEY"                          >> "$SECRETS"; wrote=1; }
  [ -n "${REPLICATE_API_TOKEN:-}" ] && { grep -q '^export REPLICATE_API_TOKEN='  "$SECRETS" 2>/dev/null || printf 'export REPLICATE_API_TOKEN=%s\n' "$REPLICATE_API_TOKEN"  >> "$SECRETS"; wrote=1; }
  if [ "$wrote" = 1 ]; then chmod 600 "$SECRETS"; echo ">> chave(s) gravada(s) em $SECRETS (chmod 600). Rode:  source $SECRETS  antes do script."
  else echo ">> Nenhuma chave no ambiente. Defina REPLICATE_API_TOKEN e/ou FAL_KEY (em $SECRETS ou export) antes de gerar."; fi
}

# opcional: baixa o checkpoint ACE-Step p/ o caminho LOCAL (ComfyUI nativo, ~3.5GB)
get_checkpoint(){
  [ "${DOWNLOAD_CHECKPOINT:-0}" = "1" ] || { echo ">> (pulei o checkpoint local; use DOWNLOAD_CHECKPOINT=1 para baixar o modelo do caminho LOCAL)"; return 0; }
  local dir="$COMFY/models/checkpoints" url="https://huggingface.co/Comfy-Org/ACE-Step_ComfyUI_repackaged/resolve/main/all_in_one/ace_step_v1_3.5b.safetensors?download=true"
  mkdir -p "$dir"
  echo ">> baixando ace_step_v1_3.5b.safetensors (~3.5GB) para $dir ..."
  if command -v aria2c >/dev/null 2>&1; then aria2c -x16 -s16 -c -o "ace_step_v1_3.5b.safetensors" -d "$dir" "$url"
  else wget -c -O "$dir/ace_step_v1_3.5b.safetensors" "$url"; fi
}

get_files; node_deps; config_keys; get_checkpoint
echo "============================================"
echo " text-to-music-api pronto."
echo " Bundle em: $DEST"
echo ""
echo " CAMINHO NUVEM (recomendado — sem GPU):"
echo "   source $SECRETS   # carrega as chaves"
echo "   cd \"$DEST\""
echo "   node gerar_trilhas.mjs --provider replicate --preset all --count 3    # ToS mais limpa p/ vender"
echo "   node gerar_trilhas.mjs --provider fal       --preset perseguicao --count 10"
echo "   -> arquivos .wav em $DEST/output/"
echo ""
echo " CAMINHO LOCAL (bonus, so se tiver ~8GB de VRAM — \$0/faixa, licenca a mais limpa):"
echo "   1) DOWNLOAD_CHECKPOINT=1 bash setup.sh   (uma vez, baixa o modelo)"
echo "   2) Reinicie o ComfyUI e abra text-to-music-local.json (ACE-Step e nativo/core; sem custom node)."
echo "============================================"
