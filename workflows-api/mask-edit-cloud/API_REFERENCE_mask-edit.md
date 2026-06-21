# mask-edit-cloud — API Reference (nós e parâmetros)

Técnica **select → edit-region → paste-back**. Workflows em formato UI. A máscara roda **local**; o inpaint pode ser
**nuvem** (`FluxPro1Fill_fal`) ou **local** (SDXL). Ver `knowledge-image-masking` / `knowledge-image-editing`.

## 🎯 Seleção da região (local, precisão cheia)

### `GroundingDinoSAMSegment (segment anything)` — texto → máscara
| Campo | Tipo | Exemplo | Nota |
|---|---|---|---|
| `image` | IMAGE | — | |
| `prompt` | STRING | `"the shirt"` | substantivo simples em inglês |
| `threshold` | FLOAT | `0.3` | 0.25–0.4; caia p/ 0.2 se não achar |
| saída 1 | IMAGE | região recortada | |
| **saída 2** | **MASK** | a máscara | é o que segue no fluxo |
> Loaders: `SAMModelLoader` (`sam_vit_h`) + `GroundingDinoModelLoader` (SwinB). Manual: `Load Image` → **Open in MaskEditor**.

### `GrowMaskWithBlur` (KJNodes) — refinar a máscara
| Campo | Valor | Nota |
|---|---|---|
| `expand` | `10` | pega a borda |
| `blur_radius` | `8` | suaviza (costura) |
| `fill_holes` | true | |

## ☁️ Rota nuvem — `03_inpaint_nuvem_fal_composite`

### `FluxPro1Fill_fal` — Flux.1 Fill Pro (fal)  ·  **seed=0=aleatório**
| Campo | Tipo | Exemplo | ⚠️ |
|---|---|---|---|
| `image` | IMAGE | a original | |
| `mask_image` | **IMAGE** | ← `MaskToImage(MASK)` | quer IMAGE, **não** MASK → insira `MaskToImage` |
| `seed` | INT | **`0`** | `-1` **TRAVA** (gate `!= 0`) |
| `num_images` | INT | `1` | |
| `safety` | STRING | `"2"` | |
| `output_format` | enum | `png` | |
> Saída → `ImageCompositeMasked` (original = `destination`, gerado = `source`, mesma máscara) → opcional `ColorMatch` → `SaveImage`.

## 💻 Rota local grátis — `02_inpaint_local_sdxl_composite`
Cadeia: `CheckpointLoaderSimple (sd_xl_base_1.0)` → **`DifferentialDiffusion`** (no MODEL) → `VAEEncode` + **`SetLatentNoiseMask`**(mask) → `KSampler` → `VAEDecode` → `ImageCompositeMasked`.
| Nó | Campo | Valor |
|---|---|---|
| `KSampler` | `steps`/`cfg` | `25` / `6` |
| `KSampler` | `sampler`/`scheduler` | `dpmpp_2m` / `karras` |
| `KSampler` | `denoise` | `0.75` (0.5–0.6 leve · 0.8–0.9 forte) |
> `sd_xl_base` **não é** modelo de inpaint → use `VAEEncode`+`SetLatentNoiseMask` (+`DifferentialDiffusion`), **nunca** `InpaintModelConditioning` (esse é só p/ modelos dedicados, ex.: Flux Fill).

## 🔍 Alta resolução — `04_crop_stitch_alta_res` (KJNodes)
`ImageCropByMaskAndResize(base_resolution=1024, padding=32)` → inpaint do tile → `ImageUncropByMask(... bbox)`.
> Maior ganho de detalhe em 8 GB: só o recorte passa pelo VAE; o resto da imagem nunca é re-decodificado.

## 🎨 `ImageCompositeMasked` (core) — a recolagem
`mask*source + (1-mask)*destination`. **Sempre** finalize com ele sobre a original (o VAE altera levemente pixels fora da máscara). Equivalente em código: `replace_via_codigo.py` (PIL `paste` com máscara borrada, blur 4px).

## 🗺️ Mapa por arquivo
| Arquivo | Nó(s) principal(is) | Billing |
|---|---|---|
| `01_selecionar_regiao_texto` | `GroundingDinoSAMSegment` + loaders + `GrowMaskWithBlur` | local |
| `02_inpaint_local_sdxl_composite` | `CheckpointLoaderSimple` + `KSampler` + `ImageCompositeMasked` | local grátis |
| `03_inpaint_nuvem_fal_composite` | `FluxPro1Fill_fal` + `MaskToImage` + `ImageCompositeMasked` | fal |
| `04_crop_stitch_alta_res` | `ImageCropByMaskAndResize` + `ImageUncropByMask` | local |
| `replace_via_codigo.py` | PIL paste (fora do ComfyUI) | — |
