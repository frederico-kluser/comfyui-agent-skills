#!/usr/bin/env bash
# setup.sh — person-swap-scail2 (troca de pessoa em vídeo, SCAIL-2 Replacement)
# RunPod / ComfyUI — rode como ROOT no pod (web terminal/JupyterLab):  bash setup.sh
# Ou via template AI-Dock: env PROVISIONING_SCRIPT=<raw_url deste arquivo>.
# Fork focado de .agents/skills/knowledge-runpod-provisioning/scripts/provisioning.sh
set -Euo pipefail

# ============ CONFIG ============
if   [ -d "${WORKSPACE:-/workspace}/ComfyUI" ]; then COMFY="${WORKSPACE:-/workspace}/ComfyUI"
elif [ -d "/opt/ComfyUI" ];                      then COMFY="/opt/ComfyUI"
else COMFY="${WORKSPACE:-/workspace}/ComfyUI"; fi
echo ">> ComfyUI em: $COMFY"

HF_TOKEN="${HF_TOKEN:-}"
CIVITAI_TOKEN="${CIVITAI_TOKEN:-}"
PIP="python -m pip install --no-cache-dir"
PAR=3

# URL raw deste workflow no repo público (baixado p/ o pod automaticamente)
WORKFLOW_URL="https://raw.githubusercontent.com/frederico-kluser/comfyui-agent-skills/main/workflows/person-swap-scail2/person-swap-scail2.json"

# ---- Custom nodes (conjunto SCAIL-2) ----
NODES=(
  "https://github.com/ltdrdata/ComfyUI-Manager"
  "https://github.com/kijai/ComfyUI-WanVideoWrapper"
  "https://github.com/kijai/ComfyUI-KJNodes"
  "https://github.com/kijai/ComfyUI-SCAIL-Pose"
  "https://github.com/city96/ComfyUI-GGUF"
  "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite"
  "https://github.com/rgthree/rgthree-comfy"
  "https://github.com/Fannovel16/ComfyUI-Frame-Interpolation"
  "https://github.com/PozzettiAndrea/ComfyUI-SAM3"
  "https://github.com/cubiq/ComfyUI_essentials"
  "https://github.com/Brobert-in-aus/scail-auto-extend"
)

# ---- Modelos: "URL|subpasta_em_models" (escopo: SCAIL-2 Replacement) ----
MODELS=(
  "https://huggingface.co/Comfy-Org/SCAIL-2/resolve/main/diffusion_models/wan2.1_14B_SCAIL_2_fp8_scaled.safetensors|diffusion_models"
  "https://huggingface.co/Comfy-Org/SCAIL-2/resolve/main/loras/wan2.1_SCAIL_2_DPO_lora_bf16.safetensors|loras"
  "https://huggingface.co/lightx2v/Wan2.1-I2V-14B-480P-StepDistill-CfgDistill-Lightx2v/resolve/main/loras/Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors|loras"
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors|text_encoders"
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors|vae"
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors|clip_vision"
  "https://huggingface.co/Comfy-Org/sam3.1/resolve/main/checkpoints/sam3.1_multiplex_fp16.safetensors|sam"
)

# ============ FUNÇÕES ============
setup_tools() {
  echo ">> Instalando ferramentas (aria2, git)..."
  command -v aria2c >/dev/null 2>&1 || { apt-get update -y && apt-get install -y aria2 git git-lfs; }
}

update_comfy() {
  # SCAIL-2 exige ComfyUI nightly/master (nó 'Create SCAIL-2 Colored Mask' é core)
  if [ -d "$COMFY/.git" ]; then
    echo ">> Atualizando ComfyUI (nightly p/ SCAIL-2)..."
    ( cd "$COMFY" && git pull --ff-only || true )
    [ -f "$COMFY/requirements.txt" ] && $PIP -r "$COMFY/requirements.txt" || true
  else
    echo "   AVISO: $COMFY não é um git clone — garanta manualmente uma build nightly/master."
  fi
}

get_nodes() {
  echo ">> Instalando custom nodes..."
  mkdir -p "$COMFY/custom_nodes"
  for repo in "${NODES[@]}"; do
    dir="${repo##*/}"; path="$COMFY/custom_nodes/$dir"
    if [ ! -d "$path" ]; then git clone --recursive "$repo" "$path" || continue
    else ( cd "$path" && git pull --ff-only || true ); fi
    [ -f "$path/requirements.txt" ] && $PIP -r "$path/requirements.txt" || true
    [ -f "$path/install.py" ] && ( cd "$path" && python install.py || true )
  done
}

dl_one() {
  local url="$1" dest="$COMFY/models/$2"
  mkdir -p "$dest"
  local fname; fname="$(basename "${url%%\?*}")"
  if [ -f "$dest/$fname" ]; then echo "   [skip] $fname"; return 0; fi
  local hdr=()
  [[ "$url" == *huggingface.co* && -n "$HF_TOKEN" ]] && hdr=(--header="Authorization: Bearer $HF_TOKEN")
  [[ "$url" == *civitai.com* && -n "$CIVITAI_TOKEN" ]] && url="${url}?token=${CIVITAI_TOKEN}"
  echo "   baixando $fname -> models/$2"
  aria2c -c -x16 -s16 -k1M --auto-file-renaming=false --allow-overwrite=false \
         --console-log-level=warn --summary-interval=0 \
         "${hdr[@]}" -d "$dest" -o "$fname" "$url" \
    || wget -nc --content-disposition "${hdr[@]}" -P "$dest" "$url"
}

get_models() {
  echo ">> Baixando modelos SCAIL-2 (paralelo: $PAR)..."
  for entry in "${MODELS[@]}"; do
    dl_one "${entry%%|*}" "${entry##*|}" &
    while [ "$(jobs -rp | wc -l)" -ge "$PAR" ]; do wait -n; done
  done
  wait
  # SAM em sam/ e também checkpoints/ (workflows variam)
  if [ -f "$COMFY/models/sam/sam3.1_multiplex_fp16.safetensors" ]; then
    mkdir -p "$COMFY/models/checkpoints"
    ln -sf "$COMFY/models/sam/sam3.1_multiplex_fp16.safetensors" \
           "$COMFY/models/checkpoints/sam3.1_multiplex_fp16.safetensors" 2>/dev/null || true
  fi
}

get_workflow() {
  echo ">> Baixando o workflow person-swap-scail2.json..."
  local wfdir="$COMFY/user/default/workflows"
  mkdir -p "$wfdir"
  wget -nc --content-disposition -P "$wfdir" "$WORKFLOW_URL" \
    || curl -fL --output-dir "$wfdir" --remote-name "$WORKFLOW_URL" || true
}

main() {
  setup_tools
  update_comfy
  get_nodes
  get_workflow
  get_models
  echo "============================================"
  echo " person-swap-scail2: provisionamento COMPLETO."
  echo " 1) Reinicie o ComfyUI (Manager > Restart) e pressione 'R'."
  echo " 2) Abra o workflow person-swap-scail2 e siga o nó LEIA-ME / o README."
  echo " 3) Modelos de pose (NLF/ViTPose) baixam sozinhos no 1º uso."
  echo "============================================"
}
main
