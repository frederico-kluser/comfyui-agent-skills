---
name: knowledge-image-masking
description: >-
  Conhecimento de seleção/segmentação de região no ComfyUI: máscara manual (MaskEditor), seleção
  semântica por texto (SAM2/SAM3, Florence-2, Grounding DINO), detecção automática (Impact Pack:
  UltralyticsDetector/YOLO, SAMDetector, FaceDetailer) e operações de máscara (grow/blur/SEGS/binária).
  Use para selecionar ou mascarar "a camisa", "o céu", um objeto, rostos ou mãos antes de editar —
  mesmo sem citar a skill. Editar a região depois → knowledge-image-editing.
metadata:
  version: 0.2.0
  type: knowledge
---
# ComfyUI — Seleção e Masking de Região

Como obter a MÁSCARA da parte da imagem a editar. Evoluiu de "pintar à mão" para "descrever em texto".

## Quando usar
"Selecionar/mascarar <objeto>", "máscara do céu/da camisa/do rosto", segmentar por texto, detectar
rostos/mãos/pessoas, converter/crescer/borrar máscara. Editar depois → `knowledge-image-editing`.

## Técnicas (um arquivo por técnica)

| Técnica | Arquivo | O que cobre |
|---------|---------|-------------|
| Máscara manual | [mask-editor.md](mask-editor.md) | MaskEditor: pintar, salvar, margem para blend |
| Segmentação por texto | [text-segmentation.md](text-segmentation.md) | SAM2/3, Florence-2, Grounding DINO, ComfyUI-Grounding |
| Detecção automática | [auto-detection.md](auto-detection.md) | Impact Pack: YOLO, SAMDetector, FaceDetailer |
| Operações de máscara | [mask-operations.md](mask-operations.md) | grow, blur, SEGS, binária, por cor, CLIPSeg |

## Referências (nível 3)
- `docs/image-editing.md` §2 (fonte). Projeto: `workflows-cloud/remove-background` (RMBG/SAM3).
- Cadeia: editar a região → `knowledge-image-editing`; rostos/detail → também Impact Pack.

## Evolução
Append em `LEARNINGS.md` ao achar um detector/modelo melhor por tipo de alvo, ou um gotcha de máscara. Destile se
estável (`version++`). Diff git p/ revisão.
