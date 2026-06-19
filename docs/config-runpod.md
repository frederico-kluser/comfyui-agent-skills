# Script .sh de Provisionamento RunPod para ComfyUI + SCAIL‑2 / Wan 2.1‑2.2 / Flux (Junho 2026)

## TL;DR
- **O artefato está pronto abaixo**: um `provisioning.sh` que segue o padrão real do AI‑Dock (`config/provisioning/default.sh` — arrays de `NODES`/`MODELS` + funções), mas reescrito para velocidade máxima com `aria2c -x16 -s16`, downloads em paralelo, instalação de todos os custom nodes, modelos SCAIL‑2/Wan/Flux nas pastas corretas e **download automático dos workflows .json** para `ComfyUI/user/default/workflows/`.
- **A forma mais rápida e robusta de baixar** modelos grandes no RunPod é `aria2c -x16 -s16` apontando para URLs `…/resolve/main/…` (usuários relatam que o `RUN` do Docker é ~8× mais lento que aria2c); use `aria2c --allow-overwrite=false`/`wget -nc` para **não rebaixar** o que já está no network volume. Atenção: a partir do `huggingface_hub v1.0` a variável `HF_HUB_ENABLE_HF_TRANSFER` foi **descontinuada** (o Hub migrou para o backend Xet) — por isso o script usa aria2c diretamente e não depende de `hf_transfer`.
- **Configure a variável `PROVISIONING_SCRIPT`** apontando para a raw URL de um Gist com este script ao criar o template/pod RunPod (a doc do AI‑Dock diz: *"The URL must point to a plain text file - GitHub Gists/Pastebin (raw) are suitable options"*), ou cole‑o no web terminal/JupyterLab. Para acelerar a inferência (não o setup), instale SageAttention via KJNodes **"Patch Sage Attention"** — e **não** pelo flag global em modelos Wan, que pode gerar saída preta/ruidosa.

---

## Key Findings

1. **Estrutura AI‑Dock confirmada pelo arquivo real.** O `default.sh` declara arrays no topo (`NODES`, `CHECKPOINT_MODELS`, `LORA_MODELS`, `VAE_MODELS`, `CONTROLNET_MODELS`, `ESRGAN_MODELS`…) e funções: `provisioning_start`, `provisioning_get_nodes`, `provisioning_install_python_packages`, `provisioning_get_models`, `provisioning_download`, `provisioning_print_header/_end`. Faz `git clone "${repo}" "${path}" --recursive` e, se existir, `pip install -r requirements.txt`. O download real é uma única linha: `wget -qnc --content-disposition --show-progress -e dotbytes="${3:-4M}" -P "$2" "$1"`. É acionado pela env `PROVISIONING_SCRIPT` (raw URL) ou montando `/opt/ai-dock/bin/provisioning.sh`. Há exemplos de SD3 e FLUX.1 em `config/provisioning`.

2. **Velocidade de download.** `aria2c -x16 -s16 -k1M` é a abordagem mais rápida e confirmada pela comunidade (caso documentado de "8× mais lento" via Docker RUN vs aria2c direto no network volume). A alternativa `hf download` + Xet (`HF_XET_HIGH_PERFORMANCE=1`) é boa para repositórios inteiros, mas o `hf_transfer` antigo foi descontinuado no `huggingface_hub v1.0`. Para downloads gated, passe o token no header `Authorization: Bearer $HF_TOKEN`. Paralelize com `&` + `wait` limitando a ~3 downloads simultâneos para não saturar o disco.

3. **Modelos SCAIL‑2/Wan/Flux** — repos e caminhos exatos validados nas próprias páginas HuggingFace (lista completa em *Details*).

4. **Custom nodes** — repos GitHub validados (kijai, city96, Kosinkadink, rgthree, Fannovel16, PozzettiAndrea, Brobert‑in‑aus). O node `Create SCAIL‑2 Colored Mask`/`SCAIL2ColoredMask` é **core do ComfyUI** (não custom) e exige build **nightly/master**.

5. **Workflows .json** — o ComfyUI moderno salva em `ComfyUI/user/default/workflows/`. Basta `wget`/`curl` de raw URLs.

6/7. **Performance de inferência** — SageAttention 2.2.0 no Linux é **compilado do source** (precisa de nvcc/CUDA toolkit, ~10–30 min); para Wan, usar o node de patch do KJNodes.

---

## Details

### 1. Como funciona o provisioning do AI‑Dock (estrutura real)

