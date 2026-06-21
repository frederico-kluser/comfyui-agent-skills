# outfit-swap-api — API Reference (nós e parâmetros)

Duas rotas de troca de roupa. Workflows em formato UI. Ver `knowledge-comfyui-api-nodes` (partner vs fal).

## 👕 `01_flux_vton` — `FluxVTONode` (partner BFL, Comfy credits)
| Campo | Tipo | Exemplo | Nota |
|---|---|---|---|
| `image` (pessoa) | IMAGE | sua foto | |
| `garment` / 2ª imagem | IMAGE | a peça | **single-garment** (1 peça exata) |
| `seed` | INT | `0` / fixed | partner → **login** comfy.org |
> Troca **só** a peça fornecida, preservando pose/rosto/fundo. Billing: créditos Comfy.

## 👗 `02_nanobanana_outfit` — `NanoBananaPro_fal` (Gemini 3, fal)
| Campo | Tipo | Exemplo | Nota |
|---|---|---|---|
| `images` | IMAGE (input) | `ImageBatch(você, look)` | **você = image_1** (âncora), **look = image_2**; empilhe via `ImageResizeKJ`(get_image_size)+`ImageBatch` |
| `prompt` | STRING | prosa nomeando a roupa | sem pronomes, nunca "transform", **nomeie a roupa** |
| `aspect_ratio` | enum | `auto` | |
| `resolution` | enum | `1K` | |
| `output_format` | enum | `png` | |
| `seed` | — | — | **não tem** (Nano Banana Pro trava por âncora) |
> Outfit **completo** (não só 1 peça), com relight para casar a iluminação.

## 🗺️ Mapa por arquivo
| Arquivo | Nó | Billing | Caso |
|---|---|---|---|
| `01_flux_vton` | `FluxVTONode` | Comfy credits | 1 peça exata |
| `02_nanobanana_outfit` | `NanoBananaPro_fal` | fal | look completo |
