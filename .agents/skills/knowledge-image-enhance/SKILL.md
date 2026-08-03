---
name: knowledge-image-enhance
description: >-
  Conhecimento de realce e controle de imagem no ComfyUI: upscaling (ESRGAN/4x-UltraSharp, Ultimate SD
  Upscale, SUPIR), outpainting (Pad/Extend for Outpainting + Flux Fill), relighting (IC-Light), ControlNet
  (canny/depth/openpose/tile), IPAdapter e PuLID/InstantID (estilo e consistência facial), detailers
  (FaceDetailer) e remoção de fundo (RMBG/BiRefNet/SAM3). Use ao ampliar, estender, reiluminar, controlar
  estrutura/pose, transferir estilo ou remover fundo de uma imagem — mesmo sem citar a skill.
metadata:
  version: 0.2.0
  type: knowledge
---
# ComfyUI — Realce e Controle de Imagem

Técnicas além do inpaint puro: ampliar, estender, reiluminar, controlar e limpar.

## Quando usar
"Aumentar/upscale", "melhorar resolução/restaurar", "estender a imagem/outpaint", "reiluminar/relight",
"controlar pose/estrutura (ControlNet)", "transferir estilo/IPAdapter", "manter o rosto (PuLID)", "tirar o fundo".

## Técnicas (um arquivo por técnica)

| Técnica | Arquivo | O que cobre |
|---------|---------|-------------|
| Upscaling | [upscaling.md](upscaling.md) | ESRGAN, Ultimate SD Upscale, SUPIR |
| Outpainting | [outpainting.md](outpainting.md) | Pad/Extend for Outpainting + Flux Fill |
| Relighting | [relighting.md](relighting.md) | IC-Light (fc/fbc), ImageCompositeMasked |
| Controle e estilo | [control-style.md](control-style.md) | ControlNet, IPAdapter, PuLID/InstantID, detailers |
| Remoção de fundo | [background-removal.md](background-removal.md) | RMBG, BiRefNet, SAM3 |

## Referências (nível 3)
- `docs/image-editing.md` §4 (fonte). Projetos: `workflows-cloud/outpaint-extend`, `workflows-cloud/remove-background`.
- Cadeia: editar a região → `knowledge-image-editing`; selecionar → `knowledge-image-masking`; provisionar modelos → `knowledge-runpod-provisioning`.

## Evolução
Append em `LEARNINGS.md` ao achar um upscaler/ControlNet/IPAdapter melhor por caso, ou um gotcha de relight. Diff git p/ revisão.
