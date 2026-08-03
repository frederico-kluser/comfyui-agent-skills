# RunPod — Manifesto de Modelos

Repo → arquivo → pasta. ⚠️ A lista completa passa de **~90GB** — comente o que não usar.

## SCAIL-2
- `Comfy-Org/SCAIL-2`: `diffusion_models/wan2.1_14B_SCAIL_2_fp8_scaled.safetensors` (17.7GB) → `models/diffusion_models/`
- `loras/wan2.1_SCAIL_2_DPO_lora_bf16.safetensors` → `models/loras/`
- GGUF: `realrebelai/SCAIL-2_GGUF` → `models/unet/` (Q4_K_M 10.9GB daily driver)

## Componentes Wan
`Comfy-Org/Wan_2.1_ComfyUI_repackaged/split_files/`:
- `text_encoders/umt5_xxl_fp8_e4m3fn_scaled` → `text_encoders/`
- `vae/wan_2.1_vae` → `vae/`
- `clip_vision/clip_vision_h` → `clip_vision/`

## LoRA aceleração
`lightx2v/Wan2.1-I2V-14B-480P-StepDistill-CfgDistill-Lightx2v`:
`loras/Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors` (739MB) → `loras/`.

## SAM 3.1
`Comfy-Org/sam3.1`: `checkpoints/sam3.1_multiplex_fp16.safetensors` (1.75GB) → `models/sam/`
**e** symlink em `checkpoints/` (workflows variam quanto à pasta).

## Wan 2.2 14B
`Comfy-Org/Wan_2.2_ComfyUI_Repackaged/split_files/diffusion_models/`:
`wan2.2_i2v_{high,low}_noise_14B_fp8_scaled` → `diffusion_models/`
(T2V: troque `i2v`→`t2v`).

## Flux
`Comfy-Org/flux1-dev/flux1-dev-fp8.safetensors` (17.2GB) → `models/checkpoints/`.

## Referências
- Provisionar → [provisioning-script](provisioning-script.md)
- GPU/custo → `knowledge-runpod-infra`
