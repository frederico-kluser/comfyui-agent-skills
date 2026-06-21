# commercial-ondokai — API Reference (nós e parâmetros)

Cards dos nós editáveis do comercial por API. Todos os workflows estão em **formato UI** (arraste o `.json`).
Provedores: **fal** (`*_fal`, cobra `FAL_KEY`) + **Kling partner** (login comfy.org). Ver `knowledge-comfyui-api-nodes`.

## ⚠️ Seed gates (errar o valor TRAVA o nó — regra de ouro)

| Nó | Tem seed? | Valor p/ "aleatório" | Observação |
|---|---|---|---|
| `NanoBananaPro_fal` | **não** | — | Identidade trava por âncora + frase repetida |
| `Veo31_fal` | **não** | — | P/ reprodutibilidade use `Veo3FirstLastFrameNode` / `SeedanceProImageToVideo_fal` / `GrokVideoExtendNode` |
| `SeedanceImageToVideo_fal` | sim | `-1` (modo `randomize`) | Draft 480p |
| `SeedanceProImageToVideo_fal` | sim | (fixa p/ repetir) | Extend C; tem `negative_prompt` + `end_image` |
| `FluxPro1Fill_fal` (mask-edit) | sim | **`0`** | `-1` **TRAVA**! (gate `!= 0`) |
| `FluxProKontext_fal` (max_quality) | sim | **`0`** | gate `> 0` |
| `FluxUltra_fal` / `Upscaler_fal` | sim | **`-1`** | gate `!= -1` |

## 🎯 Geração de imagem (keyframes + âncora)

### `NanoBananaPro_fal` — Nano Banana Pro / Gemini 3 (fal)
| Campo | Tipo | Exemplo | Descrição |
|---|---|---|---|
| `prompt` | STRING | retrato de estúdio com `<<PROTAGONISTA — ...>>` | Prosa fotográfica; **a frase de identidade é idêntica em toda cena** |
| `images` | IMAGE (input) | a âncora | Âncora de identidade (e refs de pose/figurino); multi-imagem via `ImageResizeKJ`+`ImageBatch` |
| `num_images` | INT | `1` | |
| `aspect_ratio` | enum | `16:9` | `16:9` / `9:16` / `1:1` |
| `resolution` | enum | `4K` | `1K` < `2K` < `4K` |
| `output_format` | enum | `png` | |
> `10_ANCORA`: gera 1× e salva `ondokai_anchor` (filename_prefix). Cenas 3/7/9 usam só este nó (still).

## 🎬 Geração de vídeo (cena = keyframe → Veo)

### `Veo31_fal` — Veo 3.1 (fal)  ·  **24 fps**, sem campo negative, sem seed
| Campo | Tipo | Exemplo | Descrição |
|---|---|---|---|
| `first_frame` | IMAGE (input) | keyframe da cena | Frame inicial (obrigatório) |
| `last_frame` | IMAGE (input) | END do morph | Opcional; **first+last = transição/morph** (cena 14) |
| `duration` | enum | `8s` | `4s` / `6s` / `8s` |
| `aspect_ratio` | enum | `16:9` | |
| `resolution` | enum | `1080p` | `720p` (teste) / `1080p` (final) |
| `generate_audio` | BOOL | cenas `false`, moldes `true` | ⚠️ a cadeia de saída **perde o áudio nativo** (ver abaixo) |
> Negativos: como não há campo, escreva-os em prosa no `first_frame`/prompt da cena.

### Cadeia de saída de vídeo (todos os clipes)
`Veo31_fal.video_url (STRING)` → **`LoadVideoURL`** (widget `url` convertido em input) → **`CreateVideo`** (`fps=24`) → **`SaveVideo`** (`mp4`/`h264`).
> ⚠️ `LoadVideoURL→CreateVideo` extrai **apenas frames** → **perde o áudio do Veo**. Para manter áudio, baixe a `video_url` original.

## 🎥 Câmera precisa (cena nova) — `31_MODELO_cena_camera_kling`

### `KlingCameraControls`
| Campo | Valor | Descrição |
|---|---|---|
| `type` | `simple` | |
| 6 eixos numéricos | só **1 ≠ 0** (ex.: `zoom=5.0`) | range −10..+10; `zoom+`=mais perto, `pan`=girar horizontal, `tilt`=vertical, `horizontal/vertical_movement`=deslizar |

### `KlingCameraControlI2VNode` (partner)
| Campo | Exemplo | Descrição |
|---|---|---|
| `start_frame` (input) | keyframe | |
| `camera_control` (input) | ← `KlingCameraControls` | |
| `prompt` / `negative_prompt` | `"no morphing, distorted hands, flicker, face morphing, camera shake, changing wardrobe"` | |
| `cfg_scale` | `0.75` | 0–1 |
| `aspect_ratio` | `16:9` | |

