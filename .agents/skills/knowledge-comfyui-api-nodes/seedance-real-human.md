# Seedance 2.0 — Humano Real (Asset Verificado)

⚠️ `reference_images` / `reference_videos` **recusam pessoa real**. Para colocar uma pessoa real num vídeo,
é preciso verificar o asset.

## Fluxo de verificação
`LoadImage`→`ByteDanceCreateImageAsset` e `LoadVideo`→`ByteDanceCreateVideoAsset` → saídas `asset_id`+`group_id` →
liga o `asset_id` em `model.reference_assets.asset_N`.

- A verificação é **facial, por link H5** que o nó **loga no CONSOLE DO SERVIDOR** (não aparece na UI) e fica em polling.
- **`group_id`** verificado pula a verificação nas próximas vezes — **só na mesma conta**; 1 pessoa por imagem/vídeo.
- Antes de cada geração o nó revalida (`/proxy/seedance/assets/{id}`): status ≠ `Active` → `Reference asset N ... is not Active`.

## Rótulos posicionais no prompt
Assets entram **depois** de images/videos/audios e continuam a contagem do mesmo tipo
(0 refs + asset de imagem → **`Image 1`**; asset de vídeo → **`Video 1`**).

⚠️ A regex de reescrita é `\basset ?(\d{1,2})\b` → `asset 1`/`asset1` viram o rótulo, mas
**`asset_1` (underscore) NÃO casa** e vai cru para o modelo. **Escreva `Image 1`/`Video 1` direto.**

## Dica dos templates oficiais
O `asset_id` passa por um **`PreviewAny`** antes do Seedance (ele mostra **e repassa** a STRING).

## Referências
- Template oficial: `template_seedance2_0_viral_videos_character_swap`
- Bundle: `workflows-api/video-person-swap-seedance-2/`
- Catálogo de vídeo → [catalog-video](catalog-video.md)
