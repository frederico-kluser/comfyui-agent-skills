# API Reference — image-edit-pro-byok

> Schemas extraídos do **OpenAPI ao vivo da fal.ai** em **2026-08-04**. Os quatro motores
> aceitam `prompt` + `image_urls` e **divergem em tudo o mais** — o nó normaliza essas
> diferenças e avisa no console quando clampeia um pedido.
>
> ```bash
> curl -s "https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=bytedance/seedream/v5/pro/edit" | jq .
> ```

---

## Autenticação

| Item | Valor |
|---|---|
| Header | `Authorization: Key $FAL_KEY` |
| Env var | `FAL_KEY` — do ambiente ou de `~/ComfyUI/secrets.env` |
| Host | `https://queue.fal.run/<endpoint_id>` (assíncrono: submit → poll → result) |

O nó usa o **`fal_client`** (já instalado como dependência do `ComfyUI-fal-API`), que faz
upload, submit e polling. É a **mesma chave** do `../video-seedance25-byok/`.

> ⚠️ **Regra de prefixo — é por modelo, não convenção.** `fal-ai/flux-2-pro/edit` e
> `fal-ai/nano-banana-pro/edit` **levam** `fal-ai/`. Já `bytedance/seedream/v5/pro/edit` e
> `openai/gpt-image-2/edit` **não levam**. Errar dá 404.

---

## Os quatro motores — diferenças que importam

