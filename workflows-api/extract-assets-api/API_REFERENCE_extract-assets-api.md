# API Reference — extract-assets-api

Campos por nó (conferidos no código-fonte do ComfyUI instalado: `comfy_api_nodes/nodes_recraft.py`,
`custom_nodes/ComfyUI-fal-API`, `nodes.py`). A ordem dos `widgets_values` no `.json` da UI segue a ordem abaixo.

## `NanoBananaPro_fal` (fal · Nano Banana Pro / Gemini 3 Pro Image) — **ISOLA o elemento**
- **inputs (link):** `images` (IMAGE — aqui = a única imagem da interface, vinda do `LoadImage`).
- **widgets (ordem):** `prompt` (STRING — a instrução que nomeia o elemento) · `num_images` (INT=1) ·
  `aspect_ratio` (`auto`/`1:1`/`16:9`/…, use **`auto`**) · `output_format` (`png`) · `resolution` (`1K`/`2K`/`4K`) · `sync_mode` (false).
- **seed:** ❌ não tem (anchor-locked). Sem cache-bust por seed → prompts diferentes por elemento já não colidem;
  re-rodar o MESMO prompt volta do cache do ComfyUI (mude uma palavra p/ forçar).
- **output:** IMAGE (RGB, o elemento isolado sobre fundo branco).
- **billing:** fal credits (`FAL_KEY`).

## `RecraftRemoveBackgroundNode` (partner · "Recraft Remove Background") — **dá o ALPHA**
- **input (link):** `image` (IMAGE — a saída do Nano Banana Pro). **Sem widgets.**
- **outputs:** slot 0 = **`IMAGE` já em RGBA** (4 canais, fundo transparente) · slot 1 = `MASK` (o alpha do recorte).
- **fiação:** ligue o **slot 0 (IMAGE)** direto no `SaveImage` → PNG transparente. **Não** precisa de `JoinImageWithAlpha`
  (o IMAGE já tem alpha; e o `JoinImageWithAlpha` *inverteria* este MASK, que é não-invertido).
- **billing:** **créditos comfy.org** (`price_badge` no nó = **~US$0.01/imagem**). Exige **login** em platform.comfy.org. SEM chave.
- **categoria no menu:** `partner/image/Recraft`.

## `SaveImage` (core) — **escreve o PNG transparente**
- **input:** `images` (IMAGE). **widget:** `filename_prefix` (STRING; aceita subpasta, ex.: `assets/avatar`).
- **alpha:** o `save_images` faz `Image.fromarray()` do tensor cru — se vier **RGBA (4 canais)** salva PNG **com transparência**.
  Como o `RecraftRemoveBackgroundNode` entrega RGBA, a saída é transparente sem nó extra.
- Saída em `ComfyUI/output/<filename_prefix>_NNNNN_.png`.

## `LoadImage` (core)
- A imagem da interface. **outputs:** `IMAGE` (slot 0) · `MASK` (slot 1, não usado).
- No workflow visual há **um único** `LoadImage` alimentando todas as lanes.

## Cadeia (por elemento / por lane)
`LoadImage(UI)` → `NanoBananaPro_fal` (isola o elemento nomeado no prompt) → `RecraftRemoveBackgroundNode` →
`SaveImage` (PNG RGBA transparente).

## Formato API (`extract-assets-api.api.json`, p/ o `extract_assets.py`)
Mesma cadeia, **1 lane**, nós `"10"`(LoadImage) → `"20"`(NanoBananaPro_fal) → `"30"`(RecraftRemoveBackgroundNode) →
`"40"`(SaveImage). O script acha os nós por `class_type` (ids não importam) e troca, por elemento:
`["20"].inputs.prompt` (o texto do elemento) e `["40"].inputs.filename_prefix`.
