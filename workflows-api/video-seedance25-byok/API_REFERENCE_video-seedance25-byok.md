# API Reference — video-seedance25-byok

> Contratos extraídos do **OpenAPI ao vivo da fal.ai** e do **código-fonte instalado**, em
> **2026-08-04**. Nada aqui veio de blog ou de README de marketing — o README oficial do
> repositório `fal-ai/seedance-2.0-api` está *desatualizado* em relação ao schema (inventa um
> input `seed`, esconde 1080p/4k e omite `bitrate_mode`). Reconferir:
>
> ```bash
> curl -s "https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=bytedance/seedance-2.0/reference-to-video" | jq .
> ```

---

## Estado do Seedance 2.5 em 2026-08-04

| Provedor | Situação | Como confirmei |
|---|---|---|
| **fal.ai** | **Roteável, fora do catálogo público.** `bytedance/seedance-2.5/{text,image,reference}-to-video` devolvem OpenAPI **200**; o controle `bytedance/seedance-3.0/text-to-video` devolve **404**. Mas uma busca no catálogo retorna **15 modelos Seedance, nenhum 2.5** | `curl` no OpenAPI e em `fal.ai/api/models?keywords=seedance` |
| **BytePlus ModelArk** | **Anunciado, API fechada.** O ID `dreamina-seedance-2-5-260628` e a tabela de preço já estão publicados, mas a página de criação de task exibe *"API access will be available soon"*. O chamável é a série 2.0 | docs.byteplus.com (páginas 1520757 / 1330310 / 1544106) |
| **Replicate** | **Não existe 2.5.** Só `bytedance/seedance-2.0` (+ `-fast`, `-mini`) | página do modelo |

**O schema 2.5 da fal é um molde do 2.0**: mesmos campos, `duration` ainda limitada a **15 s**
(não os 30 s anunciados pela ByteDance em 2026-07-31) e **sem** `bitrate_mode`. Ou seja: hoje
o 2.5 não oferece vantagem funcional sobre o 2.0. O bundle já traz a opção no widget `model`
para o dia em que a fal liberar — é trocar uma opção do combo, nada mais.

> ⚠️ **Regra de nomenclatura que derruba quem adivinha:** os endpoints **2.x não levam o
> prefixo `fal-ai/`**. É `bytedance/seedance-2.0/...`. Já os v1/v1.5 **levam**
> (`fal-ai/bytedance/seedance/v1.5/pro/image-to-video`). Errar isso dá 404.

---

## Autenticação e transporte (o contrato BYOK)

| Item | Valor |
|---|---|
| Header | `Authorization: Key $FAL_KEY` |
| Env var | `FAL_KEY` — lida do ambiente ou de `~/ComfyUI/secrets.env` |
| Host assíncrono | `https://queue.fal.run/<endpoint_id>` |
| Submit | `POST` → `{request_id, status_url, response_url, cancel_url}` |
| Polling | `GET .../requests/{id}/status` → `IN_QUEUE` · `IN_PROGRESS` · `COMPLETED` |
| Resultado | `GET .../requests/{id}` |
| Cancelar | `PUT .../requests/{id}/cancel` |

O bundle não fala HTTP cru: usa o **`fal_client`** (já instalado no venv do ComfyUI como
dependência do `ComfyUI-fal-API`), que faz upload, submit e polling. Siga sempre o
`status_url` devolvido — não remonte a URL na mão, porque o runtime da fal usa um prefixo
de app truncado.

---

## `SeedanceBYOKReferenceToVideo` — "Seedance BYOK · Reference to Video"

- **Módulo:** `custom_nodes/seedance-byok` (deste bundle) · **Categoria:** `Seedance BYOK`
- **Endpoint:** `bytedance/seedance-2.{0,5}[/fast|/mini]/reference-to-video`
- **Billing:** fal.ai, por token de vídeo · **Chave:** `FAL_KEY`
- **Saídas:** `video` (**VIDEO nativo**) · `video_url` (STRING)

### Inputs