A imagem `ghcr.io/ai-dock/comfyui` **não inclui modelos**. Você fornece a env `PROVISIONING_SCRIPT` com uma raw URL (texto puro: Gist/Pastebin). O script é "sourced" pelo `init.sh` depois que os serviços base (sshd, caddy, etc.) sobem. Esqueleto real:

```bash
NODES=( "https://github.com/ltdrdata/ComfyUI-Manager" )
CHECKPOINT_MODELS=( ... ); LORA_MODELS=( ... ); VAE_MODELS=( ... )

function provisioning_start() {
    provisioning_print_header
    provisioning_get_nodes
    provisioning_install_python_packages
    provisioning_get_models "${WORKSPACE}/storage/stable_diffusion/models/ckpt" "${CHECKPOINT_MODELS[@]}"
    provisioning_get_models "${WORKSPACE}/storage/stable_diffusion/models/lora" "${LORA_MODELS[@]}"
    provisioning_print_end
}
function provisioning_get_nodes() {
    for repo in "${NODES[@]}"; do
        dir="${repo##*/}"; path="/opt/ComfyUI/custom_nodes/${dir}"
        if [[ -d $path ]]; then ( cd "$path" && git pull )
        else git clone "${repo}" "${path}" --recursive; fi
        [[ -e "${path}/requirements.txt" ]] && pip install -r "${path}/requirements.txt"
    done
}
function provisioning_download() {
    wget -qnc --content-disposition --show-progress -e dotbytes="${3:-4M}" -P "$2" "$1"
}
provisioning_start
```

Tokens `HF_TOKEN` e `CIVITAI_TOKEN` são lidos como env. **Importante:** no RunPod com network volume, o ComfyUI é movido para `/workspace`; logo os modelos devem ir para `${WORKSPACE}/ComfyUI/models/...` (e não `/opt`). O script abaixo detecta isso.

### 2. Lista exata de modelos (repos HuggingFace + arquivo + pasta destino)

**SCAIL‑2** — repo `Comfy-Org/SCAIL-2`:
| Arquivo (path no repo) | Tamanho | Pasta ComfyUI |
|---|---|---|
| `diffusion_models/wan2.1_14B_SCAIL_2_fp8_scaled.safetensors` | 17.7 GB | `models/diffusion_models/` |
| `diffusion_models/wan2.1_14B_SCAIL_2_fp16.safetensors` | ~32 GB | `models/diffusion_models/` |
| `diffusion_models/wan2.1_14B_SCAIL_2_nvfp4_mxpf8_mix.safetensors` | — | `models/diffusion_models/` |
| `loras/wan2.1_SCAIL_2_DPO_lora_bf16.safetensors` (opcional) | — | `models/loras/` |

**SCAIL‑2 GGUF** — repo `realrebelai/SCAIL-2_GGUF` (carregar com o *Unet Loader (GGUF)* do city96, em `models/unet/`): Q4_K_M ≈ 10.9 GB (daily driver), Q6_K ≈ 13.8 GB, Q8_0 ≈ 17.7 GB. (Há também `vantagewithai/SCAIL-2-GGUF-ComfyUI`.)

**Componentes Wan compartilhados** — repo `Comfy-Org/Wan_2.1_ComfyUI_repackaged`:
- `split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors` → `models/text_encoders/`
- `split_files/vae/wan_2.1_vae.safetensors` → `models/vae/`
- `split_files/clip_vision/clip_vision_h.safetensors` → `models/clip_vision/`

**LoRA de aceleração** — repo `lightx2v/Wan2.1-I2V-14B-480P-StepDistill-CfgDistill-Lightx2v`:
- `loras/Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors` (739 MB) → `models/loras/`

**SAM 3.1** — repo `Comfy-Org/sam3.1`:
- `checkpoints/sam3.1_multiplex_fp16.safetensors` (1.75 GB) → `models/sam/` (alguns workflows esperam em `models/checkpoints/` — o script coloca nas duas ou cria symlink).

**Wan 2.2 14B** — repo `Comfy-Org/Wan_2.2_ComfyUI_Repackaged`:
- `split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors` → `models/diffusion_models/`
- `split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors` → `models/diffusion_models/`
- (T2V: trocar `i2v` por `t2v`; LoRAs lightx2v 4‑steps: `split_files/loras/wan2.2_t2v_lightx2v_4steps_lora_v1.1_{high,low}_noise.safetensors`)

