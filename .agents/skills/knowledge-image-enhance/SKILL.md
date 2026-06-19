---
name: knowledge-image-enhance
description: >-
  Conhecimento de realce e controle de imagem no ComfyUI: upscaling (ESRGAN/4x-UltraSharp, Ultimate SD
  Upscale, SUPIR), outpainting (Pad/Extend for Outpainting + Flux Fill), relighting (IC-Light), ControlNet
  (canny/depth/openpose/tile), IPAdapter e PuLID/InstantID (estilo e consistência facial), detailers
  (FaceDetailer) e remoção de fundo (RMBG/BiRefNet/SAM3). Use ao ampliar, estender, reiluminar, controlar
  estrutura/pose, transferir estilo ou remover fundo de uma imagem — mesmo sem citar a skill.
metadata:
  version: 0.1.0
  type: knowledge
---
# ComfyUI — Realce e Controle de Imagem

Técnicas além do inpaint puro: ampliar, estender, reiluminar, controlar e limpar.

## Quando usar
"Aumentar/upscale", "melhorar resolução/restaurar", "estender a imagem/outpaint", "reiluminar/relight",
"controlar pose/estrutura (ControlNet)", "transferir estilo/IPAdapter", "manter o rosto (PuLID)", "tirar o fundo".

## Upscaling
- **Model upscale** (rápido): `Upscale Image (using Model)` com ESRGAN/RealESRGAN/**4x-UltraSharp**/4x-Foolhardy-Remacri.
- **Ultimate SD Upscale** (ssitu): tiles + re-difusão; `tile_size`, `seam_fix`, linear/chess; use **ControlNet Tile** p/ coerência.
- **SUPIR** (kijai/ComfyUI-SUPIR): restauração foto-realista SDXL; pesado (32GB+ RAM, fp8 ajuda). Comum: SUPIR→2K depois 4x Remacri→8K.

## Outpainting
`Pad Image for Outpainting` (adiciona borda + cria a máscara) → Flux Fill / modelo de inpaint. `Extend Image for
Outpainting` (CropAndStitch) traz rescale/blend/restitch. Veja `workflows/outpaint-extend`.

## Relighting — IC-Light
`kijai/ComfyUI-IC-Light` (ou huchenlei native): `iclight_sd15_fc` (foreground/por texto), `iclight_sd15_fbc` (por background).
`IC Light Apply Mask Grey` deixa a área mascarada cinza. Combine com `ImageCompositeMasked` + IPAdapter p/ fotografia de produto.

## Controle e estilo
- **ControlNet** (`comfyui_controlnet_aux` p/ pré-processadores): canny/depth/openpose/lineart/scribble/tile. 2026: Union/Flux ControlNet padrão.
- **IPAdapter** (`ComfyUI_IPAdapter_plus`): estilo/conceito de uma imagem-ref. **PuLID/InstantID** (Flux PuLID): consistência facial a partir de uma foto.
- **Regional prompting**: `ConditioningSetArea`/`ConditioningSetMask`. **Detailers**: FaceDetailer (rostos), hand detailer (LoRA de mãos).

## Remoção de fundo
**ComfyUI-RMBG** (1038lab): RMBG-2.0, INSPYRENET, BEN2, **BiRefNet**, e **SAM3** (v3.0.0). Veja `workflows/remove-background`.

## Referências (nível 3)
- `docs/image-editing.md` §4 (fonte). Projetos: `workflows/outpaint-extend`, `workflows/remove-background`.
- Cadeia: editar a região → `knowledge-image-editing`; selecionar → `knowledge-image-masking`; provisionar modelos → `knowledge-runpod-provisioning`.

## Evolução
Append em `LEARNINGS.md` ao achar um upscaler/ControlNet/IPAdapter melhor por caso, ou um gotcha de relight. Diff git p/ revisão.
