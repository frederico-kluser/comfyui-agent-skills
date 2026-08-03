# Cadeia WanVideoWrapper (Kijai) — Vídeo

A cadeia padrão para geração de vídeo com Wan no ComfyUI.

## Grafo
```
WanVideoModelLoader ─model─► WanVideoSampler ─samples─► WanVideoDecode ─► VHS_VideoCombine
LoadWanVideoT5TextEncoder ─► WanVideoTextEncode ─text_embeds─► (Sampler)
WanVideoEmptyEmbeds (T2V)  ─image_embeds─► (Sampler)
WanVideoVAELoader ─vae─► (Decode)
```

## I2V (imagem→vídeo)
Troque `WanVideoEmptyEmbeds` por `WanVideoImageToVideoEncode` (start_image via VAE + CLIP-vision `clip_vision_h`).
- `num_frames` default **81**, passo 4 (`((n-1)//4)*4+1`).
- `noise_aug_strength` — adiciona movimento/nitidez.
- `start_latent_strength` menor = mais movimento.
- `tiled_vae` economiza memória.

## Sampler
Entradas: `model, image_embeds, text_embeds, shift, steps, cfg, seed, scheduler`.
Opcionais: `context_options`, `cache_args/teacache_args`, `denoise_strength`, `samples` (v2v).

## Otimizações
- `WanVideoTextEncodeCached` descarrega o T5 (sem pegada de VRAM/RAM).
- Prompt travel: prompts separados por `|`.

## Referências
- `docs/workflow-guide.md`
- Vídeo longo → [context-windows](context-windows.md)
