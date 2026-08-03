# Detecção Automática — Impact Pack

Detecção de rostos, mãos, pessoas e objetos sem descrever em texto.
`ComfyUI-Impact-Pack` (ltdrdata).

## Detectores
- **UltralyticsDetectorProvider** (YOLO): `bbox/face_yolov8m.pt`, `bbox/hand_yolov8s.pt`, `segm/person_yolov8m-seg.pt`.
- **BBOX/SEGM/SAMDetector**: detecções → **SEGS** (máscara+bbox+confiança+label).
- **SAMDetector (combined)** = silhueta precisa (SAM refina a detecção YOLO).

## FaceDetailer
Detecta+refina rostos (crop → KSampler interno → cola de volta).
Use 2-pass para rostos muito danificados.

## Referências
- `docs/image-editing.md` §2
- Para selecionar por texto → [segmentação semântica](text-segmentation.md)
- Para operações sobre máscaras → [operações de máscara](mask-operations.md)
