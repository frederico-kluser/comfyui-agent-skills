# API Reference — video-person-replace

> Schemas extraídos do `/object_info` do ComfyUI **ao vivo** (`:8188`) em 2026-08-03.
> Contém **custom nodes** (`ComfyUI-fal-API`, `ComfyUI-VideoHelperSuite`) — não é um bundle só-core.

---

## `Wan2214b_animate_replace_character_fal` — Wan 2.2 Animate 14B (replace)

- **Categoria:** `FAL/VideoGeneration` · **Módulo:** `custom_nodes.ComfyUI-fal-API`
- **Endpoint:** `fal-ai/wan/v2.2-14b/animate/replace`
- **Billing:** **fal.ai**, por segundo de vídeo. Lê a env var **`FAL_KEY`**
- **Saídas:** `video_url` (STRING) · `frames_zip_url` (STRING)

### Inputs

| Nome | Tipo | Obrig. | Default | Nota |
|---|---|---|---|---|
| `image` | IMAGE | ✅ | — | A pessoa que vai **entrar**. Corpo inteiro |
| `video` | VIDEO | — | — | O vídeo a editar (ou use `input_video_url`) |
| `input_video_url` | STRING | — | `""` | Alternativa ao slot `video` |
| `turbo` | BOOLEAN | — | `True` | Rota rápida/barata |
| `resolution` | COMBO | — | **`480p`** | `480p` · `580p` · `720p` — **480p é o piso deste endpoint** |
| `seed` | INT | — | `24` | 0 … 2147483647. **Sem** `control_after_generate` |
| `num_inference_steps` | INT | — | `20` | 1 … 40 |
| `guidance_scale` | FLOAT | — | `1.0` | 1.0 … 10.0. ⚠️ **modelo destilado: `>1` borra o vídeo** |
| `shift` | INT | — | `8` | 1 … 10 |
| `video_quality` | COMBO | — | `high` | `low` · `medium` · `high` · `maximum` (encode, não geração) |
| `video_write_mode` | COMBO | — | `balanced` | `balanced` · `fast` · `small` |
| `enable_safety_checker` | BOOLEAN | — | `True` | |
| `enable_output_safety_checker` | BOOLEAN | — | `False` | |
| `return_frames_zip` | BOOLEAN | — | `False` | Liga a saída `frames_zip_url` |
| `variations` | INT | — | `1` | 1 … 10 — **multiplica o custo** |

> **Não existe campo de prompt e não existe máscara.** O movimento e a expressão saem
> do próprio vídeo. É o que torna este nó a ferramenta certa para *"me colocar num vídeo que eu forneço"*.

### Ordem exata dos `widgets_values`

```
[0] input_video_url   [5] guidance_scale        [10] enable_safety_checker
[1] turbo             [6] shift                 [11] enable_output_safety_checker
[2] resolution        [7] video_quality         [12] return_frames_zip
[3] seed              [8] video_write_mode      [13] variations
[4] num_inference_steps
```

> `image` e `video` são **links**, não widgets — não entram no `widgets_values`.
> `seed` aqui **não** tem `control_after_generate` (diferente dos nós partner).

---

## `PixverseSwapNode_fal` — Pixverse Swap

- **Categoria:** `FAL/VideoGeneration` · **Saída:** `video_url` (STRING) · Chave: `FAL_KEY`

| Nome | Tipo | Obrig. | Default | Nota |
|---|---|---|---|---|
| `image` | IMAGE | ✅ | — | A pessoa que entra |
| `mode` | COMBO | ✅ | `person` | `person` · `object` · `background` |
| `keyframe_id` | INT | ✅ | `1` | Qual sujeito trocar quando há mais de um |
| `quality` | COMBO | ✅ | `720p` | `360p` · `540p` · `720p` — **360p é o piso** |
| `original_sound_switch` | BOOLEAN | ✅ | `True` | Mantém o áudio original **automaticamente** |
| `video` / `input_video_url` | VIDEO / STRING | — | — | O vídeo original |

**Ordem dos `widgets_values`:** `[mode, keyframe_id, quality, original_sound_switch, input_video_url]`

---

## `LoadVideoURL` — traz o resultado de volta

- **Categoria:** `video` · **Módulo:** `custom_nodes.ComfyUI-fal-API`
- **Saídas:** `frames` (IMAGE) · `frame_count` (INT) · `video_info` (VHS_VIDEOINFO)

**Ordem dos `widgets_values`:**
`[url, force_rate, force_size, custom_width, custom_height, frame_load_cap, skip_first_frames, select_every_nth]`

> No grafo o `url` está **convertido em input** (recebe o `video_url` por link).
> Serialização: `{"name":"url","type":"STRING","widget":{"name":"url"},"link":N}`.

## `VHS_VideoInfoLoaded` — fps real

- **Módulo:** `custom_nodes.ComfyUI-VideoHelperSuite` · **Input:** `video_info`
- **Saídas:** `fps` (FLOAT) · `frame_count` · `duration` · `width` · `height`

## `GetVideoComponents` — áudio do vídeo original

- **Módulo:** `comfy_extras.nodes_video` (**core**) · **Input:** `video` (VIDEO)
- **Saídas:** `images` (IMAGE) · `audio` (AUDIO) · `fps` (FLOAT) · `bit_depth` (INT)

## `CreateVideo` / `SaveVideo` — remontagem

- `CreateVideo` — inputs `images` (IMAGE), `audio` (AUDIO, opcional), widgets `[fps, bit_depth]`
- `SaveVideo` — input `video`, widgets `[filename_prefix, format, codec]`

> No grafo o `fps` do `CreateVideo` está **convertido em input**, alimentado pelo
> `VHS_VideoInfoLoaded`. **Regra de ordenação de slots** (confirmada nos templates
> oficiais): entradas de link normais **primeiro**, widgets convertidos em input
> **depois** — aqui `images`(0), `audio`(1), `fps`(2).

---

## Nós da cadeia de realismo (locais, CPU, custo zero)

| Nó | Módulo | `widgets_values` |
|---|---|---|
| `ColorMatchV2` | `ComfyUI-KJNodes` | `[method, strength, multithread]` |
| `ImageScaleToMaxDimension` | `comfy_extras.nodes_images` (**core**) | `[upscale_method, largest_size]` |
| `Image Filter Adjustments` | `was-node-suite-comfyui` | `[brightness, contrast, saturation, sharpness, blur, gaussian_blur, edge_enhance, detail_enhance]` |
| `Image Chromatic Aberration` | `was-node-suite-comfyui` | `[red_offset, green_offset, blue_offset, intensity, fade_radius]` |
| `ImageSharpen` | core | `[sharpen_radius, sigma, alpha]` |
| `Image Film Grain` | `was-node-suite-comfyui` | `[density, intensity, highlights, supersample_factor]` |
| `ImageAddNoise` | core | `[seed, control_after_generate, strength]` |
| `Image Save` | `was-node-suite-comfyui` | 15 widgets — `extension` e `quality` fazem o JPEG real |

> ⚠️ **`Image Film Grain` supersampleia `supersample_factor`× internamente.** Com `4`
> e uma imagem grande isso estoura a RAM: uma de **5248×12800 derrubou o ComfyUI**
> durante a calibração deste bundle. Por isso o `ImageScaleToMaxDimension` vem
> **antes** dele, limitando o lado maior. Em vídeo o fator está em **1** (roda quadro a quadro).
