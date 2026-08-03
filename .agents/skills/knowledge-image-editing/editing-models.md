# Modelos de Edição de Imagem

Repos, arquivos e paths para cada modelo de edição.

## Flux Fill (inpaint/outpaint)
- `flux1-fill-dev.safetensors` → `diffusion_models/`
- clip_l, t5xxl → `text_encoders/`
- `ae.safetensors` → `vae/`

## Flux Kontext
- `flux1-dev-kontext_fp8_scaled.safetensors` → `diffusion_models/`

## Qwen-Image-Edit 2511
- Modelo Qwen + Qwen2.5-VL + VAE (workflow nativo).

## SDXL-Inpainting
- Alternativa rápida/leve para tarefas simples.

## Download
Manifesto completo → `knowledge-runpod-provisioning` (padrão aria2c) ou o `setup.sh` do projeto.

## Referências
- `docs/image-editing.md` §1
- Otimização → [editing-optimization](editing-optimization.md)
