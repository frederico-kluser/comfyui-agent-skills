---
name: knowledge-image-editing
description: >-
  Conhecimento de edição de imagem no ComfyUI: inpainting (VAE Encode for Inpainting vs Set Latent
  Noise Mask vs InpaintModelConditioning, denoise, feathering, Differential Diffusion, Inpaint
  Crop&Stitch), edição por instrução sem máscara (Flux Kontext, Qwen-Image-Edit), composição e os
  modelos (Flux Fill/Kontext/Qwen/Flux.2/Z-Image/SDXL) + otimização. Use ao editar/inpaint/alterar
  uma imagem, trocar objeto/cor/fundo por máscara ou por instrução — mesmo sem citar a skill.
  Selecionar a região → knowledge-image-masking; recolar via código/API → knowledge-comfyui-api.
metadata:
  version: 0.2.0
  type: knowledge
---
# ComfyUI — Edição de Imagem (inpaint + instrução)

Duas filosofias que se combinam: (a) **máscara + denoise** (inpainting clássico) e (b) **edição por
instrução textual** (Flux Kontext, Qwen-Image-Edit) que dispensa máscara para muitas tarefas.

## Quando usar
"Editar/alterar/inpaint uma imagem", "trocar objeto/cor/fundo", "mudar X para Y na foto", escolher
o nó de máscara ou o modelo de edição, corrigir bordas/cor pós-inpaint.

## Técnicas (um arquivo por técnica)

| Técnica | Arquivo | O que cobre |
|---------|---------|-------------|
| Encodar a máscara | [inpainting-mask-encode.md](inpainting-mask-encode.md) | VAE Encode (for Inpainting) vs Set Latent Noise Mask vs InpaintModelConditioning |
| Força e bordas | [inpainting-denoise-borders.md](inpainting-denoise-borders.md) | denoise, grow mask, blur, Differential Diffusion |
| Crop & Stitch | [crop-stitch.md](crop-stitch.md) | Inpaint Crop → sampling → Inpaint Stitch |
| Edição por instrução | [instruction-editing.md](instruction-editing.md) | Flux Kontext, Qwen-Image-Edit (sem máscara) |
| Modelos | [editing-models.md](editing-models.md) | Flux Fill, Kontext, Qwen, SDXL — paths e repos |
| Otimização | [editing-optimization.md](editing-optimization.md) | Samplers, fp8/GGUF, SageAttention, erros comuns |

## Referências (nível 3)
- `docs/image-editing.md` (fonte completa). Projetos: `workflows-cloud/inpaint-region-cropstitch`, `instruction-edit-kontext`, `qwen-image-edit`, `outpaint-extend`.
- Cadeia: selecionar região → `knowledge-image-masking`; recolar via código/API → `knowledge-comfyui-api`; upscale/relight/controlnet → `knowledge-image-enhance`.

## Evolução
Append em `LEARNINGS.md` ao descobrir um nó/param melhor, um modelo novo, ou um anti-padrão (bordas/cor). Destile
no corpo se estável (`version++`). Diff git p/ revisão.
