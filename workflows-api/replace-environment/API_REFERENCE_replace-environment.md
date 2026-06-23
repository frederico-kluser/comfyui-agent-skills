# API Reference — replace-environment

Campos por nó (capturados do `/object_info` do ComfyUI). Mesma cadeia do `replace-object`, mas
BASE = **o sujeito** e REFERÊNCIA = **o ambiente novo**; no composite você pinta o **FUNDO**.

## `NanoBananaPro_fal` (fal · Nano Banana Pro / Gemini 3)
- **inputs (link):** `images` (IMAGE — batch de BASE/sujeito + REFERÊNCIA/ambiente via `ImageBatch`).
- **widgets (ordem):** `prompt` · `num_images` (1) · `aspect_ratio` (`auto`) · `output_format` (`png`) · `resolution` (`1K`/`2K`/`4K`) · `sync_mode` (false).
- **seed:** ❌ não tem (âncora = 1ª imagem = o sujeito).
- **output:** IMAGE.

## `FluxProKontextMulti_fal` (fal · Flux 1.1 Pro Kontext Max, multi-ref)
- **inputs (link):** `image_1` (sujeito) · `image_2` (ambiente) · `image_3`/`image_4` (opcionais).
- **widgets (ordem):** `prompt` · `aspect_ratio` (None) · `max_quality` (false) · `guidance_scale` (3.5) · `num_images` (1) · `safety_tolerance` (`2`) · `output_format` (`png`) · `sync_mode` (false) · `seed` (INT) · `control_after_generate` (`fixed`).
- **⚠️ seed gate:** `seed = 0` e control **`fixed`**. **`seed > 0` TRAVA o nó.**
- **output:** IMAGE.

## `ImageResizeKJ` (KJNodes)
- **inputs:** `image` · `get_image_size` (recebe a BASE/sujeito → BASE e REFERÊNCIA do mesmo tamanho p/ `ImageBatch`).
- **widgets (ordem):** `width` · `height` · `upscale_method` · `keep_proportion` · `divisible_by` · `crop`.
- "Conforma" (03/04): `keep_proportion=false`, `divisible_by=1` → casa o tamanho EXATO da base antes do composite.

## `GrowMaskWithBlur` (KJNodes)
- **input:** `mask` (pinte o **FUNDO** no MaskEditor — saída MASK do `LoadImage`).
- **widgets (ordem):** `expand` · `incremental_expansion_rate` · `tapered_corners` · `flip_input` · `blur_radius` · `lerp_alpha` · `decay_factor` · `fill_holes`.
- **outputs:** `mask` (0) · **`mask_inverted` (1)** ← usada pelo composite.

## `ImageCompositeMasked` (core)
- **inputs:** `destination` (= edição completa conformada) · `source` (= BASE/sujeito original) · `mask` (= `mask_inverted`).
- **widgets:** `x` (0) · `y` (0) · `resize_source` (true).
- **Resultado:** o sujeito (fora do fundo pintado) fica pixel-idêntico; só o fundo recebe o novo ambiente.
- **Bypass (mode 4, padrão nos 03/04):** devolve a edição completa → igual ao 01/02.

## Cadeia
`LoadImage(sujeito)`+`LoadImage(ambiente)` → `ImageResizeKJ`×2 → `ImageBatch` → `NanoBananaPro_fal` *(ou `FluxProKontextMulti_fal` com image_1/image_2)* → *(opcional)* `ImageResizeKJ(Conforma)` + `GrowMaskWithBlur` → `ImageCompositeMasked` → `SaveImage`.