**Flux** — `flux1-dev-fp8.safetensors` (17.2 GB, SHA256 `8e91b6…3d88a`) do repo `Comfy-Org/flux1-dev` → `models/checkpoints/`. Para o pipeline "diffusion_models" separado: `flux1-dev.safetensors` (BFL) + `ae.safetensors` (VAE) + `clip_l.safetensors` + `t5xxl_fp16.safetensors`/`t5xxl_fp8_e4m3fn_scaled.safetensors` em `models/text_encoders/`.

**Estrutura final esperada (SCAIL‑2):**
```
ComfyUI/models/
├── diffusion_models/wan2.1_14B_SCAIL_2_fp8_scaled.safetensors
├── text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors
├── vae/wan_2.1_vae.safetensors
├── clip_vision/clip_vision_h.safetensors
├── loras/Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors
└── sam/sam3.1_multiplex_fp16.safetensors
```

### 3. Custom nodes (repos Git)
| Node | Repo | Instalação |
|---|---|---|
| ComfyUI‑Manager | `ltdrdata/ComfyUI-Manager` | requirements.txt |
| WanVideoWrapper | `kijai/ComfyUI-WanVideoWrapper` | requirements.txt |
| KJNodes | `kijai/ComfyUI-KJNodes` | requirements.txt |
| SCAIL‑Pose | `kijai/ComfyUI-SCAIL-Pose` | requirements.txt |
| ComfyUI‑GGUF | `city96/ComfyUI-GGUF` | requirements.txt |
| VideoHelperSuite | `Kosinkadink/ComfyUI-VideoHelperSuite` | requirements.txt |
| rgthree | `rgthree/rgthree-comfy` | requirements.txt |
| Frame‑Interpolation | `Fannovel16/ComfyUI-Frame-Interpolation` | requirements.txt + install.py |
| SAM3 | `PozzettiAndrea/ComfyUI-SAM3` | requirements.txt + `python install.py` |
| scail‑auto‑extend | `Brobert-in-aus/scail-auto-extend` | (sem requirements pesados) |

> **Aviso crítico:** o node `Create SCAIL‑2 Colored Mask` (antigo `SCAIL2ColoredMask`) **não é custom** — é core do ComfyUI, mergeado em junho/2026. Se aparecer vermelho ("missing"), **atualize o ComfyUI para o commit nightly/master**. Os example workflows do SCAIL também usam `ComfyUI_essentials` e (opcional) `ComfyUI-RMBG`.

### 4. Como anexar/baixar os workflows .json automaticamente
O ComfyUI moderno salva e procura workflows do usuário em **`ComfyUI/user/default/workflows/`**. O script cria a pasta e faz `wget -nc` de raw URLs. Fontes prontas:
- **WanVideoWrapper (kijai)**: `https://github.com/kijai/ComfyUI-WanVideoWrapper/raw/refs/heads/main/example_workflows/wanvideo_2_1_14B_SCAIL_pose_control_example_01.json`
- **scail‑auto‑extend (Brobert‑in‑aus)**: `SCAIL Auto Extend V3.json` (no repo)
- **SCAIL‑Pose (kijai)**: `example_workflows/SCAIL_preprocess_example_01.json`
- Tutoriais com JSON pronto: Next Diffusion, `comfyui.nomadoor.net`, RunComfy.
- **Melhor prática:** hospede seus próprios workflows num Gist/repo e baixe via raw URL — exatamente como o `kingaigfcash/aigfcash-runpod-template` faz (pasta `/workflows/`).