| | Seedream 5.0 Pro | FLUX.2 Pro | Nano Banana Pro | GPT Image 2 |
|---|---|---|---|---|
| **Endpoint** | `bytedance/seedream/v5/pro/edit` | `fal-ai/flux-2-pro/edit` | `fal-ai/nano-banana-pro/edit` | `openai/gpt-image-2/edit` |
| **Máx. referências** | 10 (as **últimas** 10 se mandar mais) | — | 14 | **16** |
| **Controle de tamanho** | `image_size`: `auto_1K`, `auto_2K`, presets, ou `{width,height}` | `image_size`: `auto` + presets | `resolution`: **`1K`/`2K`/`4K`** + `aspect_ratio` | `image_size`: `auto` + presets · `quality` |
| **Teto de resolução** | **2048×2048** (mín. 1024×1024) | do input | **4K** | do input |
| **`seed`** | ❌ | ✅ | ✅ | ❌ |
| **`system_prompt`** | ❌ | ❌ | ✅ | ❌ |
| **`safety_tolerance`** | ❌ | `1`–`5` (def. `2`) | `1`–`6` (def. `4`) | ❌ |
| **Máscara** | ❌ | ❌ | ❌ | ✅ `mask_url` |
| **`output_format`** | jpeg/png | jpeg/png | jpeg/png/**webp** | png/jpeg/webp |
| **Saída extra** | — | `seed` | **`description`** | — |

Todos devolvem `images: [{url, ...}]`.

### Detalhes que só aparecem no schema

- **Seedream** tem um teto duro de **4.194.304 px** e piso de **1.048.576 px** — pedir `4K`
  é rejeitado. O nó clampeia para `auto_2K` e **avisa no console** em vez de deixar a API
  falhar.
- **FLUX.2 Pro e GPT Image 2 não têm controle discreto de resolução** — só `auto` e presets
  de proporção. O tamanho sai do próprio input. Por isso o widget `resolucao` é ignorado
  nesses dois (com nota no console).
- **Nano Banana Pro** tem `limit_generations` (default `True`), que ignora instruções no
  prompt sobre quantidade de imagens. O nó não mexe nisso — use `num_images`.
- **GPT Image 2** é o único com `quality` (`auto`/`low`/`medium`/`high`); o nó envia `high`.

---

## `ProImageEditBYOK` — "Pro Image Edit BYOK · Editar foto"

- **Módulo:** `custom_nodes/pro-image-edit-byok` · **Categoria:** `Pro Image Edit BYOK`
- **Saídas:** `images` (**IMAGE**, batch) · `image_url` (STRING) · `descricao` (STRING)

### Inputs

| Nome | Tipo | Obrig. | Default | Nota |
|---|---|---|---|---|
| `model` | COMBO | ✅ | `Seedream 5.0 Pro` | 5 opções (os 4 motores + Seedream Lite) |
| `prompt` | STRING | ✅ | — | Cite as imagens como `Image 1`, `Image 2`… na **ordem dos slots** |
| `resolucao` | COMBO | ✅ | `2K` | `auto` · `1K` · `2K` · `4K`. Traduzido por motor (ver acima) |
| `num_images` | INT | ✅ | `1` | 1–4. **Suba para 3** e escolha o melhor rosto |
| `output_format` | COMBO | ✅ | `png` | PNG é sem perda |
| `seed` | INT | ✅ | `0` | Enviado **só** a FLUX.2 Pro e Nano Banana Pro; nos outros força re-execução |
| `image_1`…`image_6` | IMAGE | — | — | `image_1` é a **BASE**. Viram `image_urls[]` na ordem |
| `mask` | MASK | — | — | **Só o GPT Image 2 usa** (`mask_url`). Nos outros é ignorada com aviso |
| `aspect_ratio` | COMBO | — | `auto` | Só o Nano Banana Pro |
| `system_prompt` | STRING | — | `""` | Só o Nano Banana Pro. Vazio = não enviado |
| `safety_tolerance` | COMBO | — | `4` | `1`–`5`. Omitido em quem não aceita |

### Ordem exata dos `widgets_values`

```
[0] model        [3] num_images      [6] control_after_generate   [9] safety_tolerance
[1] prompt       [4] output_format   [7] aspect_ratio
[2] resolucao    [5] seed            [8] system_prompt
```

> `control_after_generate` é intercalado pelo frontend **logo após `seed`**.
> `image_*` e `mask` são **links**, não widgets — não entram no `widgets_values`.

### Comportamento de normalização

O nó traduz o seu pedido para o parâmetro que **aquele** motor entende:

| Você pede | Seedream | FLUX.2 Pro | Nano Banana Pro | GPT Image 2 |
|---|---|---|---|---|
| `auto` | `image_size=auto_2K` | `image_size=auto` | `resolution=2K` | `image_size=auto` |
| `1K` | `image_size=auto_1K` | `auto` (+ nota) | `resolution=1K` | `auto` (+ nota) |
| `2K` | `image_size=auto_2K` | `auto` (+ nota) | `resolution=2K` | `auto` (+ nota) |
| `4K` | `auto_2K` (**+ aviso**) | `auto` (+ nota) | `resolution=4K` | `auto` (+ nota) |

Validações locais, antes de qualquer chamada paga: prompt não-vazio · ao menos uma imagem ·
número de referências dentro do teto do motor escolhido.

### Detalhes de qualidade embutidos no nó

- **Upload sempre em PNG.** JPEG na *entrada* já custa detalhe de pele antes de o modelo ver
  a foto.
- **Batch de saída:** se o motor devolver imagens de tamanhos diferentes (possível com
  `num_images > 1`), empilhar quebraria o tensor. O nó **avisa e devolve a primeira**, em vez
  de estourar com erro de shape.

---

## `ProFaceRestoreBYOK` — "Pro Image Edit BYOK · Restaurar rosto (passe final)"

- **Endpoint:** `fal-ai/codeformer` · **Saídas:** `image` (IMAGE) · `image_url` (STRING)

O passe de restauração que a literatura de face swap de 2026 aponta como responsável por
boa parte do ganho de qualidade final: limpa artefato de difusão e recupera microtextura
de pele.

| Nome | Tipo | Default | Nota |
|---|---|---|---|
| `image` | IMAGE | — | A imagem já editada |
| `fidelity` | FLOAT | **`0.8`** | **O botão que importa.** Alto = fiel ao rosto de entrada. Baixo = "embeleza" e troca traços. O nó avisa no console abaixo de 0.5 |
| `upscale_factor` | FLOAT | `1.0` | `1.0` = só restaura. Suba para ampliar junto |
| `face_upscale` | BOOLEAN | `true` | Amplia a região do rosto especificamente |
| `only_center_face` | BOOLEAN | `false` | `true` = mexe só no rosto central (preserva as outras pessoas do quadro) |
| `seed` | INT | `0` | Aceito de verdade por este endpoint; `0` = omitido |

`widgets_values`: `[fidelity, upscale_factor, face_upscale, only_center_face, seed,
control_after_generate]` · inputs: `[image]`

> ⚠️ A semântica de `fidelity` do CodeFormer é contraintuitiva: **alto = fiel ao input**,
> baixo = "melhor qualidade" às custas dos traços. O default do endpoint é `0.5`; este nó
> sobe para `0.8` porque o objetivo aqui é preservar identidade, não embelezar.

---

## `ProImageEditCheckKey` — "Pro Image Edit BYOK · Testar Chave"

Sem inputs. Saída `status` (STRING). Custo **zero**: mostra os 4 últimos caracteres da chave e
faz um GET no OpenAPI de cada motor para dizer quais estão roteáveis. `IS_CHANGED` devolve
`NaN` — **sempre reexecuta**.

Roteável ≠ com saldo.

---

## Preço (fal, referência de 2026-08-04)

Ordens de grandeza divulgadas para os motores de edição: **Nano Banana 2 Edit** a partir de
**~US$ 0,06/imagem**; **FLUX.2 [pro] Edit** a **~US$ 0,03/megapixel**; **FLUX.1 Kontext [pro]**
a **~US$ 0,04/imagem**.

Os valores do **Seedream 5.0 Pro**, do **Nano Banana Pro** e do **GPT Image 2** não foram
verificados na fonte primária durante a montagem deste bundle — **confira no painel da fal**
antes de rodar em volume. `num_images = 3` custa aproximadamente 3×.

> ⚠️ Resolução maior custa mais nos modelos cobrados por megapixel. `2K` é o ponto de
> equilíbrio recomendado; `4K` só quando o entregável exigir.

---

## Diferença para os bundles partner

`../image-edit-nano-banana-2/` e `../image-edit-seedream/` usam nós **core partner**
(`GeminiNanoBanana2`, `ByteDanceSeedreamNode`) que passam pelo comfy.org: **cobram crédito
comfy.org e exigem login**, e ficam presos a um modelo por bundle. Além disso o
`GeminiNanoBanana2` é o Gemini 3.1 **Flash** — o tier rápido, não o **Pro**.

Este bundle fala com a fal direto, troca de motor num dropdown e alcança o tier Pro do Gemini.

---

## Referências

- Seedream 5 Pro: `curl -s "https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=bytedance/seedream/v5/pro/edit"`
- FLUX.2 Pro: `…?endpoint_id=fal-ai/flux-2-pro/edit`
- Nano Banana Pro: `…?endpoint_id=fal-ai/nano-banana-pro/edit`
- GPT Image 2: `…?endpoint_id=openai/gpt-image-2/edit`
- Catálogo de edição na fal: `curl -s "https://fal.ai/api/models?keywords=edit"`
- Bundle irmão de vídeo com a mesma chave: `../video-seedance25-byok/`