| Nome | Tipo | Obrig. | Default | Nota |
|---|---|---|---|---|
| `model` | COMBO | ✅ | `Seedance 2.0` | `Seedance 2.5 (assim que a fal publicar)` · `Seedance 2.0` · `Seedance 2.0 Fast` · `Seedance 2.0 Mini` |
| `prompt` | STRING | ✅ | — | **Único campo obrigatório da API.** Cite as referências como `@Image1`, `@Video1`, `@Audio1` |
| `resolution` | COMBO | ✅ | `720p` | `480p` · `720p` · `1080p` · `4k`. **Fast e Mini só vão até 720p** — o nó recusa antes de gastar |
| `aspect_ratio` | COMBO | ✅ | `auto` | `auto` · `21:9` · `16:9` · `4:3` · `1:1` · `3:4` · `9:16` |
| `duration` | COMBO | ✅ | `auto` | `auto` ou `4`…`15` (string, não int) |
| `generate_audio` | BOOLEAN | ✅ | `true` | Gera áudio novo. **Custa o mesmo ligado ou desligado** |
| `seed` | INT | ✅ | `0` | ⚠️ **Não é enviado à API.** O Seedance 2.x na fal **não tem** input de seed. Serve só para forçar re-execução do nó |
| `image_1`…`image_4` | IMAGE | — | — | Viram `image_urls[]` → `@Image1`…`@Image4` |
| `video_1`, `video_2` | VIDEO | — | — | Viram `video_urls[]` → `@Video1`, `@Video2` |
| `audio_1` | AUDIO | — | — | Vira `audio_urls[]` → `@Audio1` |
| `bitrate_mode` | COMBO | — | `standard` | `standard` · `high`. **Só existe no 2.0 e no 2.0 Fast** — o nó omite do payload nos demais |
| `end_user_id` | STRING | — | `""` | Opcional; atribuição de abuso do lado da fal |

### Ordem exata dos `widgets_values`

```
[0] model          [4] duration         [8]  bitrate_mode
[1] prompt         [5] generate_audio   [9]  end_user_id
[2] resolution     [6] seed
[3] aspect_ratio   [7] control_after_generate
```

> `control_after_generate` é intercalado pelo frontend **logo após `seed`**. Reconstruir o nó
> fora dessa ordem embaralha os widgets **em silêncio**.
> `image_*`, `video_*` e `audio_1` são **links**, não widgets — não entram no `widgets_values`.

### Limites validados no nó (antes de gastar crédito)

| Regra | Valor |
|---|---|
| Imagens | ≤ 9 · ≤30 MB cada · lado entre 300 e 6000 px · JPEG/PNG/WebP |
| Vídeos | ≤ 3 · **somados entre 2 e 15 s** · total <50 MB · cada um entre ~480p (640×640) e ~720p (834×1112) · MP4/MOV |
| Áudios | ≤ 3 · somados ≤15 s · ≤15 MB cada · MP3/WAV |
| **Total** | **≤ 12 arquivos** somando todas as modalidades |
| Áudio sozinho | **proibido** — exige ao menos 1 imagem ou 1 vídeo |

Só `maxItems` (9/3/3) é imposto pelo schema; os limites de MB, segundos e pixels são texto
e **falham no servidor**. Por isso o nó valida localmente o que dá para validar.

### Rótulos posicionais — a diferença que quebra copy-paste

Três rotas para o **mesmo modelo** usam **três sintaxes diferentes** no prompt:

| Rota | Como citar a referência |
|---|---|
| **fal (este bundle)** | `@Image1` · `@Video1` · `@Audio1` |
| Replicate | `[Image1]` · `[Video1]` |
| Partner comfy.org (`ByteDance2ReferenceNode`) | `Image 1` · `Video 1` (sem `@`, com espaço) |

Prompt copiado do bundle `../video-person-swap-seedance-2/` **não funciona aqui sem traduzir
os rótulos**. O nó imprime um aviso no console quando você liga uma referência que o prompt
nunca cita.

---

## `SeedanceBYOKImageToVideo` — "Seedance BYOK · Image to Video (first/last)"

- **Endpoint:** `bytedance/seedance-2.{0,5}[/fast|/mini]/image-to-video`
- **Saídas:** `video` (VIDEO) · `video_url` (STRING)

