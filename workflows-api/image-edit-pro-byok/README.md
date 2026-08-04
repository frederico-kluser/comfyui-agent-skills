# image-edit-pro-byok — os melhores editores de foto por API, com o modelo em dropdown

> Os **mesmos 6 processos** do `../image-edit-nano-banana-2/`, mas rodando nos **quatro
> melhores motores de edição de 2026** — trocáveis num dropdown — **sem login comfy.org**,
> só com a sua `FAL_KEY`. Mais um sétimo workflow que existe para responder a pergunta
> central: **qual deles acerta o seu rosto.**

|  |  |
|---|---|
| 🎯 Faz | Edita foto por instrução + referências: roupa, objeto, pessoa, cenário, e insere você na cena |
| 🧠 Técnica | Edição multi-referência com **modelo selecionável**: Seedream 5.0 Pro · FLUX.2 Pro · Nano Banana Pro · GPT Image 2 |
| 💳 Custo/billing | **fal.ai**, por imagem. **Zero crédito comfy.org** |
| 🔌 Rota | **BYOK puro** — `Authorization: Key $FAL_KEY` |
| 📥 Entrada | A foto BASE + 1–5 referências (**2 ângulos do rosto** nos processos de pessoa) |
| 📤 Saída | **PNG em 2K** em `output/edit/` — sem passe de degradação |
| 🧱 Requer | `FAL_KEY` com saldo. Os nós vêm **dentro deste bundle** |
| 🟡 Status | Schemas dos 4 endpoints extraídos do OpenAPI ao vivo; grafos conferidos contra o schema dos nós. **Nada foi executado** — nenhuma geração, nenhum crédito gasto |

📇 **Card de API:** [`API_REFERENCE_image-edit-pro-byok.md`](API_REFERENCE_image-edit-pro-byok.md)

---

## Por que as fotos anteriores erravam o seu rosto

Diagnóstico do `../image-edit-nano-banana-2/`. Quatro causas, em ordem de impacto — e as
três primeiras **não eram culpa do modelo**:

### 1. A saída estava em `1K` — esta é a causa maior

O bundle antigo fixava `resolution = 1K` de propósito, para gastar menos crédito e ajudar no
"look de celular". O problema: se você aparece **de corpo inteiro** num quadro de 1K, o seu
rosto ocupa algo como **120×120 pixels**. Não existe modelo no mundo que segure identidade
nesse orçamento de pixel — ele *precisa* inventar.

**Aqui o padrão é `2K`,** e o Nano Banana Pro chega a `4K`.

### 2. A cadeia de "realismo de celular" rodava depois da edição

Grão de filme, aberração cromática, redução de nitidez, JPEG. Essa cadeia é excelente para
disfarçar cara de render — e **péssima para o rosto**, porque destrói exatamente a
microtextura de pele que faz você parecer você.

**Ela não está neste bundle.** Se você quiser o look de celular, rode
[`../foto-realismo-celular/`](../foto-realismo-celular/) **depois**, como passe separado, e
compare com o PNG limpo antes de decidir.

### 3. O prompt pedia coisas demais numa tacada

Identidade + exposição + reiluminação + estética de celular, tudo junto. Quanto mais eixos
você manda mudar de uma vez, mais o modelo reinterpreta o rosto — é o mecanismo mais bem
documentado de *identity drift*.

Os prompts daqui são **focados na identidade** e dizem explicitamente ao modelo **para não
re-renderizar o rosto** quando o processo não exige.

### 4. O prompt mandava te subexpor

Havia uma cláusula pedindo *"let the subject fall darker and slightly flat"* e permitindo
estouro de janela com halação sobre você. Rosto escuro e chapado = menos informação de rosto.
**Removida.**

