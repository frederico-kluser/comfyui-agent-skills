#!/usr/bin/env bash
# setup.sh — scail2-native-3rdparty/tryoff (Clothing Transfer + SCAIL-2 Animation)
# RunPod/ComfyUI — rode como ROOT:  bash setup.sh
# Dois workflows sequenciais: (1) tryoff-preprocess (extrai roupa do vídeo → aplica na foto),
# (2) scail2-animation (SCAIL-2 com referência processada).
# SCAIL2ColoredMask/WanSCAILToVideo são CORE → garante ComfyUI nightly.
set -Euo pipefail
if   [ -d "${WORKSPACE:-/workspace}/ComfyUI" ]; then COMFY="${WORKSPACE:-/workspace}/ComfyUI"
elif [ -d "/opt/ComfyUI" ];                      then COMFY="/opt/ComfyUI"
else COMFY="${WORKSPACE:-/workspace}/ComfyUI"; fi
echo ">> ComfyUI em: $COMFY"
HF_TOKEN="${HF_TOKEN:-}"; PIP="python -m pip install --no-cache-dir"; PAR=3

WORKFLOW_BASE="https://raw.githubusercontent.com/frederico-kluser/comfyui-agent-skills/main/workflows/scail2-native-3rdparty/tryoff"
WORKFLOWS=(
  "tryoff-preprocess.json"
  "scail2-animation.json"
)

# === Custom Nodes ===
NODES=(
  # SCAIL-2 + utilitários
  "https://github.com/ltdrdata/ComfyUI-Manager"
  "https://github.com/PozzettiAndrea/ComfyUI-SAM3"
  "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite"
  "https://github.com/Fannovel16/ComfyUI-Frame-Interpolation"
  "https://github.com/kijai/ComfyUI-KJNodes"
  "https://github.com/rgthree/rgthree-comfy"
  "https://github.com/city96/ComfyUI-GGUF"
  # TryOff + segmentação
  "https://github.com/asutermo/ComfyUI-Flux-TryOff"
  "https://github.com/chflame163/ComfyUI_LayerStyle"
)

# === Modelos (aria2c: arquivo único) ===
# formato: "URL|pasta_relativa_dentro_de_models"
MODELS=(
  # SCAIL-2
  "https://huggingface.co/Comfy-Org/SCAIL-2/resolve/main/diffusion_models/wan2.1_14B_SCAIL_2_fp8_scaled.safetensors|diffusion_models"
  "https://huggingface.co/lightx2v/Wan2.1-I2V-14B-480P-StepDistill-CfgDistill-Lightx2v/resolve/main/loras/Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors|loras"
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors|text_encoders"
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors|vae"
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors|clip_vision"
  "https://huggingface.co/Comfy-Org/sam3.1/resolve/main/checkpoints/sam3.1_multiplex_fp16.safetensors|checkpoints"
)

# === Modelos via git clone (repositórios HF LFS) ===
clone_hf_repo() {
  local repo="$1" dest="$2"
  if [ -d "$dest/.git" ]; then
    echo "   [skip] $dest já existe"
  else
    echo "   git clone $repo → $dest"
    git clone "https://huggingface.co/$repo" "$dest" || echo "   (falhou: verifique HF_TOKEN ou baixe manualmente)"
  fi
}

setup_tools(){ command -v aria2c >/dev/null 2>&1 || { apt-get update -y && apt-get install -y aria2 git git-lfs; }; }
update_comfy(){ if [ -d "$COMFY/.git" ]; then echo ">> nightly p/ nós core SCAIL-2..."; ( cd "$COMFY" && git pull --ff-only || true ); [ -f "$COMFY/requirements.txt" ] && $PIP -r "$COMFY/requirements.txt" || true; else echo "   AVISO: garanta build nightly/master."; fi; }
get_nodes(){ mkdir -p "$COMFY/custom_nodes"; for repo in "${NODES[@]}"; do dir="${repo##*/}"; path="$COMFY/custom_nodes/$dir"
  if [ ! -d "$path" ]; then git clone --recursive "$repo" "$path" || continue; else ( cd "$path" && git pull --ff-only || true ); fi
  [ -f "$path/requirements.txt" ] && $PIP -r "$path/requirements.txt" || true; [ -f "$path/install.py" ] && ( cd "$path" && python install.py || true ); done; }
dl_one(){ local url="$1" dest="$COMFY/models/$2"; mkdir -p "$dest"; local fname; fname="$(basename "${url%%\?*}")"
  [ -f "$dest/$fname" ] && { echo "   [skip] $fname"; return 0; }
  local hdr=(); [[ "$url" == *huggingface.co* && -n "$HF_TOKEN" ]] && hdr=(--header="Authorization: Bearer $HF_TOKEN")
  echo "   baixando $fname -> models/$2"
  aria2c -c -x16 -s16 -k1M --auto-file-renaming=false --allow-overwrite=false --console-log-level=warn --summary-interval=0 \
         "${hdr[@]}" -d "$dest" -o "$fname" "$url" || wget -nc --content-disposition "${hdr[@]}" -P "$dest" "$url" || echo "   (falhou: confirme no HF)"; }
get_models(){ for e in "${MODELS[@]}"; do dl_one "${e%%|*}" "${e##*|}" & while [ "$(jobs -rp | wc -l)" -ge "$PAR" ]; do wait -n; done; done; wait; }
get_workflows(){ local d="$COMFY/user/default/workflows"; mkdir -p "$d"; for wf in "${WORKFLOWS[@]}"; do wget -nc -P "$d" "$WORKFLOW_BASE/$wf" || curl -fL --output-dir "$d" --remote-name "$WORKFLOW_BASE/$wf" || true; done; }
get_hf_repos(){
  clone_hf_repo "mattmdjaga/segformer_b2_clothes" "$COMFY/models/segformer_b2_clothes"
  clone_hf_repo "xiaozaa/cat-tryoff-flux"        "$COMFY/models/cat-tryoff-flux"
  # FLUX.1-dev — TryOffFluxFillModelNode espera diretório diffusers-format em models/checkpoints/FLUX.1-dev/
  # (~23 GB download. O nó tenta baixar automaticamente se ausente, mas pode ser lento/timeout.)
  if [ ! -d "$COMFY/models/checkpoints/FLUX.1-dev" ]; then
    echo ">> Baixando FLUX.1-dev (~23 GB, pode demorar)..."
    clone_hf_repo "black-forest-labs/FLUX.1-dev" "$COMFY/models/checkpoints/FLUX.1-dev" || echo "   (se falhar, o nó TryOffFluxFillModelNode fará download automático)"
  fi
}

setup_tools; update_comfy; get_nodes; get_workflows; get_models; get_hf_repos
echo "============================================"
echo " scail2-native-3rdparty/tryoff pronto."
echo ""
echo " Workflows em: $COMFY/user/default/workflows/"
echo "  1. tryoff-preprocess.json  — extrai roupa do vídeo, aplica na foto"
echo "  2. scail2-animation.json   — anima com SCAIL-2 (referência processada)"
echo ""
echo " Execute o workflow 1 PRIMEIRO. Depois carregue a saída"
echo " (reference_processed_*.png) no LoadImage do workflow 2."
echo ""
echo " ⚠️  Rode os workflows SEQUENCIALMENTE (feche/recarregue entre eles"
echo "    para liberar VRAM). GPU min: 24 GB (RTX 4090)."
echo " ⚠️  FLUX.1-dev (~23 GB) pode demorar no primeiro download."
echo " Reinicie o ComfyUI após a instalação."
echo "============================================"
