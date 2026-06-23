# API Reference — replace-object

Campos por nó (capturados do `/object_info` do ComfyUI). A ordem dos `widgets_values` segue a ordem abaixo.

## `NanoBananaPro_fal` (fal · Nano Banana Pro / Gemini 3)
- **inputs (link):** `images` (IMAGE — batch de BASE + REFERÊNCIA via `ImageBatch`).
- **widgets (ordem):** `prompt` (STRING) · `num_images` (INT=1) · `aspect_ratio` (`auto`/`16:9`/…, use `auto`) · `output_format` (`png`) · `resolution` (`1K`/`2K`/`4K`) · `sync_mode` (false).
- **seed:** ❌ não tem. Reprodutível por **âncora** (1ª imagem do batch = BASE).
- **output:** IMAGE.

## `FluxProKontextMulti_fal` (fal · Flux 1.1 Pro Kontext Max, multi-ref)
- **inputs (link):** `image_1` (BASE) · `image_2` (REFERÊNCIA) · `image_3`/`image_4` (opcionais).
- **widgets (ordem):** `prompt` (STRING) · `aspect_ratio` (None=mantém input) · `max_quality` (BOOL, default false) · `guidance_scale` (FLOAT 3.5) · `num_images` (INT 1) · `safety_tolerance` (`1`..`6`, default `2`) · `output_format` (`jpeg`/`png`) · `sync_mode` (false) · `seed` (INT) · `control_after_generate` (`fixed`).
- **⚠️ seed gate:** `seed = 0` e control **`fixed`**. **`seed > 0` TRAVA o nó.**
- **output:** IMAGE.

## `ImageResizeKJ` (KJNodes)
- **inputs:** `image` · `get_image_size` (IMAGE opcional — quando ligado, usa o tamanho dessa imagem).
- **widgets (ordem):** `width` · `height` · `upscale_method` (`lanczos`) · `keep_proportion` (BOOL) · `divisible_by` (INT) · `crop` (`center`/`disabled`).
- Uso aqui: nos workflows, `get_image_size` recebe a **BASE** → BASE e REFERÊNCIA saem do mesmo tamanho (exigência do `ImageBatch`). O nó **"Conforma"** (03/04) usa `keep_proportion=false`, `divisible_by=1` p/ casar o tamanho EXATO da base antes do composite.

## `GrowMaskWithBlur` (KJNodes)
- **input:** `mask` (a máscara pintada no MaskEditor, saída MASK do `LoadImage`).
- **widgets (ordem):** `expand` (INT) · `incremental_expansion_rate` (FLOAT) · `tapered_corners` (BOOL) · `flip_input` (BOOL) · `blur_radius` (FLOAT) · `lerp_alpha` · `decay_factor` · `fill_holes` (BOOL).
- **outputs:** `mask` (slot 0) · **`mask_inverted` (slot 1)** ← é a saída usada pelo composite.

## `ImageCompositeMasked` (core)
- **inputs:** `destination` (= **edição completa** conformada) · `source` (= **BASE original**) · `mask` (= `mask_inverted`).
- **widgets:** `x` (0) · `y` (0) · `resize_source` (true).
- **Resultado:** cola o original fora da área pintada → só a região pintada recebe a edição; resto pixel-idêntico.
- **Bypass (mode 4, padrão nos 03/04):** devolve `destination` = edição completa → igual ao 01/02.

## Cadeia
`LoadImage(BASE)`+`LoadImage(REF)` → `ImageResizeKJ`×2 → `ImageBatch` → `NanoBananaPro_fal` *(ou `FluxProKontextMulti_fal` direto com image_1/image_2)* → *(opcional)* `ImageResizeKJ(Conforma)` + `GrowMaskWithBlur` → `ImageCompositeMasked` → `SaveImage`.
