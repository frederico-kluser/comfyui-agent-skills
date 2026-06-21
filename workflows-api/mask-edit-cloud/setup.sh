#!/usr/bin/env bash
# setup.sh — mask-edit-cloud (máscara local SAM/DINO + inpaint nuvem fal OU local SDXL + composite)
# Roda LOCAL (8GB ok). A máscara é local; a geração pode ser nuvem (FAL_KEY) ou local (SDXL).
#   HF_TOKEN=... FAL_KEY=... INSTALL_SDXL=1 bash setup.sh
set -Euo pipefail

if   [ -d "${COMFY_HOME:-}" ];                   then COMFY="$COMFY_HOME"
elif [ -d "${WORKSPACE:-/workspace}/ComfyUI" ];  then COMFY="${WORKSPACE:-/workspace}/ComfyUI"
elif [ -d "$HOME/ComfyUI" ];                     then COMFY="$HOME/ComfyUI"
elif [ -d "/opt/ComfyUI" ];                      then COMFY="/opt/ComfyUI"
else COMFY="$HOME/ComfyUI"; fi
echo ">> ComfyUI em: $COMFY"

HF_TOKEN="${HF_TOKEN:-}"; FAL_KEY="${FAL_KEY:-}"; INSTALL_SDXL="${INSTALL_SDXL:-0}"
PIP="python -m pip install --no-cache-dir"; PAR=3
PROJECT="mask-edit-cloud"
WORKFLOW_BASE="https://raw.githubusercontent.com/frederico-kluser/comfyui-agent-skills/main/workflows-api/${PROJECT}"

NODES=(
  "https://github.com/ltdrdata/ComfyUI-Manager"
  "https://github.com/storyicon/comfyui_segment_anything"   # GroundingDinoSAMSegment + loaders
  "https://github.com/kijai/ComfyUI-KJNodes"                # GrowMaskWithBlur, ImageCrop/UncropByMask, ColorMatch
  "https://github.com/gokayfem/ComfyUI-fal-API"             # FluxPro1Fill_fal (rota nuvem)
)
WORKFLOWS=(
  "00_LEIA-ME_comece_aqui.json" "01_selecionar_regiao_texto.json"
  "02_inpaint_local_sdxl_composite.json" "03_inpaint_nuvem_fal_composite.json"
  "04_crop_stitch_alta_res.json" "replace_via_codigo.py"
)
# Modelos de MÁSCARA (locais, precisão cheia ~3.4GB). SDXL (~6.5GB) só com INSTALL_SDXL=1.
MODELS=(
  "https://huggingface.co/HCMUE-Research/SAM-vit-h/resolve/main/sam_vit_h_4b8939.pth|sams"
  "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/groundingdino_swinb_cogcoor.pth|grounding-dino"
  "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/GroundingDINO_SwinB.cfg.py|grounding-dino"
)
[ "$INSTALL_SDXL" = "1" ] && MODELS+=( "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors|checkpoints" )

setup_tools(){ command -v aria2c >/dev/null 2>&1 || { apt-get update -y && apt-get install -y aria2 git; }; }
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
config_fal(){ local cfg="$COMFY/custom_nodes/ComfyUI-fal-API/config.ini"
  [ -z "$FAL_KEY" ] && { echo ">> FAL_KEY não setada — rota nuvem (03) exige; configure em $cfg ou ~/ComfyUI/secrets.env."; return 0; }
  mkdir -p "$(dirname "$cfg")"; printf '[API]\nFAL_KEY = %s\n' "$FAL_KEY" > "$cfg"; chmod 600 "$cfg"; echo ">> FAL_KEY gravada (chmod 600)."; }
get_workflows(){ local d="$COMFY/user/default/workflows/$PROJECT"; mkdir -p "$d"
  for wf in "${WORKFLOWS[@]}"; do wget -nc -P "$d" "$WORKFLOW_BASE/$wf" 2>/dev/null \
    || curl -fsSL --output-dir "$d" --remote-name "$WORKFLOW_BASE/$wf" || echo "   (falhou: $wf)"; done; }

setup_tools; get_nodes; config_fal; get_workflows; get_models
echo "============================================"
echo " mask-edit-cloud pronto. Reinicie o ComfyUI."
echo " GroundingDINO: NÃO renomeie os arquivos. Nós vermelhos? Manager > Install Missing."
echo " Workflows em: $COMFY/user/default/workflows/$PROJECT/"
echo "============================================"
