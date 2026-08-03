# Controle e Estilo — ControlNet, IPAdapter, PuLID

Controlar estrutura, pose e estilo da geração.

## ControlNet
`comfyui_controlnet_aux` para pré-processadores:
- **canny** — bordas/estrutura.
- **depth** — profundidade da cena.
- **openpose** — pose/esqueleto.
- **lineart/scribble/tile** — esboço, rabisco, coerência de tiles.
- 2026: Union/Flux ControlNet é o padrão.

## IPAdapter — Transferência de Estilo
`ComfyUI_IPAdapter_plus`: transfere estilo/conceito de uma imagem-referência sem prompt engineering.

## PuLID / InstantID — Consistência Facial
**Flux PuLID**: mantém a identidade facial a partir de uma foto de referência.

## Regional Prompting
`ConditioningSetArea`/`ConditioningSetMask` — prompts diferentes para regiões diferentes.

## Detailers
**FaceDetailer** — detecta+refina rostos.
**Hand detailer** — usa LoRA de mãos para corrigir dedos.

## Referências
- `docs/image-editing.md` §4
- IPAdapter + IC-Light → [relighting](relighting.md)
