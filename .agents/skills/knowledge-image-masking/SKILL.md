---
name: knowledge-image-masking
description: >-
  Conhecimento de seleção/segmentação de região no ComfyUI: máscara manual (MaskEditor), seleção
  semântica por texto (SAM2/SAM3, Florence-2, Grounding DINO), detecção automática (Impact Pack:
  UltralyticsDetector/YOLO, SAMDetector, FaceDetailer) e operações de máscara (grow/blur/SEGS/binária).
  Use para selecionar ou mascarar "a camisa", "o céu", um objeto, rostos ou mãos antes de editar —
  mesmo sem citar a skill. Editar a região depois → knowledge-image-editing.
metadata:
  version: 0.1.0
  type: knowledge
---
# ComfyUI — Seleção e Masking de Região

Como obter a MÁSCARA da parte da imagem a editar. Evoluiu de "pintar à mão" para "descrever em texto".

## Quando usar
"Selecionar/mascarar <objeto>", "máscara do céu/da camisa/do rosto", segmentar por texto, detectar
rostos/mãos/pessoas, converter/crescer/borrar máscara. Editar depois → `knowledge-image-editing`.

## Manual — MaskEditor
Load Image → clique direito → **"Open in MaskEditor"** → pinte (roda ajusta o pincel) → **"Save to node"**.
Saídas `IMAGE` + `MASK`. Pinte um pouco além do objeto (margem p/ blend). Alpha apagado (GIMP/PS) também vira máscara.

## Semântico por texto
- **SAM3** (PCS): uma frase ("striped cat") segmenta **todas as instâncias** de uma vez. ComfyUI via **ComfyUI-RMBG v3.0.0** (1038lab) / Ultralytics 8.3.237+. `sam3.pt` requer aprovação de licença no HF. (~3.4GB, server-scale.)
- **SAM2** (clique/ponto/caixa, imagem+vídeo): `kijai/ComfyUI-segment-anything-2`, modelos em `models/sam2`. Nós `Sam2Segmentation`, `Sam2AutoSegmentation`.
- **Grounding DINO + SAM** (`storyicon/comfyui_segment_anything`): string → máscara. Nó `GroundingDinoSAMSegment`.
- **Florence-2** (`kijai/ComfyUI-Florence2`): `Florence2Run` task `referring_expression_segmentation` ou `caption_to_phrase_grounding`. ⚠️ referring pega 1 segmento por vez p/ múltiplos objetos.
- **ComfyUI-Grounding** (PozzettiAndrea): 19+ modelos de grounding + Florence-2 + SA2VA.

## Automático — Impact Pack (rostos/mãos/pessoas)
`ComfyUI-Impact-Pack` (ltdrdata):
- **UltralyticsDetectorProvider** (YOLO): `bbox/face_yolov8m.pt`, `bbox/hand_yolov8s.pt`, `segm/person_yolov8m-seg.pt`.
- **BBOX/SEGM/SAMDetector**: detecções → **SEGS** (máscara+bbox+confiança+label). `SAMDetector (combined)` = silhueta precisa.
- **FaceDetailer**: detecta+refina rostos (crop → KSampler interno → cola de volta); 2-pass p/ rostos muito danificados.

## Operações de máscara
`MASK to SEGS` / `SEGS to MASK`, `ToBinaryMask`, `Dilate Mask` (grow), `Gaussian Blur Mask` (feathering),
`SEGSPaste` (cola SEGS na original). Por cor: `ImageColorToMask`. Por texto sem SAM: CLIPSeg (`CLIPSegDetectorProvider`). Depth/luminância → threshold.

## Referências (nível 3)
- `docs/image-editing.md` §2 (fonte). Projeto: `workflows-cloud/remove-background` (RMBG/SAM3).
- Cadeia: editar a região → `knowledge-image-editing`; rostos/detail → também Impact Pack.

## Evolução
Append em `LEARNINGS.md` ao achar um detector/modelo melhor por tipo de alvo, ou um gotcha de máscara. Destile se
estável (`version++`). Diff git p/ revisão.