> **O que sobra de responsabilidade do modelo:** o Gemini (Nano Banana **2** = Gemini 3.1
> *Flash*) é o tier rápido. O tier de qualidade é o **Nano Banana Pro** (Gemini 3 *Pro*), que
> tem trava de referência de rosto — e está aqui no dropdown. Mas como o seu relato é
> justamente de erro com o Google, o **padrão do bundle é o Seedream 5.0 Pro**.

---

## Não existe "o melhor do mundo" — existe o melhor para o **seu** rosto

Isso não é evasiva: identidade é idiossincrática. Um motor pode acertar você e errar outra
pessoa, porque o que ele "entende" do seu rosto depende de quanto rostos parecidos com o seu
apareceram no treino.

Por isso o bundle começa com **`00_teste-de-identidade`**: a mesma foto base e as mesmas
referências entram nos três motores principais, com o mesmo prompt, e você compara.
São três chamadas — o gasto mais barato que existe para parar de errar em todas as edições
seguintes.

### Os quatro motores e quando escolher cada um

| Modelo | Endpoint | Por que escolher | Refs | Seed |
|---|---|---|---|---|
| **Seedream 5.0 Pro** *(padrão)* | `bytedance/seedream/v5/pro/edit` | **10 imagens de referência** — mais âncoras de identidade que qualquer outro. Saída já em 2K | 10 | ❌ |
| **FLUX.2 Pro** | `fal-ai/flux-2-pro/edit` | Melhor pele e anatomia humana nos comparativos de 2026 | 10 | ✅ |
| **Nano Banana Pro** | `fal-ai/nano-banana-pro/edit` | Gemini 3 **Pro** (o tier de cima), único que vai a **4K**, aceita `system_prompt` | 14 | ✅ |
| **GPT Image 2** | `openai/gpt-image-2/edit` | Até **16 referências** e o **único que aceita máscara** | 16 | ❌ |
| Seedream 5.0 Lite | `bytedance/seedream/v5/lite/edit` | Rascunho barato | 10 | ❌ |

---

## Quem paga: o seletor `rota`

O nó tem um widget **`rota`** com duas opções:

| Rota | Credencial | O que dá acesso |
|---|---|---|
| **`Minha chave (fal.ai)`** *(padrão)* | `FAL_KEY` | Os **5 motores** do dropdown |
| **`Créditos comfy.org (login)`** | **login em `platform.comfy.org`** — o saldo que você já pagou | **Só o Seedream** (`seedream-5-0-260128`, o "5.0 lite" do partner) |

Escolhendo a rota comfy.org, o nó **ignora o dropdown `model`** (avisa no console) e chama o
Seedream partner com o seu crédito. Sem `FAL_KEY`, sem cobrança na fal.

### Por que só o Seedream

Só existe nó partner no comfy.org para uma parte dos motores, e replicar cada payload sem
poder testar seria arriscado. O que dá para usar hoje com o seu crédito:

| Motor deste bundle | Crédito comfy.org? | Como |
|---|---|---|
| **Seedream** | ✅ | `rota = Créditos comfy.org` neste nó |
| **Nano Banana Pro** | ⚠️ existe partner (`GeminiImage2Node`, "Nano Banana Pro"), **não ligado aqui** | Use o nó nativo direto no ComfyUI |
| **FLUX.2 Pro** | ⚠️ existe partner (`Flux2ProImageNode`), **não ligado aqui** | Use o nó nativo direto |
| **GPT Image 2** | ⚠️ existe proxy OpenAI, **não ligado aqui** | Use o nó nativo direto |
| **Restaurar rosto (CodeFormer)** | ❌ sem partner | Só `FAL_KEY` |

Os bundles `../image-edit-nano-banana-2/` e `../image-edit-seedream/` já rodam 100% em
crédito comfy.org — mas com as configurações antigas (1K + passe de degradação). Se for
usá-los, **suba o `resolution` para 2K** e pule o passe de realismo quando o rosto importar.

