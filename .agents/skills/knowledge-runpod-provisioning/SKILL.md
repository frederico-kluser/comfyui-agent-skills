---
name: knowledge-runpod-provisioning
description: >-
  Setup reproduzível do ComfyUI no RunPod para SCAIL-2/Wan/Flux: o provisioning.sh (padrão AI-Dock + aria2c
  -x16), o manifesto exato de modelos (repo HuggingFace → arquivo → pasta), a lista de custom nodes, o
  download automático de workflows e os caveats (SageAttention, ComfyUI nightly, HF_TOKEN, pasta do SAM).
  Use ao provisionar um pod, baixar/atualizar modelos, ou editar o script — mesmo sem citar a skill. Traz
  scripts/provisioning.sh pronto. Para escolher GPU/custo, veja knowledge-runpod-infra.
metadata:
  version: 0.1.0
  type: knowledge
---
# RunPod — Provisionamento (ComfyUI + modelos)

Setup automatizado e reproduzível. O artefato pronto é `scripts/provisioning.sh` (nesta skill): instala
custom nodes, baixa modelos nas pastas certas com `aria2c -x16 -s16` e baixa workflows.

## Quando usar
"Provisionar/subir o pod", "baixar os modelos", "instalar os custom nodes", "configurar o ComfyUI", editar/variar
o script (GGUF vs fp8, Wan 2.2 t2v, Flux com encoders separados).

## Como rodar (3 caminhos)
1. **Template (recomendado)**: hospede `scripts/provisioning.sh` num Gist público; no template AI-Dock/ComfyUI
   defina env `PROVISIONING_SCRIPT=<raw_url>`, `HF_TOKEN`, `CIVITAI_TOKEN`, `COMFYUI_ARGS=--fast`. Volume ≥200GB,
   container ≥30GB, CUDA 12.8.
2. **Manual**: web terminal/JupyterLab → `wget <raw_url> -O provisioning.sh && bash provisioning.sh`.
3. **One-liner**: geradores tipo `deploy.promptingpixels.com`.

## Manifesto de modelos (repo → arquivo → pasta)
- **SCAIL-2** `Comfy-Org/SCAIL-2`: `diffusion_models/wan2.1_14B_SCAIL_2_fp8_scaled.safetensors` (17.7GB) →
  `models/diffusion_models/`; `loras/wan2.1_SCAIL_2_DPO_lora_bf16.safetensors` → `models/loras/`. GGUF:
  `realrebelai/SCAIL-2_GGUF` → `models/unet/` (Q4_K_M 10.9GB daily driver).
- **Componentes Wan** `Comfy-Org/Wan_2.1_ComfyUI_repackaged/split_files/`: `text_encoders/umt5_xxl_fp8_e4m3fn_scaled`
  → `text_encoders/`; `vae/wan_2.1_vae` → `vae/`; `clip_vision/clip_vision_h` → `clip_vision/`.
- **LoRA aceleração** `lightx2v/Wan2.1-I2V-14B-480P-StepDistill-CfgDistill-Lightx2v`:
  `loras/Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors` (739MB) → `loras/`.
- **SAM 3.1** `Comfy-Org/sam3.1`: `checkpoints/sam3.1_multiplex_fp16.safetensors` (1.75GB) → `models/sam/`
  **e** symlink em `checkpoints/` (workflows variam quanto à pasta).
- **Wan 2.2 14B** `Comfy-Org/Wan_2.2_ComfyUI_Repackaged/split_files/diffusion_models/`:
  `wan2.2_i2v_{high,low}_noise_14B_fp8_scaled` → `diffusion_models/` (T2V: troque `i2v`→`t2v`).
- **Flux** `Comfy-Org/flux1-dev/flux1-dev-fp8.safetensors` (17.2GB) → `models/checkpoints/`.
- ⚠️ A lista completa passa de **~90GB** — comente o que não usar e dimensione o volume.

## Custom nodes (repos)
`ltdrdata/ComfyUI-Manager`, `kijai/ComfyUI-WanVideoWrapper`, `kijai/ComfyUI-KJNodes`, `kijai/ComfyUI-SCAIL-Pose`,
`city96/ComfyUI-GGUF`, `Kosinkadink/ComfyUI-VideoHelperSuite`, `rgthree/rgthree-comfy`,
`Fannovel16/ComfyUI-Frame-Interpolation`, `PozzettiAndrea/ComfyUI-SAM3`, `cubiq/ComfyUI_essentials`,
`Brobert-in-aus/scail-auto-extend`.

## Caveats (críticos)
- `Create SCAIL-2 Colored Mask` é **core**, não custom → exige ComfyUI **nightly/master** (`git pull` em `$COMFY`).
- `HF_HUB_ENABLE_HF_TRANSFER` foi **descontinuado** (huggingface_hub v1.0 migrou p/ backend Xet). O script usa
  `aria2c` direto; `aria2c --allow-overwrite=false` + `-c` **não rebaixa** o que já está no volume e resume downloads.
- **SageAttention** (Linux) compila do source (~10–30min, precisa de `nvcc`/CUDA ≥12.8). Em Wan, ative pelo node
  KJNodes **`PatchSageAttentionKJ`** (`sageattn_qk_int8_pv_fp16_cuda`) — **nunca** o flag global
  `--use-sage-attention` (→ vídeo preto/ruidoso). Cacheie o `.whl` para reusar.
- Token HF/CivitAI errado → download parcial **silencioso**. CivitAI via script às vezes falha mesmo com token correto.
- Largura/altura divisíveis por **32** no SCAIL-2 (o pose/mask roda em meia-resolução).

## Variar o script
GGUF em vez de fp8: troque a linha SCAIL-2 por `realrebelai/SCAIL-2_GGUF/.../SCAIL-2-Q4_K_M.gguf|unet`. Wan 2.2
T2V: `i2v`→`t2v`. Flux com encoders separados: adicione `ae.safetensors|vae` + `clip_l`/`t5xxl|text_encoders`.

## Referências (nível 3, sob demanda)
- `scripts/provisioning.sh` — script completo e editável (arrays `NODES`/`MODELS`/`WORKFLOWS`).
- `docs/config-runpod.md` — guia completo (estrutura AI-Dock, velocidade, SageAttention).
- Cadeia: subir o pod → `task-launch-runpod-pod`; GPU/custo → `knowledge-runpod-infra`.

## Evolução
Append em `LEARNINGS.md` quando um repo/arquivo/branch de modelo mudar (confira a aba *Files* do HF), quando um
node novo for necessário, ou quando um download falhar. Atualize `scripts/provisioning.sh` junto. Destile se
estável (`version++`). Diff git para revisão.
