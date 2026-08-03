# RunPod — Caveats de Provisionamento

Armadilhas críticas ao configurar o ambiente.

## ComfyUI nightly
`Create SCAIL-2 Colored Mask` é **core**, não custom → exige ComfyUI **nightly/master** (`git pull` em `$COMFY`).

## Download de modelos
- `HF_HUB_ENABLE_HF_TRANSFER` foi **descontinuado** (huggingface_hub v1.0 migrou para backend Xet).
- O script usa `aria2c` direto; `aria2c --allow-overwrite=false` + `-c` **não rebaixa** o que já está no volume e resume downloads.
- Token HF/CivitAI errado → download parcial **silencioso**.
- CivitAI via script às vezes falha mesmo com token correto.

## SageAttention (Linux)
Compila do source (~10–30min, precisa de `nvcc`/CUDA ≥12.8).
- Em Wan, ative pelo node KJNodes **`PatchSageAttentionKJ`** (`sageattn_qk_int8_pv_fp16_cuda`).
- **Nunca** o flag global `--use-sage-attention` (→ vídeo preto/ruidoso).
- Cacheie o `.whl` para reusar.

## Resolução SCAIL-2
Largura/altura divisíveis por **32** (o pose/mask roda em meia-resolução).

## Variar o script
- GGUF em vez de fp8: troque a linha SCAIL-2 por `realrebelai/SCAIL-2_GGUF/.../SCAIL-2-Q4_K_M.gguf|unet`.
- Wan 2.2 T2V: `i2v`→`t2v`.
- Flux com encoders separados: adicione `ae.safetensors|vae` + `clip_l`/`t5xxl|text_encoders`.

## Referências
- `scripts/provisioning.sh`
- `docs/config-runpod.md`
- GPU/custo → `knowledge-runpod-infra`
