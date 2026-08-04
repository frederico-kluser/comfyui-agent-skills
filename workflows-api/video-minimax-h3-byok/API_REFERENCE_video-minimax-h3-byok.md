# API Reference — video-minimax-h3-byok

> Contrato extraído da **documentação oficial da MiniMax** e **confirmado ao vivo** em
> **2026-08-04** (os três endpoints respondem, e sem chave devolvem o `authorized_error`
> documentado). Fonte primária:
> <https://platform.minimax.io/docs/api-reference/video-generation-v2-create>
>
> Reconferir a credencial a qualquer momento:
> ```bash
> curl -s -o /dev/null -w '%{http_code}\n' \
>   -H "Authorization: Bearer $MINIMAX_API_KEY" \
>   https://api.minimax.io/v2/query/video_generation/0
> # 401 = chave ruim · qualquer outro código = credencial aceita
> ```

---

## Os três endpoints usados pelo bundle

| Passo | Método e URL | Auth |
|---|---|---|
| 1 · subir arquivo | `POST https://api.minimax.io/v1/files/upload` (multipart) | `Authorization: Bearer <key>` |
| 2 · criar tarefa | `POST https://api.minimax.io/v2/video_generation` | idem + `Content-Type: application/json` |
| 3 · consultar | `GET https://api.minimax.io/v2/query/video_generation/{task_id}` | idem |

> Repare na mistura de versões: o **upload é `v1`**, a **geração é `v2`**. Não é engano.
>
> O host pode ser trocado pela env var **`MINIMAX_API_HOST`** (existe uma plataforma separada
> para a China continental, com outro domínio). Default: `https://api.minimax.io`.

### 1 · Upload → `mm_file://`

```
POST /v1/files/upload            Content-Type: multipart/form-data
  purpose = video_generation_input        (obrigatório)
  file    = <binário>                     (obrigatório)
→ {"file": {"file_id": 123456, ...}, "base_resp": {"status_code": 0, "status_msg": "success"}}
```

Referencie depois como **`mm_file://123456`**. O arquivo **vale 7 dias**.

Limites por `purpose=video_generation_input`: imagens **30 MB** (jpg/jpeg/png/webp/heic/heif),
vídeo **50 MB** (mp4/mov), áudio **15 MB** (wav/mp3).

> **Por que upload e não base64.** A API aceita `data:<tipo>;base64,<...>` embutido, mas o
> corpo do POST de geração tem teto de **64 MB** e base64 infla ~33% — um vídeo de referência
> estoura. O upload evita isso por completo.
>
> ⚠️ Sempre confira `base_resp.status_code == 0`: a MiniMax pode devolver **HTTP 200 com erro
> no corpo**. O nó valida isso.

### 2 · Criar a tarefa

```jsonc
POST /v2/video_generation
{
  "model": "MiniMax-H3",            // obrigatório
  "content": [ /* ver abaixo */ ],  // obrigatório
  "resolution": "768P",             // obrigatório — "768P" | "2K"
  "duration": 6,                    // obrigatório — inteiro, 4..15
  "ratio": "16:9",                  // opcional — só no text-to-video
  "callback_url": "https://…"       // opcional
}
→ {"task_id": "424010985738629"}
```

### 3 · Consultar (polling)

```jsonc
GET /v2/query/video_generation/{task_id}
→ {"task": {
     "id": "…", "model": "MiniMax-H3",
     "status": "queued" | "running" | "succeeded" | "failed" | "cancelled",
     "content": {"url": "…mp4"},        // presente quando succeeded
     "resolution": "768P", "duration": 6, "ratio": "…",
     "usage": {"total_seconds": …, "input_seconds": …,
               "output_seconds": …, "input_image_count": …},
     "error": {"code": …, "message": "…"}   // quando failed
   }}
```

`content.url` é **temporária** — baixe na hora (o nó já faz). Expirou? Consulte de novo para
obter uma URL nova.

---

## O array `content` — onde mora toda a semântica

Cada item tem um `type` e, para mídia, um `role`:

| `type` | Campo da URL | `role` possíveis |
|---|---|---|
| `text` | `text` (a string do prompt) | — |
| `image_url` | `image_url.url` | `first_frame` · `last_frame` · `reference_image` |
| `video_url` | `video_url.url` | `reference_video` |
| `audio_url` | `audio_url.url` | `reference_audio` |