## ➕ Extensão dirigida (ação nova por segmento)

### A — `40_ESTENDER_A_veo_handoff` : 2× `Veo31_fal` + `GetImageRangeFromBatch`
- `GetImageRangeFromBatch` widgets `[start_index=-1, length=1]` → pega o **último frame** do seg1.
- Esse frame vira o `first_frame` do seg2 `Veo31_fal`, com **prompt novo** ("SEG 2 — continuação dirigida…"). Ambos 8s/16:9/1080p.

### B — `41_ESTENDER_B_kling_nativo` : `KlingImage2VideoNode` + 2× `KlingVideoExtendNode`
| Nó | Campos-chave |
|---|---|
| `KlingImage2VideoNode` | `start_frame`; `model_name=kling-v2-1`; `mode=pro`; `cfg_scale=0.8`; `aspect_ratio=16:9`; `duration=5` |
| `KlingVideoExtendNode` (×2) | `video_id` (encadeado do clipe anterior); `prompt` (ação nova/segmento); `cfg_scale=0.5` |

### C — `42_ESTENDER_C_seedance_barato` : 2× `SeedanceProImageToVideo_fal` + `GetImageRangeFromBatch`
| Campo | Exemplo | Descrição |
|---|---|---|
| `image` / `end_image` (input) | keyframe / frame final desejado | Seedance Pro aceita `end_image` |
| `prompt` / `negative_prompt` | `"morphing, distorted hands, flicker, face morphing"` | tem campo negative |
| `duration` / `cfg_scale` | `5` / `0.5` | |
| `seed` | `1` | **tem** seed (reprodutível) |

## 🪙 Rascunho barato — `20_FERRAMENTA_rascunho_barato`
### `SeedanceImageToVideo_fal`
| Campo | Exemplo | Descrição |
|---|---|---|
| `image` / `prompt` (input) | keyframe / ação | |
| `resolution` | `480p` | barato p/ testar timing |
| `duration` | `5` | |
| `camera_fixed` | `false` | |
| `seed` | `-1` (`randomize`) | |

## 🎨 Consistência de cor — `ColorMatch`
| Campo | Valor | Descrição |
|---|---|---|
| `method` | `hm-mkl-hm` | |
| `strength` | `0.4` | 0.3–0.6 |
| referência | **um** hero frame canônico | NÃO o clipe anterior (evita deriva acumulada) |

## 🗺️ Mapa por arquivo (nó de geração principal)
| Arquivo | Nó(s) | Notas |
|---|---|---|
| `10_ANCORA_protagonista` | `NanoBananaPro_fal` | 16:9 / 4K / png; salva âncora |
| `11_cena01_coldopen` | `NanoBananaPro_fal` → `Veo31_fal` | Veo 8s/16:9/1080p, audio off; dolly-in 35mm |
| `12_cena02_gaiola` | idem | truck lateral, anamórfico |
| `13_cena03_faisca` | `NanoBananaPro_fal` (still) | ECU still 4K |
| `14_cena04_estalo_morph` | 2× `NanoBananaPro_fal` → `Veo31_fal` | **morph** START+END, Veo **6s**, locked-off |
| `15_cena05_hero` | `NanoBananaPro_fal` → `Veo31_fal` | orbit cinematográfico lento |
| `16_cena06_roda_sozinho` | idem | dolly-out pedestal |
| `17_cena07_santuario` | `NanoBananaPro_fal` (still) | wide still, golden hour |
| `18_cena08_libertacao` | `NanoBananaPro_fal` → `Veo31_fal` | push-in lento, golden hour |
| `19_cena09_logo` | `NanoBananaPro_fal` (still) | endcard "Ondokai", sem pessoas |
| `20_FERRAMENTA_rascunho_barato` | `SeedanceImageToVideo_fal` | 480p draft |
| `30_MODELO_cena_nova_keyframe_veo` | `NanoBananaPro_fal` + `Veo31_fal` | molde; `generate_audio=true` |
| `31_MODELO_cena_camera_kling` | `KlingCameraControlI2VNode` + `KlingCameraControls` | câmera numérica |
| `40_ESTENDER_A_veo_handoff` | 2× `Veo31_fal` + `GetImageRangeFromBatch` | handoff de frame |
| `41_ESTENDER_B_kling_nativo` | `KlingImage2VideoNode` + 2× `KlingVideoExtendNode` | encadeia `video_id` |
| `42_ESTENDER_C_seedance_barato` | 2× `SeedanceProImageToVideo_fal` + `GetImageRangeFromBatch` | extend barato |
