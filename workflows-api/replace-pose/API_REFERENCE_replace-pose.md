# API Reference — replace-pose

Campos por nó (capturados do `/object_info` do ComfyUI). A ordem dos `widgets_values` segue a ordem abaixo.

## `NanoBananaPro_fal` (fal · Nano Banana Pro / Gemini 3)
- **inputs (link):** `images` (IMAGE — referência: batch BASE+REF via `ImageBatch`; texto: só a BASE).
- **widgets (ordem):** `prompt` (STRING) · `num_images` (INT=1) · `aspect_ratio` (`auto`) · `output_format` (`png`) · `resolution` (`1K`/`2K`/`4K`) · `sync_mode` (false).
- **seed:** ❌ não tem. Reprodutível por **âncora** (1ª imagem do batch = BASE = a pessoa).
- **output:** IMAGE.

## `FluxProKontextMulti_fal` (fal · Flux 1.1 Pro Kontext Max, multi-ref)
- **inputs (link):** `image_1` (BASE) · `image_2` (REFERÊNCIA de pose; **no modo texto = cópia da BASE**) · `image_3`/`image_4` (opcionais).
- **widgets (ordem):** `prompt` (STRING) · `aspect_ratio` (None=mantém input) · `max_quality` (BOOL, default false) · `guidance_scale` (FLOAT 3.5) · `num_images` (INT 1) · `safety_tolerance` (`1`..`6`, default `2`) · `output_format` (`jpeg`/`png`) · `sync_mode` (false) · `seed` (INT) · `control_after_generate` (`fixed`).
- **⚠️ seed gate:** `seed = 0` e control **`fixed`**. **`seed > 0` TRAVA o nó.**
- **`image_1` e `image_2` são obrigatórios** → o workflow de texto (`04`) liga a BASE nos dois.
- **output:** IMAGE.

## `ImageResizeKJ` (KJNodes) — só nos workflows de referência (01) e Nano
- **inputs:** `image` · `get_image_size` (IMAGE — recebe a **BASE** → BASE e REF saem do mesmo tamanho, exigência do `ImageBatch`).
- **widgets (ordem):** `width` · `height` · `upscale_method` (`lanczos`) · `keep_proportion` (BOOL true) · `divisible_by` (INT 2) · `crop` (`center`).

## `ImageBatch` (core) — só nos workflows de referência (01) e Nano
- **inputs:** `image1` (BASE redimensionada) · `image2` (REF redimensionada). **output:** IMAGE (batch) → `NanoBananaPro_fal.images`.

## Cadeias
- **Referência (Nano):** `LoadImage(BASE)`+`LoadImage(REF)` → `ImageResizeKJ`×2 → `ImageBatch` → `NanoBananaPro_fal` → `SaveImage`.
- **Referência (Kontext):** `LoadImage(BASE)`→`image_1`, `LoadImage(REF)`→`image_2` → `FluxProKontextMulti_fal` → `SaveImage`.
- **Texto (Nano):** `LoadImage(BASE)` → `ImageResizeKJ` → `NanoBananaPro_fal` → `SaveImage`.
- **Texto (Kontext):** `LoadImage(BASE)` → `image_1` **e** `image_2` → `FluxProKontextMulti_fal` → `SaveImage`.

## Prompts (no nó do modelo)
- **Referência:** "*Repose the person from the first image so their body posture, limb positions and orientation exactly match the pose of the person shown in the second image. Keep the identity, face, hairstyle, skin tone, clothing, colors, lighting and background of the first image unchanged — change ONLY the body pose. Do not copy the face, clothing or background of the second image; use it only as a pose guide.*"
- **Texto:** "*Change the body pose of the person in this image to: `<DESCREVA A POSE>`. Keep the identity, face, hairstyle, clothing, colors, lighting and background exactly the same. Change ONLY the pose and limb positions.*"