Formatos aceitos em `url`: **HTTPS público**, **`mm_file://{file_id}`** ou
**`data:<tipo>;base64,<...>`**.

### As três regras que a API impõe

1. **Sempre um item `text` não-vazio** — em todos os modos, inclusive image-to-video.
   Máx. **7000 caracteres**.
2. **Image-to-video e reference-to-video são mutuamente exclusivos.** Havendo qualquer
   `reference_*`, não pode haver `first_frame`/`last_frame` — e vice-versa. É por isso que o
   bundle tem **nós separados** em vez de um só com tudo.
3. **`reference_audio` nunca vem sozinho** — exige ao menos uma imagem ou vídeo de referência.

### Limites de mídia

| Tipo | Qtd. | Tamanho | Dimensão | Proporção | Duração | Outros |
|---|---|---|---|---|---|---|
| Imagem | ≤9 ref · ≤1 first · ≤1 last | ≤30 MB | 256–5760 px | 0,4–2,5 | — | JPG/JPEG/PNG/WEBP/HEIC/HEIF |
| Vídeo | ≤3 | ≤50 MB | 256–5760 px | 0,4–2,5 | 2–15 s cada, **total ≤15 s** | MP4/MOV · H.264 ou H.265 · áudio AAC/MP3 · 23,976–60 fps |
| Áudio | ≤3 | ≤15 MB | — | — | 2–15 s cada, **total ≤15 s** | WAV/MP3 |

Corpo total do request: **≤64 MB**.

### Como o prompt cita as referências

**Linguagem natural**, seguindo a ordem dos itens — não há sintaxe de tag. Exemplo verbatim
da documentação:

> *"Character speaks: Follow the wind, live free. Leave worries behind, enjoy the moment.
> **Voice timbre follows reference audio 1**."*

Duas convenções úteis que aparecem no doc oficial: **`Character speaks: "…"`** define a fala,
e **`Voice timbre follows reference audio N.`** amarra o timbre.

> ⚠️ O modelo **open-weights** (o do tutorial do comfy.org, que roda em GPU local) usa outra
> convenção: `<Picture 1>`, `<Video 1>`. **Não misture** — na API é linguagem natural.

---

## Os nós do bundle

Todos em **`Módulo: custom_nodes/minimax-h3-byok`**, categoria **`MiniMax BYOK`**,
chave **`MINIMAX_API_KEY`** (ambiente ou `~/ComfyUI/secrets.env`).

### `MiniMaxH3BYOKReferenceToVideo` — "MiniMax H3 BYOK · Reference to Video"

Saídas: `video` (**VIDEO nativo**) · `video_url` (STRING).

| Nome | Tipo | Obrig. | Default | Nota |
|---|---|---|---|---|
| `prompt` | STRING | ✅ | — | Máx. 7000 chars. Cite *"reference image 1"* etc. |
| `resolution` | COMBO | ✅ | `768P` | `768P` · `2K` |
| `duration` | COMBO | ✅ | `6` | `4`…`15` (enviado como **inteiro**) |
| `seed` | INT | ✅ | `0` | ⚠️ **Não vai para a API** — a v2 não aceita seed. Só força re-execução |
| `image_1`…`image_4` | IMAGE | — | — | Viram `role: reference_image` |
| `video_1`, `video_2` | VIDEO | — | — | Viram `role: reference_video` |
| `audio_1` | AUDIO | — | — | Vira `role: reference_audio` |
| `callback_url` | STRING | — | `""` | Se preenchido, a MiniMax faz POST do progresso e **exige** que o seu servidor devolva o `challenge` em **3 s**. Deixe vazio se não tem isso montado |

`widgets_values`: `[prompt, resolution, duration, seed, control_after_generate, callback_url]`
inputs: `[image_1, image_2, image_3, image_4, video_1, video_2, audio_1]`

> `ratio` **não** é exposto aqui de propósito: neste modo a API força `adaptive`.

### `MiniMaxH3BYOKImageToVideo` — "… Image to Video (first/last)"

| Nome | Tipo | Obrig. | Nota |
|---|---|---|---|
| `first_frame` | IMAGE | ✅ | `role: first_frame` |
| `prompt` | STRING | ✅ | Obrigatório também aqui |
| `last_frame` | IMAGE | — | `role: last_frame` |
| `resolution`, `duration`, `seed`, `callback_url` | — | — | Iguais |