| Nome | Tipo | Obrig. | Nota |
|---|---|---|---|
| `first_frame` | IMAGE | ✅ | Vira `image_url` |
| `prompt` | STRING | ✅ | Obrigatório também aqui |
| `last_frame` | IMAGE | — | Vira `end_image_url` — fecha o clipe neste frame |
| demais | — | — | Iguais aos do reference-to-video |

`widgets_values`: `[model, prompt, resolution, aspect_ratio, duration, generate_audio, seed,
control_after_generate, bitrate_mode, end_user_id]` · inputs: `[first_frame, last_frame]`.

> ⚠️ Na **Replicate** (rota alternativa) `reference_images` é **mutuamente exclusivo** com
> `image`/`last_frame_image`. Na fal são endpoints separados, então a exclusão é natural: ou
> você usa reference-to-video, ou image-to-video.

---

## `WanAnimateBYOK` — "Wan Animate BYOK · Editar o vídeo original"

O único nó do bundle que **edita** em vez de recriar. Sem prompt, sem máscara: a performance
sai do próprio vídeo.

- **Endpoints:** `fal-ai/wan/v2.2-14b/animate/replace` · `fal-ai/wan/v2.2-14b/animate/move`
- **Saídas:** `video` (VIDEO) · `video_url` (STRING) · `prompt_gerado` (STRING)

> ⚠️ **Este endpoint LEVA o prefixo `fal-ai/`** — ao contrário do Seedance 2.x. A regra do
> prefixo é **por modelo**, não uma convenção da fal. Confirmado ao vivo: com prefixo → 200,
> sem prefixo → 404.

| Nome | Tipo | Obrig. | Default | Nota |
|---|---|---|---|---|
| `mode` | COMBO | ✅ | `replace` | `replace` troca a pessoa do vídeo · `move` anima a foto com o movimento do vídeo |
| `image` | IMAGE | ✅ | — | Vira `image_url` — a pessoa que **entra**, corpo inteiro |
| `video` | VIDEO | ✅ | — | Vira `video_url` — o plano a **editar** |
| `resolution` | COMBO | ✅ | `480p` | `480p` · `580p` · `720p`. **480p é o piso e o default do endpoint** |
| `use_turbo` | BOOLEAN | ✅ | `true` | Rota rápida; o endpoint auto-otimiza os parâmetros |
| `num_inference_steps` | INT | ✅ | `20` | 1…40 |
| `guidance_scale` | FLOAT | ✅ | `1.0` | ⚠️ **Modelo destilado: >1.0 BORRA o vídeo.** O nó avisa no console |
| `shift` | FLOAT | ✅ | `5.0` | 1.0…10.0 — **`5.0` é o default real do endpoint** |
| `video_quality` | COMBO | ✅ | `high` | Qualidade de **encode**, não de geração |
| `seed` | INT | ✅ | `0` | **Aqui a seed funciona de verdade.** `0` = o nó omite e a fal sorteia |
| `enable_safety_checker` | BOOLEAN | — | `false` | |

`widgets_values`: `[mode, resolution, use_turbo, num_inference_steps, guidance_scale, shift,
video_quality, seed, control_after_generate, enable_safety_checker]` · inputs: `[image, video]`.

**Sem prompt na entrada** — mas o modelo **escreve um** e devolve em `prompt`, exposto como
`prompt_gerado`. Útil para entender o que ele achou que estava vendo.

> ⚠️ **A saída não traz o áudio original.** Remuxe depois:
> ```bash
> ffmpeg -i saida.mp4 -i original.mp4 -c:v copy -map 0:v:0 -map 1:a:0 -shortest final.mp4
> ```

### Divergência com o `ComfyUI-fal-API`

O custom node `Wan2214b_animate_replace_character_fal` (documentado em
`../video-person-replace/`) é um wrapper **desatualizado** em relação ao endpoint ao vivo:
ele expõe `turbo` (hoje `use_turbo`), `shift` default **8** (hoje **5**), um campo
`variations` que não existe mais no schema, e devolve `video_url`/`frames_zip_url` como
STRING em vez do objeto `video`. Este nó fala com o endpoint real.

---

## `VideoUpscaleBYOK` — "Video BYOK · Upscale (passe final)"

Dois motores, um nó. Saídas: `video` (VIDEO) · `video_url` (STRING).

