# Segmentação Semântica por Texto

Selecionar região descrevendo o objeto em texto. "Máscara do céu", "a camisa azul", "o cachorro".

## SAM3 (PCS) — 🏆 recomendado
Uma frase ("striped cat") segmenta **todas as instâncias** de uma vez.
- ComfyUI via **ComfyUI-RMBG v3.0.0** (1038lab) / Ultralytics 8.3.237+.
- `sam3.pt` requer aprovação de licença no HF. (~3.4GB, server-scale).

## SAM2 (clique/ponto/caixa, imagem+vídeo)
`kijai/ComfyUI-segment-anything-2`, modelos em `models/sam2`.
Nós `Sam2Segmentation`, `Sam2AutoSegmentation`.

## Grounding DINO + SAM
`storyicon/comfyui_segment_anything`: string → máscara.
Nó `GroundingDinoSAMSegment`.

## Florence-2
`kijai/ComfyUI-Florence2`: `Florence2Run` task `referring_expression_segmentation` ou `caption_to_phrase_grounding`.
⚠️ `referring` pega 1 segmento por vez para múltiplos objetos.

## ComfyUI-Grounding (PozzettiAndrea)
19+ modelos de grounding + Florence-2 + SA2VA.

## Referências
- `docs/image-editing.md` §2
- Editar a região → `knowledge-image-editing`