### 5. Dependências de performance (SageAttention/Triton/Flash — Linux)
Confirmado via subagente (fontes: thu‑ml/SageAttention README e issues #219/#289, woct0rdho, mobcat40):
- **Triton (Linux):** `pip install triton` (geralmente já vem com o PyTorch); para fixar, casar a minor: torch 2.8→triton 3.4, 2.9→3.5.
- **SageAttention 2.2.0 (Linux):** **não há wheels Linux prebuilt gratuitas** — compile do source:
  ```bash
  pip install sageattention==2.2.0 --no-build-isolation   # precisa de nvcc/CUDA toolkit ≥12.8 p/ Blackwell
  # ou: git clone https://github.com/thu-ml/SageAttention && cd SageAttention
  #     export EXT_PARALLEL=4 NVCC_APPEND_FLAGS="--threads 8" MAX_JOBS=8 && python setup.py install
  ```
  Demora ~10–30 min (CPU/RAM‑bound; `MAX_JOBS` alto em pod com pouca RAM causa OOM). Em templates RunPod sem `nvcc` (só runtime) a build falha — use imagem `-devel` ou instale o toolkit. **Dica:** faça `pip wheel .` uma vez e guarde o `.whl` para reusar em pods futuros.
- **Uso correto em Wan:** **não** use o flag global `--use-sage-attention` (overflow → vídeo preto/ruidoso em Wan/Qwen). Instale **ComfyUI‑KJNodes** e use o node **`PatchSageAttentionKJ`** com backend **`sageattn_qk_int8_pv_fp16_cuda`**.
- **Flash‑Attention:** opcional para Wan (ganho marginal). Se quiser, **não** use `pip install flash-attn` puro no Blackwell (compila e falha) — use wheel Linux prebuilt casando torch/cuda/cxx11abi (ex.: releases `mjun0812/flash-attention-prebuild-wheels`).

### 6. Otimizações de velocidade aplicadas no script
- `aria2c -x16 -s16 -k1M` (16 conexões) em vez de wget single‑thread.
- Downloads grandes **em paralelo** (`&` + `wait -n`, máx. 3 simultâneos).
- **Nodes leves primeiro** (git clone é rápido), modelos pesados depois/em paralelo.
- `--allow-overwrite=false` + `aria2c -c` (continue) ⇒ **não rebaixa** o que já está no network volume e **resume** downloads interrompidos.
- SageAttention é a **última** etapa (opcional, lenta) e não bloqueia o ComfyUI subir.
- Flag de inferência recomendado no `COMFYUI_ARGS`: `--fast` (ou `--highvram` em GPUs ≥48 GB).

---

## O SCRIPT COMPLETO (`provisioning.sh`)

```bash
#!/usr/bin/env bash
# provisioning.sh — RunPod / AI-Dock ComfyUI
# SCAIL-2 + Wan 2.1/2.2 14B + Flux — setup rápido (junho 2026)
# Uso: defina a env PROVISIONING_SCRIPT apontando p/ a raw URL deste arquivo,
#      OU rode manualmente:  bash provisioning.sh
set -Euo pipefail

# ============ CONFIG ============
# Detecta o ComfyUI (network volume tem prioridade)
if   [ -d "${WORKSPACE:-/workspace}/ComfyUI" ]; then COMFY="${WORKSPACE:-/workspace}/ComfyUI"
elif [ -d "/opt/ComfyUI" ];                      then COMFY="/opt/ComfyUI"
else COMFY="${WORKSPACE:-/workspace}/ComfyUI"; fi
echo ">> ComfyUI em: $COMFY"

HF_TOKEN="${HF_TOKEN:-}"
CIVITAI_TOKEN="${CIVITAI_TOKEN:-}"
PIP="python -m pip install --no-cache-dir"
PAR=3   # downloads simultâneos

# ---- Custom nodes ----
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

# ---- Modelos: "URL|subpasta_em_models" ----
MODELS=(
  # SCAIL-2 (escolha fp8 OU gguf; aqui fp8_scaled)
  "https://huggingface.co/Comfy-Org/SCAIL-2/resolve/main/diffusion_models/wan2.1_14B_SCAIL_2_fp8_scaled.safetensors|diffusion_models"
  "https://huggingface.co/Comfy-Org/SCAIL-2/resolve/main/loras/wan2.1_SCAIL_2_DPO_lora_bf16.safetensors|loras"
  # Componentes Wan compartilhados
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors|text_encoders"
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors|vae"
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors|clip_vision"
  # LoRA aceleração (4 passos)
  "https://huggingface.co/lightx2v/Wan2.1-I2V-14B-480P-StepDistill-CfgDistill-Lightx2v/resolve/main/loras/Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors|loras"
  # SAM 3.1
  "https://huggingface.co/Comfy-Org/sam3.1/resolve/main/checkpoints/sam3.1_multiplex_fp16.safetensors|sam"
  # Wan 2.2 14B I2V (high + low noise)
  "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors|diffusion_models"
  "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors|diffusion_models"
  # Flux (fp8 all-in-one)
  "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors|checkpoints"
)

# ---- Workflows .json ----
WORKFLOWS=(
  "https://github.com/kijai/ComfyUI-WanVideoWrapper/raw/refs/heads/main/example_workflows/wanvideo_2_1_14B_SCAIL_pose_control_example_01.json"
  "https://github.com/kijai/ComfyUI-SCAIL-Pose/raw/refs/heads/main/example_workflows/SCAIL_preprocess_example_01.json"
  # Adicione AQUI seus próprios workflows (raw URL de um Gist/repo):
  # "https://gist.githubusercontent.com/SEU_USER/SEU_GIST/raw/meu_workflow.json"
)

# ============ FUNÇÕES ============
setup_tools() {
  echo ">> Instalando ferramentas (aria2, git)..."
  if ! command -v aria2c >/dev/null 2>&1; then
    apt-get update -y && apt-get install -y aria2 git git-lfs
  fi
}

update_comfy() {
  # SCAIL-2 exige ComfyUI nightly/master
  if [ -d "$COMFY/.git" ]; then
    echo ">> Atualizando ComfyUI (nightly p/ SCAIL-2)..."
    ( cd "$COMFY" && git pull --ff-only || true )
    [ -f "$COMFY/requirements.txt" ] && $PIP -r "$COMFY/requirements.txt" || true
  fi
}

get_nodes() {
  echo ">> Instalando custom nodes..."
  mkdir -p "$COMFY/custom_nodes"
  for repo in "${NODES[@]}"; do
    dir="${repo##*/}"; path="$COMFY/custom_nodes/$dir"
    if [ ! -d "$path" ]; then
      echo "   clonando $dir"; git clone --recursive "$repo" "$path" || continue
    else
      ( cd "$path" && git pull --ff-only || true )
    fi
    [ -f "$path/requirements.txt" ] && $PIP -r "$path/requirements.txt" || true
    [ -f "$path/install.py" ] && ( cd "$path" && python install.py || true )
  done
}

# Download de 1 modelo (16 conexões, com header de token p/ gated)
dl_one() {
  local url="$1" dest="$COMFY/models/$2"
  mkdir -p "$dest"
  local fname; fname="$(basename "${url%%\?*}")"
  if [ -f "$dest/$fname" ]; then echo "   [skip] $fname já existe"; return 0; fi
  local hdr=()
  if [[ "$url" == *huggingface.co* ]] && [ -n "$HF_TOKEN" ]; then
    hdr=(--header="Authorization: Bearer $HF_TOKEN")
  fi
  if [[ "$url" == *civitai.com* ]] && [ -n "$CIVITAI_TOKEN" ]; then
    url="${url}?token=${CIVITAI_TOKEN}"
  fi
  echo "   baixando $fname -> models/$2"
  aria2c -c -x16 -s16 -k1M --auto-file-renaming=false --allow-overwrite=false \
         --console-log-level=warn --summary-interval=0 \
         "${hdr[@]}" -d "$dest" -o "$fname" "$url" \
    || wget -nc --content-disposition "${hdr[@]/--header=/--header=}" -P "$dest" "$url"
}

get_models() {
  echo ">> Baixando modelos (paralelo: $PAR)..."
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

get_workflows() {
  echo ">> Baixando workflows .json..."
  local wfdir="$COMFY/user/default/workflows"
  mkdir -p "$wfdir"
  for w in "${WORKFLOWS[@]}"; do
    wget -nc --content-disposition -P "$wfdir" "$w" || \
      curl -fL --remote-name --output-dir "$wfdir" "$w" || true
  done
}

install_perf() {
  echo ">> (Opcional) SageAttention/Triton p/ acelerar inferência..."
  $PIP triton || true
  if command -v nvcc >/dev/null 2>&1; then
    $PIP sageattention==2.2.0 --no-build-isolation \
      || echo "   SageAttention falhou (build) — siga sem ele ou use wheel prebuilt."
  else
    echo "   nvcc ausente: pulei SageAttention. Use imagem CUDA -devel p/ compilar."
  fi
  echo "   Em Wan: use o node KJNodes 'Patch Sage Attention' (sageattn_qk_int8_pv_fp16_cuda),"
  echo "   NÃO o flag global --use-sage-attention."
}

main() {
  setup_tools
  update_comfy
  get_nodes            # leve e rápido primeiro
  get_workflows        # rápido
  get_models           # pesado, em paralelo
  install_perf         # lento, por último e opcional
  echo "============================================"
  echo " Provisionamento COMPLETO. Reinicie o ComfyUI"
  echo " (Manager > Restart) e pressione 'R' p/ recarregar modelos."
  echo "============================================"
}
main
```

**Como variar:** para usar **GGUF** em vez de fp8, troque a linha do SCAIL‑2 por `https://huggingface.co/realrebelai/SCAIL-2_GGUF/resolve/main/SCAIL-2-Q4_K_M.gguf|unet`. Para **Wan 2.2 T2V**, troque `i2v`→`t2v`. Para **Flux com text encoders separados**, adicione `ae.safetensors` (vae) e `clip_l`/`t5xxl` (text_encoders).

---

## Recommendations

**Etapa 1 — Provisionar (escolha um caminho):**
1. **Via template (recomendado):** hospede o script num **Gist público** e copie a *raw URL*. No template RunPod do AI‑Dock/ComfyUI, defina `PROVISIONING_SCRIPT=<raw_url>`, `HF_TOKEN`, `CIVITAI_TOKEN` (se precisar de gated), e `COMFYUI_ARGS=--fast` (ou `--highvram`). Volume disk ≥ **200 GB**, container disk ≥ 30 GB, CUDA **12.8**.
2. **Manual:** abra o web terminal/JupyterLab, `wget <raw_url> -O provisioning.sh && bash provisioning.sh`.

**Etapa 2 — Hardware/modelos:**
- Comece com **SCAIL‑2 fp8_scaled** (17.7 GB) em GPU ≥ 24 GB (RTX 4090/5090). Se a VRAM apertar, troque para **GGUF Q4_K_M** (~10.9 GB).
- Para vídeos longos, use o node **SCAIL Auto Extend** (limite do modelo: 81 frames/passo; extensões de 76 frames novos).

**Etapa 3 — Acelerar inferência (depois que tudo funcionar):**
- Instale SageAttention **só** se a imagem tiver `nvcc`; em Wan, ative pelo **node KJNodes**, não pelo flag global.
- Largura/altura **divisíveis por 32** no SCAIL‑2 (a doc fala em 16, mas o pose/mask roda em meia‑resolução → exige 32); 832×480 é um bom início 480p.

**Benchmarks que mudam a decisão:**
- Se o download estiver **< ~200 MB/s** com aria2c, o gargalo é o disco do pod — destrua e recrie em outro datacenter.
- Se a build do SageAttention passar de ~30 min ou der OOM, **baixe `MAX_JOBS`** ou pule (o ganho é ~35% no sampling; não é pré‑requisito).
- Se o node `Create SCAIL‑2 Colored Mask` aparecer vermelho, **o ComfyUI não está nightly** → rode `git pull` em `$COMFY` e reinicie.

---

## Caveats
- **SCAIL‑2 é muito recente (merge em junho/2026).** Os repos `Comfy-Org/SCAIL-2`, `Comfy-Org/sam3.1` e os nodes core ainda evoluem rápido; nomes de arquivos/branches podem mudar — confira a aba *Files* do HuggingFace antes de rodar em produção. Não há, na data desta pesquisa, um workflow "oficial estável" único publicado junto ao modelo (o teste inicial está no PR do ComfyUI e em exemplos da comunidade — Next Diffusion, nomadoor, kijai).
- **`HF_HUB_ENABLE_HF_TRANSFER` foi descontinuado** no `huggingface_hub v1.0` (Hub migrou para Xet; >77 PB / 6 milhões de repos migrados). Por isso o script usa `aria2c` direto. Se preferir `hf download`, use `HF_XET_HIGH_PERFORMANCE=1` em máquinas com ≥64 GB RAM.
- **Pasta do SAM:** alguns workflows esperam `models/sam/`, outros `models/checkpoints/` (a doc da nomadoor mostra em `checkpoints/`). O script coloca em `sam/` e cria symlink em `checkpoints/` para cobrir ambos.
- **SageAttention no Linux exige nvcc** (CUDA toolkit ≥12.8 para Blackwell). Templates RunPod só‑runtime falham na build; use imagem `-devel` ou cacheie seu próprio `.whl`. O tempo de compilação (~10–30 min) é uma estimativa informada — depende de cores/RAM do pod, não há benchmark único oficial.
- **Tamanho total dos downloads** com a lista completa (SCAIL‑2 fp8 + Wan 2.2 high/low + Flux fp8 + auxiliares) passa de **~90 GB** — dimensione o network volume e lembre que banda no RunPod é cobrada por TB em alguns casos. Comente o que não for usar.
- **CivitAI via script:** há relato de falha de download no AI‑Dock com `CIVITAI_TOKEN` mesmo quando o token está correto (HuggingFace funciona) — se precisar de LoRAs do CivitAI, valide manualmente o token/endpoint.