| Motor | Endpoint | Força |
|---|---|---|
| **SeedVR** *(padrão)* | `fal-ai/seedvr/upscale/video` | Difusão — **reconstrói** detalhe. Melhor em rosto |
| **Topaz** | `fal-ai/topaz/upscale/video` | Controle fino + interpolação de fps |

| Nome | Tipo | Default | Aplica a |
|---|---|---|---|
| `video` | VIDEO | — | ambos |
| `engine` | COMBO | SeedVR | — |
| `upscale_factor` | FLOAT | `2.0` | ambos (1.0–4.0) |
| `seed` | INT | `0` | só SeedVR (`0` = omitido) |
| `seedvr_output_quality` | COMBO | `high` | `low`/`medium`/`high`/`maximum` |
| `topaz_model` | COMBO | `Proteus` | `Artemis HQ/MQ`, `Gaia HQ`, `Nyx`, `Starlight HQ` |
| `topaz_target_fps` | INT | `0` | `0` = não interpola; `>0` liga interpolação |

`widgets_values`: `[engine, upscale_factor, seed, control_after_generate,
seedvr_output_quality, topaz_model, topaz_target_fps]` · inputs: `[video]`

O nó monta payloads **diferentes** por motor: o SeedVR usa `upscale_mode="factor"` +
`output_quality`; o Topaz usa `model` + `target_fps` opcional. Parâmetros do motor não
escolhido são simplesmente não enviados.

> ⚠️ **Amplie por último.** E confira o áudio: se o seu fluxo passou pelo Wan Animate (que
> não devolve áudio), remuxe no fim.

---

## `SeedanceBYOKLastFrame` — "Seedance BYOK · Último Frame"

Local, custo zero. `video` (VIDEO) → `IMAGE`. Widget `offset_from_end` (INT, default `0`):
`0` = último frame; suba para 1–3 se o último frame estiver borrado.

Existe para o workflow de cena longa não depender de custom node externo
(`GetImageRangeFromBatch` do KJNodes faria o mesmo).

---

## `SeedanceBYOKCheckKey` — "Seedance BYOK · Testar Chave"

Sem inputs. Saída `status` (STRING). Custo **zero**: confere se a `FAL_KEY` carregou (mostra
só os 4 últimos caracteres) e faz um GET no OpenAPI de cada modelo para dizer quais estão
roteáveis agora. `IS_CHANGED` devolve `NaN`, então **sempre reexecuta**.

Use antes de qualquer geração — é o diagnóstico mais barato do bundle.

---

## Preço (fal, tabela oficial de 2026-08-04)

A cobrança real é **por token**:

```
tokens = altura × largura × (duração do vídeo de ENTRADA + duração da SAÍDA) × 24 / 1024
```

| Faixa | US$ por 1000 tokens |
|---|---|
| 480p / 720p / 1080p | 0,014 |
| 4k | 0,008 |
| Fast | 0,0112 |
| Mini | 0,007 |

Equivalências publicadas pela fal para o **reference-to-video** do 2.0:
**720p ≈ US$ 0,3034/s** · **1080p ≈ US$ 0,682/s**. Com vídeo de entrada a *taxa* cai para
**US$ 0,1814/s a 720p** — mas a base de tokens **cresce**, porque a duração da entrada entra
na conta.

> ⚠️ **A armadilha de custo mais cara deste bundle.** "Vídeo de referência é mais barato" é
> falso. Uma saída de 5 s a 720p guiada por um vídeo de referência de 10 s bilha
> `15 s × 0,1814 ≈ US$ 2,72` — cerca de **US$ 0,54 por segundo de saída**, quase o dobro da
> taxa sem vídeo. Corte o vídeo de referência ao mínimo que ainda ensina o movimento.
>
> Os valores por segundo da própria fal não fecham exatamente com a fórmula dela
> (1280×720×1×24/1024 = 21.600 tokens = US$ 0,3024/s, não 0,3034). **Estime pelos tokens.**
>
> O Seedance **2.5 não tem preço publicado** na fal.

---

## Saída, áudio e validade da URL

O resultado é `{"video": {"url", "content_type", "file_name", "file_size"}, "seed": int}` —
um **MP4 com o áudio já embutido**.

