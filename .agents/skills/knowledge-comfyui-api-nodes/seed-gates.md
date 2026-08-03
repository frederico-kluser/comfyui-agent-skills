# API Online — Seed Gates

⚠️ Errar o valor TRAVA o nó — a regra mais cara de errar. Cada nó trata "seed aleatória" diferente;
o gate está no código do nó.

## Tabela de seed gates

| Nó | Valor p/ aleatório | Gate / nota |
|---|---|---|
| `FluxPro1Fill_fal` | **`0`** | `!= 0` → **`-1` TRAVA**. `mask_image` é **IMAGE** (use `MaskToImage`) |
| `FluxProKontext_fal` / `FluxProKontextMulti_fal` (`max_quality`) | **`0`** | gate `> 0` |
| `FluxUltra_fal` (Flux 1.1 Pro Ultra) / `Upscaler_fal` (Clarity) | **`-1`** | gate `!= -1` |
| `SeedanceImageToVideo_fal` / `SeedanceProImageToVideo_fal` | `-1` (tem seed) | reprodutível para vídeo |
| `Veo31_fal` · `NanoBananaPro_fal` · `NanoBananaEdit_fal` | **sem seed** | trava por **âncora**; para repro use `Veo3FirstLastFrameNode` / `SeedanceProImageToVideo_fal` / `GrokVideoExtendNode` |
| Pixverse `*_fal` | — | **1-indexed** (`keyframe_id=1`; 0 é rejeitado) |
| `Wan2214b_animate_{move,replace}_character_fal` | `seed` INT (def **24**) + `shift` INT (def **8**) — campos próprios | (live `/object_info`) sem slot `"fixed"`; saída é **URL** (`video_url`+`frames_zip_url`) → padrão A; `variations`=nº de saídas |

## Referências
- Catálogo de nós → [catalog-video](catalog-video.md) · [catalog-image-edit](catalog-image-edit.md)
