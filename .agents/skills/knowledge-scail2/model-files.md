# SCAIL-2 — Arquivos de Modelo

Paths exatos no ComfyUI para todos os componentes do SCAIL-2.

## Estrutura
```
ComfyUI/models/
├── diffusion_models/  wan2.1_14B_SCAIL_2_fp8_scaled.safetensors   (17.7 GB; fp16/mxfp8 também)
│   └── unet/          SCAIL-2-Q4_K_M.gguf                          (caminho GGUF; Unet Loader do city96)
├── text_encoders/     umt5_xxl_fp8_e4m3fn_scaled.safetensors
├── vae/               wan_2.1_vae.safetensors
├── clip_vision/       clip_vision_h.safetensors
├── sam/               sam3.1_multiplex_fp16.safetensors            (alguns workflows esperam em checkpoints/)
└── loras/             Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors
                       wan2.1_SCAIL_2_DPO_lora_bf16.safetensors     (opcional: corrige mãos/rostos)
```

## Repos
- `Comfy-Org/SCAIL-2` — fp8/fp16/mxfp8 + DPO lora.
- `realrebelai/SCAIL-2_GGUF` — quantizações.
- Componentes Wan: `Comfy-Org/Wan_2.1_ComfyUI_repackaged`.

## Download
Manifesto completo → `knowledge-runpod-provisioning`.

## Referências
- `docs/SCAIL-2.md`
- Escolher quantização → [quantization](quantization.md)
