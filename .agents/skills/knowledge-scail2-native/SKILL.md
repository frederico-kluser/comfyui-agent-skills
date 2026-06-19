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
  version: 0.1.0
  type: knowledge
---
# SCAIL-2 — Grafo Nativo do ComfyUI

O caminho **nativo** (nós core do ComfyUI), distinto do wrapper kijai (`WanVideoModelLoader`/
`WanVideoAddSCAIL*Embeds`/`WanVideoSampler`). Mapeado de um workflow real de terceiros
(`workflows/scail2-native-3rdparty/`). `SCAIL2ColoredMask` e `WanSCAILToVideo` são **core** → exigem ComfyUI **nightly**.

## Quando usar
Montar/depurar/entender o workflow **nativo** do SCAIL-2; toggle Animation/Replacement; máscara por texto via SAM3.

## A cadeia (3 grupos: MODELS · INPUTS · SAMPLER+OUTPUT)
```
UNETLoader(wan2.1_14B_SCAIL_2_fp8) → LoraLoaderModelOnly(lightx2v rank64, str 1) → ModelSamplingSD3(shift 5) → KSampler
CLIPLoader(umt5_xxl, type "wan") → CLIPTextEncode +/− ─┐
VAELoader(wan_2.1_vae) ─────────────────────────────── │
CLIPVisionLoader(clip_vision_h) → CLIPVisionEncode(ref) │
VHS_LoadVideo(force_rate 16, cap 81) → (driving frames) │
LoadImage(ref) ─────────────────────────────────────── │
SAM3 subgraph → SCAIL2ColoredMask → (2 máscaras) ─────→ WanSCAILToVideo → (positive/negative/latent) → KSampler
                                                          → VAEDecode → RIFE VFI(×2) → VHS_VideoCombine
```

## Nós-chave (assinaturas reais)
- **`WanSCAILToVideo`** — o coração. Inputs: `positive,negative,vae`, `pose_video`+`pose_video_mask` (vídeo-condutor + máscara), `reference_image`+`reference_image_mask` (foto + máscara), `clip_vision_output`, `previous_frames` (extensão/ancoragem), `width,height,length`, **`replacement_mode` (BOOLEAN)**. Outputs: `positive,negative,latent,video_frame_offset`. É o equivalente nativo de toda a cadeia de embeds do wrapper.
- **`SCAIL2ColoredMask`** (core) — Inputs: `driving_track_data`+`ref_track_data` (SAM3_TRACK_DATA), `replacement_mode`. Outputs: `pose_video_mask`, `reference_image_mask`. Modo `area`.
- **Subgraph `SAM3`** — `SAM3_VideoTrack` ×2 + `CLIPTextEncode` ×2 (prompt do **conceito** a segmentar, ex.: `"human"`): rastreia o alvo por TEXTO no vídeo-condutor (→ `track_data`) e na foto (→ `track_data_1`). Modelo `sam3.1_multiplex_fp16` via `CheckpointLoaderSimple` (em `models/checkpoints/`).
- **`ModelSamplingSD3`** — `shift = 5` no caminho nativo (≠ o `--sample_shift 1` do CLI; é outro espaço de parâmetro). Aplica o shift ao MODEL antes do KSampler.
- **`KSampler`** — seed, `steps 6`, `cfg 1`, `euler`, `simple`, `denoise 1`. Config canônica do SCAIL-2 destilado.
- **`ResizeImageMaskNode`** — `scale total pixels 0.5` (meia-resolução do pose/mask) + `scale to multiple 32` (por isso dims **÷32**).
- **`RIFE VFI`** — `rife49.pth`, multiplier **2** (16→32 fps), fast_mode + ensemble. **`VHS_VideoCombine`** — h264-mp4, crf 19, 32 fps, save_metadata.
- **Controles** (Primitives nomeados): `DURAÇÃO (FRAMES)` = 81; `REPLACE` (BOOLEAN) → liga em `replacement_mode`. **False = Animation, True = Replacement.**

## Por que importa / gotchas
- **replacement_mode** é UM booleano que percorre `SCAIL2ColoredMask` **e** `WanSCAILToVideo` — alterne os dois juntos (este workflow usa um Primitive único ligado nos dois).
- Máscara é gerada por **texto** (SAM3), não pintada: troque o prompt do subgraph ("human" → "the man on the left", "dog"...) para mudar o alvo. Encontra/rastreia todas as instâncias do conceito.
- SCAIL-2 roda a **16 fps** (`force_rate 16`) → interpole com RIFE ×2 para 32, não suba o force_rate.
- `SCAIL2ColoredMask`/`WanSCAILToVideo` vermelhos = ComfyUI não está nightly.
- Comparação: este nativo vs `workflows/person-swap-scail2` (wrapper kijai, pose-control). O nativo tem o toggle replacement_mode explícito e máscara SAM3 por texto integrada — mais direto para "trocar pessoa".

## Referências (nível 3)
- `workflows/scail2-native-3rdparty/` (o workflow de terceiros analisado + README). `docs/SCAIL-2.md`.
- Cadeia: modelo/VRAM/quant → `knowledge-scail2`; grafo/nós em geral → `knowledge-comfyui-workflows`; máscara por texto → `knowledge-image-masking`.

## Evolução
Append em `LEARNINGS.md` ao confirmar (no pod) o significado dos slots numéricos de `WanSCAILToVideo`, o valor
ideal de shift, ou diferenças wrapper×nativo. Destile se estável (`version++`). Diff git p/ revisão.
