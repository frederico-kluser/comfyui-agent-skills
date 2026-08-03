# API Online — Gotchas dos Nós fal

## Bloqueio sem barra de progresso
`handler.get()` faz polling. Cold-start fica **minutos em `IN_QUEUE`** e ainda COMPLETA — não é travamento.

### Diagnóstico
```bash
comfyui logs → request_id
curl -H "Authorization: Key $FAL_KEY" https://queue.fal.run/<endpoint>/requests/<id>/status
```

### Interrupção
`/interrupt` **não** mata o nó; só **reiniciar o servidor** mata.
Itere em endpoints **warm** (Nano Banana Pro / Seedream / Kontext, ~30–60 s).

## Padrões de saída de vídeo
- **(A) Nós fal `*_fal`**: `video_url (STRING)` → `LoadVideoURL` → `CreateVideo` → `SaveVideo`. ⚠️ perde o áudio nativo (baixe a URL original).
- **(B) Nós partner**: **`VIDEO`** nativo → direto no `SaveVideo` (áudio preservado).
- Entrada V2V = core **`LoadVideo`** (saída `VIDEO`). `LoadVideoURL`/`VHS_LoadVideo` dão frames IMAGE, não servem.

## Stub trap
`/object_info/<Node>` devolve **200 com corpo vazio** para nós que o Manager conhece mas **não estão carregados**.
- "Aparece na busca" ≠ instalado (confira `python_module` não-nulo).
- Liste reais: `curl -s :8188/object_info | jq 'keys'`.

## Erro "Failed to upload video"
Só aparece no **console do servidor** — não na UI.

## Referências
- Seed gates → [seed-gates](seed-gates.md)
- Schemas V3 → [schemas-v3](schemas-v3.md)