O nó **baixa o MP4 inteiro** e devolve `VIDEO` nativo (`InputImpl.VideoFromFile`), que vai
direto no `SaveVideo` com o áudio intacto.

> ⚠️ **Não** use `LoadVideoURL` para trazer o resultado: ele extrai **frames (IMAGE)** e o
> áudio se perde. É o erro clássico dos grafos `*_fal` (padrão A). Aqui o padrão é o B.
>
> A saída `video_url` é útil para baixar em resolução original fora do ComfyUI, mas
> **expira** — a URL de resultado da fal é temporária. Baixe no mesmo dia.

---

## Rota alternativa: BytePlus ModelArk direto (`ARK_API_KEY`)

Não é usada por este bundle, mas está documentada porque é a origem de tudo — os nós partner
do core do ComfyUI são um **proxy fino** sobre ela (`comfy_api_nodes/nodes_bytedance.py`,
`/proxy/byteplus-seedance2/api/v3/contents/generations/tasks`).

```http
POST https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks
Authorization: Bearer $ARK_API_KEY
Content-Type: application/json

{
  "model": "dreamina-seedance-2-0-260128",
  "content": [
    {"type": "text",      "text": "..."},
    {"type": "image_url", "image_url": {"url": "..."}, "role": "reference_image"},
    {"type": "video_url", "video_url": {"url": "..."}, "role": "reference_video"},
    {"type": "audio_url", "audio_url": {"url": "..."}, "role": "reference_audio"}
  ],
  "generate_audio": true, "resolution": "1080p", "ratio": "adaptive",
  "duration": 8, "watermark": false
}
→ {"id": "cgt-2026…"}

GET  https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks/{id}
→ {"status": "succeeded", "content": {"video_url": "…"}}
```

`role` aceita `first_frame`, `last_frame`, `reference_image` (imagens), `reference_video`,
`reference_audio`. Primeiro-frame, primeiro+último-frame e multi-referência são **três modos
mutuamente exclusivos**. `seed` e `camera_fixed` **não são suportados** no Seedance 2.0.
A URL de resultado expira em **24 h** (`X-Tos-Expires=86400`); o ID da task vive 7 dias.

### Por que o bundle **não** usa esta rota

A ModelArk **proíbe explicitamente** subir imagem ou vídeo de referência com **rosto de
pessoa real**: *"Seedance 2.0 series models do not support direct upload of reference images
or videos containing real human faces."* As três saídas autorizadas são (a) vídeos que a sua
própria conta gerou nos últimos 30 dias, (b) personagens virtuais do catálogo, (c) assets de
pessoa real registrados por um fluxo de **QR code no console + verificação facial + consentimento
do titular**, referenciados como `asset://<ASSET_ID>`.

Ou seja: a rota ModelArk tem o mesmo pedágio de verificação do comfy.org — e ele **não é
acessível só com a chave**, exige o console. A fal e a Replicate não expõem nenhum campo de
verificação de identidade (só o `end_user_id` opcional), o que torna a fal a rota BYOK
prática. **Isso não é permissão** — veja "Uso responsável" no README.

---

## Modelos e rotas — resumo

| Nome no widget | Endpoint fal | Resoluções | `bitrate_mode` |
|---|---|---|---|
| `Seedance 2.5 (assim que a fal publicar)` | `bytedance/seedance-2.5` | 480p–4k | ❌ |
| `Seedance 2.0` | `bytedance/seedance-2.0` | 480p–4k | ✅ |
| `Seedance 2.0 Fast` | `bytedance/seedance-2.0/fast` | 480p · 720p | ✅ |
| `Seedance 2.0 Mini (rascunho barato)` | `bytedance/seedance-2.0/mini` | 480p · 720p | ❌ |

## Referências

- Nós de API online (catálogo geral): `.agents/skills/knowledge-comfyui-api-nodes`
- Bundle irmão em créditos comfy.org: `../video-person-swap-seedance-2/`
- Bundle que **edita** o vídeo original: `../video-person-replace/`
- Fonte do proxy partner: `ComfyUI/comfy_api_nodes/nodes_bytedance.py`
- Anúncio do Seedance 2.5: <https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5>