> 🔎 **Como funciona por dentro** (verificado no código do ComfyUI instalado, não inferido):
> o nó declara `hidden: {auth_token: AUTH_TOKEN_COMFY_ORG}`; o `execution.py` injeta o token
> da sua sessão; o nó sobe as imagens em `POST /customers/storage` e chama
> `POST /proxy/byteplus/api/v3/images/generations` em `https://api.comfy.org` com
> `Authorization: Bearer <token>`. É exatamente o caminho dos nós partner nativos.

> 🟡 **Status:** a rota comfy.org foi construída a partir do código-fonte instalado, mas
> **não foi executada** (gastaria o seu crédito). Se falhar no primeiro uso, a mensagem de
> erro traz o código HTTP e o significado — 401/403 login, 402 sem saldo, 400 payload.

---

## Instalação

```bash
bash setup.sh
```

Instala os nós (**symlink**, nada é copiado), confere o `fal_client` e a `FAL_KEY`, e deixa os
`.json` no painel. Depois **reinicie o ComfyUI**.

### A chave

```bash
printf 'FAL_KEY=%s\n' "SUA_CHAVE" >> ~/ComfyUI/secrets.env
chmod 600 ~/ComfyUI/secrets.env
```

Pegue em <https://fal.ai/dashboard/keys> (aparece **uma vez só**) e adicione crédito em
<https://fal.ai/dashboard/billing>. É a **mesma chave** do `../video-seedance25-byok/` — se
você já configurou lá, não precisa fazer nada.

---

## Como usar — a ordem importa

1. **Abra `..._00_teste-de-identidade.json`.**
2. Rode o nó **Testar a chave** (custo zero).
3. Suba: a **foto BASE** + **duas fotos suas** de ângulos diferentes.
4. **Run.** Saem três arquivos em `output/edit/`, um por motor.
5. Compare **só o rosto**: distância entre os olhos, nariz, linha do maxilar, formato da
   orelha. Ignore roupa e fundo nesta comparação.
6. Adote o vencedor no dropdown `model` dos outros seis workflows.

### Os 6 processos

| # | Arquivo | BASE (Image 1) | REF 1 (Image 2) | REF 2 (Image 3) |
|---|---|---|---|---|
| 1 | `trocar-roupa` | a pessoa | a peça (opcional) | — |
| 2 | `trocar-objetos-em-cena` | a cena | o objeto (opcional) | — |
| 3 | `trocar-a-pessoa-da-foto` | a cena | rosto 1 | rosto 2 |
| 4 | `me-colocar-na-foto-roupa-da-cena` | a cena | meu rosto 1 | meu rosto 2 |
| 5 | `me-colocar-na-foto-minha-roupa` | a cena | eu de corpo inteiro | meu rosto (close) |
| 6 | `trocar-o-local` | a pessoa | o novo local | — |
| **7** | **`07_refinar-rosto`** | a imagem já editada | — | — |

> O **7** é o **passe final** — rode depois de qualquer um dos outros. Ver a seção
> "O passe final que faltava" abaixo.

> O processo **2** já vem no **GPT Image 2** de propósito: é o único que aceita **máscara**,
> e marcar o objeto é muito mais confiável que descrevê-lo numa cena cheia.

---

## As referências: é aqui que se ganha ou se perde

Nenhum prompt conserta uma referência ruim. Em ordem de importância:

1. **O rosto deve ocupar 35–60% do quadro da referência.** Usar uma foto de corpo inteiro
   como referência de rosto é o erro mais caro que existe — **recorte no rosto antes de subir**.
2. **Dois ângulos** (frontal + 3/4). Três é melhor que dois. O modelo monta a cabeça em 3D em
   vez de copiar um retrato chapado.
3. **Nitidez.** Referência borrada obriga o modelo a inventar — e ele inventa um rosto bonito
   genérico, não o seu.
