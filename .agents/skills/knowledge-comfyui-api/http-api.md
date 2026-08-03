# API HTTP do ComfyUI (porta 8188)

Tudo que a UI faz, a API faz. Automação via REST + WebSocket.

## Pré-requisito
Ative **Settings → "Enable Dev mode Options"** e exporte **"Save (API Format)"** — o `/prompt` SÓ aceita o
**JSON achatado** (`{node_id: {class_type, inputs}}`), nunca o JSON da UI.

## Endpoints
- `POST /prompt` — `{"prompt": <API JSON>, "client_id": <id>}` → `prompt_id`.
- `POST /upload/image` — multipart (campo `image`, `type=input`); use o nome retornado no nó `LoadImage`.
- `GET /history/{prompt_id}` — outputs (filename/subfolder/type).
- `GET /view?filename=&subfolder=&type=` — bytes do arquivo.
- `GET /ws?clientId=` — progresso (espere `executing` com `node==None` e o seu `prompt_id` = fim).

## Editando o workflow no script
```python
wf["10"]["inputs"]["image"] = nome
wf["6"]["inputs"]["text"] = prompt
wf["3"]["inputs"]["seed"] = N
```

## Cuidados
- **Re-rodar exige mudar a seed** (senão volta do cache).
- Sem auth nativa → proxy em produção.

## Cliente pronto
`workflows-cloud/inpaint-region-cropstitch/scripts/run_api.py` (e ref. oficial `script_examples/websockets_api_example.py`).

## Referências
- `docs/image-editing.md` §3
- Composição Python → [python-composition](python-composition.md)
- Grafo a automatizar → `knowledge-comfyui-workflows`