`widgets_values`: `[prompt, resolution, duration, seed, control_after_generate, callback_url]`
inputs: `[first_frame, last_frame]`

### `MiniMaxH3BYOKTextToVideo` — "… Text to Video"

Único nó com **`ratio`**, que aqui é **obrigatório**: `21:9` · `16:9` · `4:3` · `1:1` ·
`3:4` · `9:16` (sem `adaptive`).

`widgets_values`: `[prompt, ratio, resolution, duration, seed, control_after_generate, callback_url]`
inputs: nenhum.

### `MiniMaxH3BYOKLastFrame` — "… Último Frame"

Local, custo zero. `video` (VIDEO) → `IMAGE`. Widget `offset_from_end` (INT, `0` = último
frame; suba para 1–3 se o último estiver borrado). Existe para o workflow de cena longa não
depender de custom node externo.

### `MiniMaxH3BYOKCheckKey` — "… Testar Chave"

Sem inputs, saída `status` (STRING), custo **zero**. Mostra o host, os 4 últimos caracteres da
chave e consulta um `task_id` inexistente: **401 = credencial ruim**; qualquer outro código =
credencial aceita. `IS_CHANGED` devolve `NaN`, então **sempre reexecuta**.

> Aceitação **não é saldo**. Sem crédito a geração falha com `insufficient_balance_error`.

---

## Erros — o que cada um quer dizer

| HTTP | `error.type` | Significado | O que fazer |
|---|---|---|---|
| 400 | `bad_request_error` | Payload inválido | Confira prompt não-vazio, resolução, duração e as regras de `role` |
| 401 | `authorized_error` | Chave ausente/inválida | Regere no Console → API Keys |
| 402 | `insufficient_balance_error` | Sem saldo | Recarregue |
| 422 | `unprocessable_entity_error` | Moderação bloqueou | Reformule prompt/referência |
| 429 | `rate_limit_error` | Limite de requisições | Espere e repita |
| 500 | `server_error` | Erro do servidor | Repita mais tarde |

Formato do corpo de erro:

```json
{"type":"error","error":{"type":"authorized_error","message":"… (1004)","http_code":"401"},
 "request_id":"06c129874198619ff3613d9c2f4fc16c"}
```

O `request_id` é o que a MiniMax pede em qualquer suporte — o nó o inclui na mensagem de erro.

---

## Preço

A MiniMax **não publica** a tabela de preço de vídeo na referência da API (fica atrás do link
*Pricing* do console e varia por resolução e duração). Este documento **não estima números**.

Meça: o campo `usage` da resposta (`total_seconds`, `input_seconds`, `output_seconds`,
`input_image_count`) é impresso no console pelo nó ao concluir. Uma chamada de
`768P` / 4 s no workflow **`so-texto`** é o teste mais barato para calibrar.

---

## Diferença para os nós partner do ComfyUI

O core do ComfyUI já traz `MinimaxTextToVideoNode`, `MinimaxImageToVideoNode`,
`MinimaxSubjectToVideoNode` e `MinimaxHailuoVideoNode` — mas eles:

- passam pelo proxy do comfy.org (`/proxy/minimax/video_generation`), ou seja **cobram
  crédito comfy.org e exigem login**;
- falam a **API v1**, cujos modelos são `T2V-01`, `I2V-01`, `S2V-01`, `MiniMax-Hailuo-02` —
  **não** o `MiniMax-H3`;
- usam o fluxo antigo de `files/retrieve` para pegar o arquivo, que na v2 não existe mais
  (a URL vem direto em `content.url`).

Este bundle fala **v2 + `MiniMax-H3`** direto, com a sua chave.

---

## Referências

- Criar tarefa: <https://platform.minimax.io/docs/api-reference/video-generation-v2-create>
- Consultar tarefa: <https://platform.minimax.io/docs/api-reference/video-generation-v2-query>
- Upload: <https://platform.minimax.io/docs/api-reference/file-management-upload>
- Guia de vídeo: <https://platform.minimax.io/docs/guides/video-generation>
- Caminho open-weights local (outro produto): <https://docs.comfy.org/tutorials/video/minimax/minimax-h3>
- Bundle irmão em `FAL_KEY`: `../video-seedance25-byok/`