4. **Luz uniforme, expressão neutra, sem óculos escuros, sem cabelo cobrindo o rosto.**
5. **Parta do arquivo original.** Um JPEG já salvo cinco vezes chega ao modelo sem a
   microtextura que ele precisaria ler.

---

## O passe final que faltava: restaurar o rosto

A literatura de face swap de 2026 converge num ponto que o bundle original **não aplicava**:
um **passe de restauração depois da geração** (CodeFormer/GFPGAN) responde por boa parte do
ganho de qualidade final. Ele limpa artefato de difusão e devolve microtextura de pele —
poros, micro-sombras, o granulado que separa foto de render.

Está no workflow **`07_refinar-rosto`** e no nó **`Pro Image Edit BYOK · Restaurar rosto`**
(`fal-ai/codeformer`), que você pode encadear dentro de qualquer outro grafo:

```
Pro Image Edit BYOK ──images──> Restaurar rosto ──image──> SaveImage
```

### O único botão que importa: `fidelity`

| Valor | O que acontece |
|---|---|
| **0.7 – 0.9** *(padrão 0.8)* | **Fiel ao rosto que entrou.** Restaura textura sem mexer nos traços |
| 0.5 (default do modelo) | Meio-termo; já começa a "corrigir" o rosto |
| 0.0 – 0.3 | Prioriza "beleza": alisa, regulariza e **troca traços** — o erro que estamos evitando |

O nó **avisa no console** se você descer abaixo de 0.5. Ligue `only_center_face` quando
houver outras pessoas no quadro que você não quer alterar.

> ⚠️ Este passe conserta **acabamento**, não **identidade**. Se o modelo te deu outro nariz,
> restaurar entrega o nariz errado com textura melhor. Traço errado se resolve na edição.

### A sequência completa recomendada

```
00_teste-de-identidade      (uma vez — escolhe o motor para o seu rosto)
      ↓
processo 1 a 6              em 2K, num_images = 3
      ↓
07_refinar-rosto            fidelity 0.8
      ↓
../foto-realismo-celular/   (opcional — só se quiser o look de celular)
```

---

## A técnica mais forte que este bundle **não** implementa: LoRA de identidade

Vale saber que ela existe, porque é o teto da qualidade de identidade hoje.

Em vez de mandar 2–3 fotos de referência a cada chamada, você **treina um LoRA** com 10–20
fotos suas. O modelo passa a "conhecer" o seu rosto em vez de inferi-lo a cada geração — e a
semelhança fica em outro patamar, especialmente para rostos com geometria distintiva (que é
justamente onde os modelos de referência regridem para proporções médias).

Endpoints prontos na fal, com a mesma `FAL_KEY`:

| Etapa | Endpoint | Nota |
|---|---|---|
| Treinar | `fal-ai/flux-lora-portrait-trainer` | Entrada: **zip** com ≥10 fotos (`images_data_url`). `steps` 2500 (default), `trigger_phrase` opcional. Saída: `diffusers_lora_file` |
| Alternativas | `fal-ai/krea-2-trainer` · `fal-ai/qwen-image-2512-trainer` | Outros ecossistemas |
| Usar | Endpoints FLUX que aceitam `loras: [{path, scale}]` | O `path` é a URL devolvida pelo treino |

**Por que não está construído aqui:** é um fluxo de forma diferente — treina uma vez (leva
minutos e custa mais que uma geração), e a inferência exige um endpoint que carregue LoRA,
que não é o mesmo conjunto de motores do dropdown. Preferi entregar o bundle de edição
completo e verificado a meias-construir uma segunda arquitetura que eu não poderia validar.

**Quando vale o investimento:** se você vai gerar dezenas de imagens suas ao longo do tempo.
Para uso pontual, `2K` + 3 referências boas + `num_images = 3` + o passe de restauração
resolve a maioria dos casos.

---

## Os três ajustes que mais salvam uma geração ruim

