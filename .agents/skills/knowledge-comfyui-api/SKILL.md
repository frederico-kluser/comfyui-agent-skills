---
name: knowledge-comfyui-api
description: >-
  Conhecimento de automação do ComfyUI via API HTTP (/prompt, /upload/image, /history, /view, WebSocket)
  e de composição/replace de região em Python puro (Pillow paste com máscara borrada, NumPy alpha blend,
  OpenCV seamlessClone/Poisson). Use ao automatizar geração por código, rodar um workflow por script,
  fazer upload/download de imagens pela API, ou recolar uma região editada na imagem original fora do
  ComfyUI — mesmo sem citar a skill. Serve também para automação de vídeo (serverless/batch).
metadata:
  version: 0.1.0
  type: knowledge
---
# ComfyUI — API HTTP e Composição em Python

Tudo que a UI faz, a API faz. E a recolagem de região pode sair do grafo para Python puro.

## Quando usar
"Automatizar/rodar por código/script", "chamar o ComfyUI por API", "upload/download de imagem programático",
"recolar/compor a região editada na original via código", pipelines/batch.

## API HTTP (porta 8188)
Ative **Settings → "Enable Dev mode Options"** e exporte **"Save (API Format)"** — o `/prompt` SÓ aceita o
**JSON achatado** (`{node_id: {class_type, inputs}}`), nunca o JSON da UI.
- `POST /prompt` — `{"prompt": <API JSON>, "client_id": <id>}` → `prompt_id`.
- `POST /upload/image` — multipart (campo `image`, `type=input`); use o nome retornado no nó `LoadImage`.
- `GET /history/{prompt_id}` — outputs (filename/subfolder/type). `GET /view?filename=&subfolder=&type=` — bytes.
- `GET /ws?clientId=` — progresso (espere `executing` com `node==None` e o seu `prompt_id` = fim).
- **Re-rodar exige mudar a seed** (senão volta do cache). Sem auth nativa → proxy em produção.
- Edite o workflow no script: `wf["10"]["inputs"]["image"]=nome`, `wf["6"]["inputs"]["text"]=prompt`, `wf["3"]["inputs"]["seed"]=N`.
- Cliente pronto: `workflows-cloud/inpaint-region-cropstitch/scripts/run_api.py` (e ref. oficial `script_examples/websockets_api_example.py`).

## Composição/replace em Python (fora do ComfyUI)
Fórmula única (alpha matte): `saída = original*(1−m) + editada*m`. Feathering = transição invisível.
- **Pillow**: `result.paste(edited,(0,0), mask.filter(ImageFilter.GaussianBlur(10)))` (copie a original antes; `paste` é in-place). Ou `Image.composite(edited, original, mask_blur)`.
- **NumPy**: normalize `m/255.0` ANTES, `m=m[...,None]` p/ broadcast, `out=orig*(1-m)+edited*m`, `clip(0,255)`.
- **OpenCV `seamlessClone`** (Poisson): casa gradientes, borda invisível. `center` = centro do `boundingRect(mask)`, é **(x,y)**. `NORMAL_CLONE` preserva textura; `MIXED_CLONE` p/ estruturas finas. Cuidados: o src deve caber no dst ao redor do center (senão erro -215); guarde `if np.any(mask)`; pode **alterar cor/luz** — p/ fidelidade de pixels prefira o alpha blend feathered.
- Script pronto: `workflows-cloud/inpaint-region-cropstitch/scripts/compose.py` (alpha-blend e seamlessclone por flag).

## Quando usar cada um
Fidelidade de pixels exata (cor original) → **alpha blend feathered** (Pillow/NumPy). Harmonizar cor/luz da
região com o entorno → **seamlessClone**. Dentro do ComfyUI, o equivalente nativo é **Inpaint Stitch** /
**ImageCompositeMasked** (`mask*source + (1-mask)*destination`).

## Referências (nível 3)
- `docs/image-editing.md` §3 (fonte: snippets completos Pillow/NumPy/OpenCV + cliente API).
- Cadeia: o grafo a automatizar → `knowledge-comfyui-workflows`; o que editar → `knowledge-image-editing`.

## Evolução
Append em `LEARNINGS.md` ao achar um endpoint/parâmetro novo, um pitfall de composição, ou um ajuste de cliente. Diff git p/ revisão.
