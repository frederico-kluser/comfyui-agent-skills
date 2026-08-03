---
name: knowledge-scail2-native
description: >-
  Conhecimento do grafo NATIVO do SCAIL-2 no ComfyUI (nós core, não o wrapper kijai): UNETLoader →
  LoraLoaderModelOnly (lightx2v) → ModelSamplingSD3 (shift ~5) → WanSCAILToVideo → KSampler
  (euler/simple/6/cfg 1) → VAEDecode → RIFE → VHS_VideoCombine; máscaras coloridas via SCAIL2ColoredMask
  alimentado por SAM3_VideoTrack (segmentação por texto, ex.: "human"); toggle replacement_mode
  (Animation↔Replacement). Use ao montar, debugar ou entender o workflow nativo do SCAIL-2 — mesmo sem
  citar a skill. Para modelo/VRAM/quantização do SCAIL-2 → knowledge-scail2.
metadata:
  version: 0.2.0
  type: knowledge
---
# SCAIL-2 — Grafo Nativo do ComfyUI

O caminho **nativo** (nós core do ComfyUI), distinto do wrapper kijai (`WanVideoModelLoader`/
`WanVideoAddSCAIL*Embeds`/`WanVideoSampler`). Mapeado de um workflow real de terceiros
(`workflows-cloud/scail2-native-3rdparty/`). `SCAIL2ColoredMask` e `WanSCAILToVideo` são **core** → exigem ComfyUI **nightly**.

## Quando usar
Montar/depurar/entender o workflow **nativo** do SCAIL-2; toggle Animation/Replacement; máscara por texto via SAM3.

## Técnicas (um arquivo por técnica)

| Técnica | Arquivo | O que cobre |
|---------|---------|-------------|
| A cadeia | [chain.md](chain.md) | Grafo completo, 3 grupos (MODELS·INPUTS·SAMPLER+OUTPUT) |
| Nós-chave | [key-nodes.md](key-nodes.md) | WanSCAILToVideo, SCAIL2ColoredMask, SAM3, KSampler, RIFE |
| Gotchas | [gotchas.md](gotchas.md) | replacement_mode único, 16fps, nativo vs wrapper |

## Referências (nível 3)
- `workflows-cloud/scail2-native-3rdparty/` (o workflow de terceiros analisado + README). `docs/SCAIL-2.md`.
- Cadeia: modelo/VRAM/quant → `knowledge-scail2`; grafo/nós em geral → `knowledge-comfyui-workflows`; máscara por texto → `knowledge-image-masking`.

## Evolução
Append em `LEARNINGS.md` ao confirmar (no pod) o significado dos slots numéricos de `WanSCAILToVideo`, o valor
ideal de shift, ou diferenças wrapper×nativo. Destile se estável (`version++`). Diff git p/ revisão.