1. **`num_images = 3`.** Gera três variações na **mesma** chamada e você escolhe o melhor
   rosto. É a forma mais barata de vencer a loteria da identidade — mais eficaz que
   reescrever o prompt.
2. **`resolucao = 2K`** (ou `4K` no Nano Banana Pro). Rosto precisa de pixel.
3. **Trocar o motor.** É literalmente para isso que o dropdown existe.

Se depois dos três o rosto continuar errado, o problema é a **referência**, não o modelo —
volte para a seção acima.

---

## Troubleshooting

| Sintoma | Causa provável | Correção |
|---|---|---|
| Nós não aparecem após o `setup.sh` | Servidor não reiniciado | `bash ~/ComfyUI/run.sh` |
| `FAL_KEY nao encontrada` | Chave não gravada, ou servidor subiu antes | Grave no `secrets.env` e reinicie |
| HTTP 401 | Chave inválida ou sem saldo | <https://fal.ai/dashboard/billing> |
| **O rosto não é o meu** | Referência com rosto pequeno, ou 1K | Recorte no rosto · `2K` · `num_images = 3` · troque o motor |
| **Ele me "embelezou"** | Viés do modelo (afinar, alisar, rejuvenescer) | O prompt já proíbe; repita a proibição no fim. Troque o motor |
| Rosto mudou num processo que não era de rosto | O motor re-renderizou a pessoa inteira | Os prompts dizem *"do not re-render the face"* — reforce, ou troque o motor |
| Pessoa parece colada na cena | Luz, não recorte | Descreva direção/temperatura/dureza da luz e exija sombra de contato |
| Roupa parece adesivo | Faltou dobra e sombra da peça | Peça explicitamente as dobras e a sombra sobre o corpo |
| Máscara ignorada | Só o GPT Image 2 aceita | Troque o `model` para GPT Image 2 (o console avisa) |
| `4K` não fez efeito | Só o Nano Banana Pro tem 4K | O console avisa e usa o teto do motor escolhido |
| Fica minutos "parado" | Cold start / fila da fal | Normal — o console mostra a posição. **O Cancel funciona** |
| Saiu só 1 imagem com `num_images = 3` | O modelo devolveu tamanhos diferentes | O nó avisa e devolve a primeira; baixe as outras pelas URLs |

---

## ⚖️ Uso responsável

Use apenas o rosto de quem autorizou — inclusive o seu. Colocar a imagem de outra pessoa numa
cena sem consentimento pode violar direito de imagem e os termos dos provedores. Todos os
motores têm moderação ativa; recusas acontecem.

Não li os termos da fal.ai nem dos provedores durante a construção deste bundle — leia
<https://fal.ai/terms> antes de uso comercial.

---

## Como este bundle se compara aos irmãos

| Bundle | Chave | Modelo | Diferença |
|---|---|---|---|
| **`image-edit-pro-byok`** (este) | **`FAL_KEY`** | 4 motores em dropdown | **2K/4K**, sem degradação, comparação de identidade |
| `../image-edit-nano-banana-2/` | Login comfy.org | Gemini 3.1 Flash, fixo | 1K + passe de realismo de celular |
| `../image-edit-seedream/` | Login comfy.org | Seedream 5.0 lite, fixo | idem |
| `../foto-realismo-celular/` | — (CPU local) | — | O passe de "look de celular", agora **opcional e separado** |

Os antigos continuam úteis quando você quer pagar com crédito comfy.org em vez de chave.
Para **qualidade de rosto**, use este.

---

## Referências

- Card de API: [`API_REFERENCE_image-edit-pro-byok.md`](API_REFERENCE_image-edit-pro-byok.md)
- Schemas ao vivo (reconferir antes de mudanças):
  `curl -s "https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=bytedance/seedream/v5/pro/edit"`
- Nós de API online (catálogo geral): `.agents/skills/knowledge-comfyui-api-nodes`
- Passe de realismo opcional: `../foto-realismo-celular/`
