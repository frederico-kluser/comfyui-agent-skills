# SCAIL-2 Nativo — Nós-Chave

Assinaturas reais dos nós do caminho nativo.

## `WanSCAILToVideo` — o coração
Inputs: `positive, negative, vae`, `pose_video`+`pose_video_mask` (vídeo-condutor + máscara),
`reference_image`+`reference_image_mask` (foto + máscara), `clip_vision_output`,
`previous_frames` (extensão/ancoragem), `width, height, length`,
**`replacement_mode` (BOOLEAN)**.
Outputs: `positive, negative, latent, video_frame_offset`.
É o equivalente nativo de toda a cadeia de embeds do wrapper.

## `SCAIL2ColoredMask` (core)
Inputs: `driving_track_data`+`ref_track_data` (SAM3_TRACK_DATA), `replacement_mode`.
Outputs: `pose_video_mask`, `reference_image_mask`. Modo `area`.

## Subgraph `SAM3`
`SAM3_VideoTrack` ×2 + `CLIPTextEncode` ×2 (prompt do **conceito** a segmentar, ex.: `"human"`):
rastreia o alvo por TEXTO no vídeo-condutor (→ `track_data`) e na foto (→ `track_data_1`).
Modelo `sam3.1_multiplex_fp16` via `CheckpointLoaderSimple` (em `models/checkpoints/`).

## `ModelSamplingSD3`
`shift = 5` no caminho nativo (≠ o `--sample_shift 1` do CLI; é outro espaço de parâmetro).
Aplica o shift ao MODEL antes do KSampler.

## `KSampler`
seed, `steps 6`, `cfg 1`, `euler`, `simple`, `denoise 1`. Config canônica do SCAIL-2 destilado.

## `ResizeImageMaskNode`
`scale total pixels 0.5` (meia-resolução do pose/mask) + `scale to multiple 32` (por isso dims **÷32**).

## `RIFE VFI`
`rife49.pth`, multiplier **2** (16→32 fps), fast_mode + ensemble.

## `VHS_VideoCombine`
h264-mp4, crf 19, 32 fps, save_metadata.

## Referências
- `workflows-cloud/scail2-native-3rdparty/`
- Cadeia completa → [chain](chain.md)
