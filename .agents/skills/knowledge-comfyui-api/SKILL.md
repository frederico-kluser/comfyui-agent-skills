---
name: knowledge-comfyui-api
description: >-
  Conhecimento de automação do ComfyUI via API HTTP (/prompt, /upload/image, /history, /view, WebSocket)
  e de composição/replace de região em Python puro (Pillow paste com máscara borrada, NumPy alpha blend,
  OpenCV seamlessClone/Poisson). Use ao automatizar geração por código, rodar um workflow por script,
  fazer upload/download de imagens pela API, ou recolar uma região editada na imagem original fora do
  ComfyUI — mesmo sem citar a skill. Serve também para automação de vídeo (serverless/batch).
metadata:
  version: 0.2.0
  type: knowledge
---
# ComfyUI — API HTTP e Composição em Python

Tudo que a UI faz, a API faz. E a recolagem de região pode sair do grafo para Python puro.

## Quando usar
"Automatizar/rodar por código/script", "chamar o ComfyUI por API", "upload/download de imagem programático",
"recolar/compor a região editada na original via código", pipelines/batch.

## Técnicas (um arquivo por técnica)

| Técnica | Arquivo | O que cobre |
|---------|---------|-------------|
| API HTTP | [http-api.md](http-api.md) | /prompt, /upload, /history, /view, WebSocket, edição de workflow |
| Composição Python | [python-composition.md](python-composition.md) | Pillow paste, NumPy alpha blend, OpenCV seamlessClone |

## Referências (nível 3)
- `docs/image-editing.md` §3 (fonte: snippets completos Pillow/NumPy/OpenCV + cliente API).
- Cadeia: o grafo a automatizar → `knowledge-comfyui-workflows`; o que editar → `knowledge-image-editing`.

## Evolução
Append em `LEARNINGS.md` ao achar um endpoint/parâmetro novo, um pitfall de composição, ou um ajuste de cliente. Diff git p/ revisão.
