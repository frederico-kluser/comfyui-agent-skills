# API — Automação HTTP

Automatizar o ComfyUI via API REST + WebSocket.

## Porta
8188 (HTTP+WS).

## Fluxo
`POST /prompt {prompt: <api_json>, client_id}` → acompanhe via `/ws?clientId=` → resultados em `/history/{id}` → arquivos em `/view`.

## ⚠️ Formato
O UI-JSON **não** roda no `/prompt` (precisa do formato API). Veja [json-formats](json-formats.md).

## Referências
- `docs/workflow-guide.md`
- API HTTP completa → `knowledge-comfyui-api`
