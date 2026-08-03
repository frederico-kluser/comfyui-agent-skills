# API Online — Catálogo de Nós: Vídeo

## Geração de vídeo (I2V/T2V/Extend)

- **`Veo31_fal`** — Veo 3.1, máx. qualidade, **24 fps**, durações 4/6/8s, 720p/1080p, **sem campo negative** (negativos em prosa).
- 🏆 **Seedance 2.0 (partner, comfy credits)** — `ByteDance2ReferenceNode` (reference-to-video: imagens + **vídeos** + áudios + assets), `ByteDance2TextToVideoNode`, `ByteDance2FirstLastFrameNode`. Saída **`VIDEO` nativo** (padrão B). `model` = `Seedance 2.0` (até **1080p**) ou `Seedance 2.0 Fast` (teto 720p). `duration` **4–15 s**, `ratio` `adaptive`, `generate_audio`. Seed **não é determinística** (só força re-run). Refs: **9 imagens · 3 vídeos · 3 áudios**. → ver [Seedance 2.0 humano real](seedance-real-human.md).
- **`SeedanceImageToVideo_fal` / `SeedanceProImageToVideo_fal`** — Seedance 1.x; 480p = **rascunho barato**; Pro tem `end_image` + negative + seed.
- **Kling (partner)** — `KlingImage2VideoNode` / `KlingTextToVideoNode` / `KlingVideoExtendNode` / `KlingCameraControlI2VNode`+`KlingCameraControls` (v2.x; câmera = **só 1 eixo ≠ 0**, range −10..+10; `KlingVideoExtendNode` encadeia `video_id`).
- **Kling fal** — `Kling25TurboPro_fal`, `Kling26Pro_fal`, `KlingO3Pro_fal`…
- **Outros**: `MiniMax*`/`MinimaxHailuoVideoNode`, `LumaVideoNode`, `OpenAIVideoSora2`, `LtxvApi*`, `PixverseImageToVideoNode`, `GrokVideoNode`, `ByteDanceImageToVideoNode` (Seedance partner — `seedance-1-5-pro` tem 1080p+`generate_audio`).

## Vídeo→Vídeo (transformar vídeo existente)

Entra por core **`LoadVideo`** → input `video`.

### Restyle/edit
- 🏆 **`RunwayAleph2VideoToVideoNode`** — restyle in-context, vídeo 2–30s, partner.
- **`GrokVideoEditNode`** — clipe ≤8.7s/50MB, partner.
- **`KlingOmniVideoToVideoEdit_fal`** — edit + inserir elementos por referência.

### Motion-transfer (substituto-API do SCAIL-2)
- `Wan2214b_animate_{move,replace}_character_fal` — imagem do sujeito + vídeo-guia.
- `KlingV3ProMotionControl_fal`/`KlingV3StandardMotionControl_fal`.

### Extend
- **`GrokVideoExtendNode`** — arquivo 2–15s, partner.
- **`KlingVideoExtendNode`** — só `video_id`, **não** arquivo; encadeia.
- **`ViduExtendVideoNode`** — arquivo, partner.
- Método Veo-handoff (`GetImageRangeFromBatch(-1)`).

## Padrões de saída de vídeo
- **(A) Nós fal `*_fal`**: `video_url (STRING)` → `LoadVideoURL` → `CreateVideo` → `SaveVideo`. ⚠️ Essa cadeia extrai **só frames** → **perde o áudio nativo** (baixe a URL original).
- **(B) Nós partner**: **`VIDEO`** nativo → vai **direto no `SaveVideo`** (áudio preservado).
- Entrada de vídeo (V2V) = core **`LoadVideo`** (saída `VIDEO`); `LoadVideoURL`/`VHS_LoadVideo` dão frames IMAGE, não servem.

## Referências
- Seed gates → [seed-gates](seed-gates.md)
- Imagem/Edição → [catalog-image-edit](catalog-image-edit.md)
