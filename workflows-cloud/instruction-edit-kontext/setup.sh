#!/usr/bin/env bash
# setup.sh — instruction-edit-kontext (Flux Kontext, edição por instrução)
# RunPod/ComfyUI — rode como ROOT:  bash setup.sh
set -Euo pipefail
if   [ -d "${WORKSPACE:-/workspace}/ComfyUI" ]; then COMFY="${WORKSPACE:-/workspace}/ComfyUI"
elif [ -d "/opt/ComfyUI" ];                      then COMFY="/opt/ComfyUI"
else COMFY="${WORKSPACE:-/workspace}/ComfyUI"; fi
echo ">> ComfyUI em: $COMFY"
HF_TOKEN="${HF_TOKEN:-}"; PIP="python -m pip install --no-cache-dir"; PAR=3
WORKFLOW_URL="https://raw.githubusercontent.com/frederico-kluser/comfyui-agent-skills/main/workflows-cloud/instruction-edit-kontext/instruction-edit-kontext.json"

NODES=(
  "https://github.com/ltdrdata/ComfyUI-Manager"
  "https://github.com/kijai/ComfyUI-KJNodes"
  "https://github.com/rgthree/rgthree-comfy"
  "https://github.com/city96/ComfyUI-GGUF"
)
MODELS=(
  "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors|text_encoders"
  "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn_scaled.safetensors|text_encoders"
  "https://huggingface.co/Comfy-Org/Lumina_Image_2.0_Repackaged/resolve/main/split_files/vae/ae.safetensors|vae"
  # Flux Kontext dev fp8 (Comfy-Org repackaged — confirme na aba Files):
  "https://huggingface.co/Comfy-Org/FLUX.1-Kontext-dev_ComfyUI/resolve/main/split_files/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors|diffusion_models"
)

setup_tools(){ command -v aria2c >/dev/null 2>&1 || { apt-get update -y && apt-get install -y aria2 git git-lfs; }; }
get_nodes(){ mkdir -p "$COMFY/custom_nodes"; for repo in "${NODES[@]}"; do dir="${repo##*/}"; path="$COMFY/custom_nodes/$dir"
  if [ ! -d "$path" ]; then git clone --recursive "$repo" "$path" || continue; else ( cd "$path" && git pull --ff-only || true ); fi
  [ -f "$path/requirements.txt" ] && $PIP -r "$path/requirements.txt" || true; done; }
dl_one(){ local url="$1" dest="$COMFY/models/$2"; mkdir -p "$dest"; local fname; fname="$(basename "${url%%\?*}")"
  [ -f "$dest/$fname" ] && { echo "   [skip] $fname"; return 0; }
  local hdr=(); [[ "$url" == *huggingface.co* && -n "$HF_TOKEN" ]] && hdr=(--header="Authorization: Bearer $HF_TOKEN")
  echo "   baixando $fname -> models/$2"
  aria2c -c -x16 -s16 -k1M --auto-file-renaming=false --allow-overwrite=false --console-log-level=warn --summary-interval=0 \
         "${hdr[@]}" -d "$dest" -o "$fname" "$url" || wget -nc --content-disposition "${hdr[@]}" -P "$dest" "$url" || echo "   (falhou: confirme a URL no HF)"; }
get_models(){ for e in "${MODELS[@]}"; do dl_one "${e%%|*}" "${e##*|}" & while [ "$(jobs -rp | wc -l)" -ge "$PAR" ]; do wait -n; done; done; wait; }
get_workflow(){ local d="$COMFY/user/default/workflows"; mkdir -p "$d"; wget -nc -P "$d" "$WORKFLOW_URL" || curl -fL --output-dir "$d" --remote-name "$WORKFLOW_URL" || true; }

setup_tools; get_nodes; get_workflow; get_models
echo "============================================"
echo " instruction-edit-kontext pronto. Reinicie o ComfyUI. Modelos faltantes: Manager > Model Manager."
echo "============================================"
