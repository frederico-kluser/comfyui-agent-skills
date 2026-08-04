# video-seedance25-byok — me colocar num vídeo, por chave de API direta

> Sete workflows para pôr **você** (ou outra pessoa) dentro de um vídeo, combinando **foto**,
> **vídeo de referência** e **foto ou vídeo do lugar**. Roda **sem GPU** e **sem login/crédito
> do comfy.org**: a única credencial é a sua **`FAL_KEY`**.

|  |  |
|---|---|
| 🎯 Faz | Gera um vídeo com você dentro dele, a partir de referências suas e do cenário |
| 🧠 Técnica | Seedance 2.x **reference-to-video** (multi-referência) + Wan 2.2 Animate para o caso de editar o plano original |
| 💳 Custo/billing | **fal.ai**, por token de vídeo. ~US$ 0,30/s a 720p no Seedance 2.0. **Zero crédito comfy.org** |
| 🔌 Rota | **BYOK puro** — `Authorization: Key $FAL_KEY` direto na fal, sem intermediário |
| 📥 Entrada | Sua foto · seu vídeo · foto ou vídeo do lugar (nas combinações de cada workflow) |
| 📤 Saída | `VIDEO` nativo com áudio em `output/video/` |
| 🧩 Modelos | Seedance 2.0 / 2.0 Fast / 2.0 Mini · **Seedance 2.5** (pré-cabeado) · Wan 2.2 Animate 14B |
| 🧱 Requer | `FAL_KEY` + `fal_client` (já vem com o `ComfyUI-fal-API`). Os nós vêm **dentro deste bundle** |
| 🟡 Status | Nós validados por carga real e grafos conferidos contra o schema dos nós. **Ainda não executados contra a API** — valide com o nó *Testar a chave* antes de gastar |

📇 **Card de API:** [`API_REFERENCE_video-seedance25-byok.md`](API_REFERENCE_video-seedance25-byok.md)

---

## Sobre o Seedance 2.5 — leia antes de se frustrar

O **Seedance 2.5 existe**: a ByteDance anunciou em **2026-07-31** (30 s de áudio+vídeo numa
passada só, até 30 imagens + 10 vídeos + 10 áudios de referência). Mas em **2026-08-04**:

- **BytePlus ModelArk** já publica o ID `dreamina-seedance-2-5-260628` e a tabela de preço,
  e a página da API diz literalmente *"API access will be available soon"*.
- **Replicate** não tem 2.5.
- **fal.ai** tem os endpoints `bytedance/seedance-2.5/*` **roteáveis** (devolvem OpenAPI 200,
  enquanto um `seedance-3.0` de controle devolve 404) — mas **fora do catálogo público**, e
  o schema publicado é um **molde do 2.0**: ainda 15 s no máximo, **não os 30 s anunciados**.

**O que isso significa na prática:** hoje o 2.5 não oferece nenhuma vantagem funcional sobre
o 2.0. Por isso os workflows vêm em **Seedance 2.0**, com a opção `Seedance 2.5` já no widget
`model`. Quando a fal liberar, você troca a opção do combo e pronto — nada mais muda.

O nó **Testar a chave** consulta os endpoints ao vivo e diz quais estão roteáveis agora.

---

## Escolha o workflow pela combinação que você tem

| # | Arquivo | Você entrega | O que sai |
|---|---|---|---|
| 1 | `eu-foto__lugar-foto` | 📷 sua foto + 📷 foto do lugar | Você naquele lugar, cena nova |
| 2 | `eu-foto__performance-video` | 📷 sua foto + 🎬 vídeo de performance | Você fazendo aquele movimento |
| 3 | `eu-foto__lugar-video` | 📷 sua foto + 🎬 vídeo do lugar | Você dentro daquele plano/movimento de câmera |
| 4 | `eu-video__lugar-video` | 🎬 seu vídeo + 🎬 vídeo do lugar | Você, do seu jeito de se mover, no outro lugar |
| 5 | **`combo-completo`** | 📷 sua foto + 🎬 seu vídeo + 📷 foto do lugar | **O mais convincente** — rosto, jeito de andar e cenário |
| 6 | `cena-longa-encadeada` | 📷 sua foto + 📷 foto do lugar | Cena **acima de 15 s**, encadeando clipes |
| 7 | **`trocar-pessoa-mantendo-o-plano`** | 📷 sua foto + 🎬 **o seu vídeo** | **Edita o seu vídeo**: troca quem aparece e mantém tudo o resto |
| **8** | **`upscale-passe-final`** | 🎬 a saída de qualquer um acima | **Passe final** — mais pixel de rosto pelo mesmo dinheiro |

### A distinção que decide tudo: recriar × editar

Os workflows **1 a 6 usam Seedance**, que **recria a cena**. As suas referências guiam, mas o
enquadramento, os cortes e o fundo do material de referência **não são preservados** — o
resultado é uma tomada nova.

O workflow **7 usa Wan 2.2 Animate**, que **edita o vídeo original**: mantém movimento,
enquadramento, cortes, fundo e os outros atores, e troca só a pessoa.

> **Regra prática:** quer *inventar* uma cena → Seedance. Quer *consertar/trocar* uma cena que
> você já gravou → Wan Animate.

---

## Quem paga: o seletor `rota`

O nó `Seedance BYOK · Reference to Video` tem um widget **`rota`**:

| Rota | Credencial | O que dá acesso |
|---|---|---|
| **`Minha chave (fal.ai)`** *(padrão)* | `FAL_KEY` | Seedance 2.5 / 2.0 / Fast / Mini, todas as resoluções |
| **`Créditos comfy.org (login)`** | **login em `platform.comfy.org`** — o saldo que você já pagou | **Seedance 2.0** e **2.0 Fast** |

Na rota comfy.org o nó sobe os arquivos para o storage do comfy.org e chama o Seedance
partner com o seu crédito — sem `FAL_KEY`, sem cobrança na fal.

**Duas coisas que o nó resolve sozinho ao trocar de rota:**

1. **Traduz os rótulos do prompt.** A fal usa `@Image1`; o partner usa `Image 1`. Sem
   tradução a referência seria silenciosamente ignorada. O nó converte e avisa no console.
2. **Recusa o que não existe na rota.** Escolheu `Seedance 2.5` ou `Mini` com a rota
   comfy.org? Erro claro dizendo que só há 2.0 e 2.0 Fast ali.

### ⚠️ A limitação que decide o seu caso de uso

O Seedance partner **recusa foto ou vídeo de pessoa real** nas entradas normais de
referência. Como o objetivo deste bundle é justamente colocar **você** no vídeo, na rota
comfy.org isso exige o **fluxo de asset verificado** (verificação facial por link H5), que
está implementado no bundle [`../video-person-swap-seedance-2/`](../video-person-swap-seedance-2/).

**Na prática:**
- **Pessoa real + crédito comfy.org** → use `../video-person-swap-seedance-2/`.
- **Pessoa real + sem verificação facial** → use a rota `Minha chave (fal.ai)` daqui.
- **Cena sem pessoa real** (produto, animação, personagem sintético) → a rota comfy.org
  daqui funciona direto.

### O resto do bundle

| Recurso | Crédito comfy.org? |
|---|---|
| **Seedance reference-to-video** | ✅ pelo seletor `rota` |
| Seedance image-to-video (cena longa) | ❌ só `FAL_KEY` neste bundle |
| **Wan Animate** (trocar pessoa mantendo o plano) | ❌ sem partner equivalente |
| **Upscale** | ⚠️ existe partner Topaz no core, **não ligado aqui** (fluxo de upload em 4 etapas) |

> 🔎 **Por dentro** (lido do ComfyUI instalado): `hidden: {auth_token: AUTH_TOKEN_COMFY_ORG}`
> → `execution.py` injeta o token → upload em `POST /customers/storage` → criação em
> `POST /proxy/byteplus/api/v3/contents/generations/tasks` → polling em
> `GET /proxy/byteplus-seedance2/api/v3/contents/generations/tasks/{id}`.
> Repare a assimetria dos dois caminhos — criar é no `byteplus`, status no `byteplus-seedance2`.

> 🟡 **Status:** rota construída a partir do código-fonte instalado, **não executada**
> (gastaria crédito). Erros trazem código HTTP e significado.

---

## Instalação (uma vez)

```bash
bash setup.sh
```

O script instala os nós do bundle (**symlink** — nada é copiado), confere o `fal_client`,
confere a `FAL_KEY` sem imprimi-la e deixa os `.json` visíveis no painel Workflows.
Depois **reinicie o ComfyUI**.

### A chave

```bash
printf 'FAL_KEY=%s\n' "SUA_CHAVE" >> ~/ComfyUI/secrets.env
chmod 600 ~/ComfyUI/secrets.env
```

Pegue em <https://fal.ai/dashboard/keys> — **o valor aparece uma vez só**. Adicione crédito em
<https://fal.ai/dashboard/billing>. O `run.sh` do ComfyUI já dá `source` no `secrets.env`.

> Os nós também leem a chave direto do `~/ComfyUI/secrets.env` caso o servidor tenha subido
> sem a env var — mas o caminho normal é reiniciar depois de gravar.

---

## Como usar

1. Abra um dos `.json` no painel **Workflows** e leia o nó **⚠️ Leia antes de rodar**.
2. Rode o nó **Testar a chave** (custo zero). Ele confirma que a `FAL_KEY` carregou e mostra
   quais modelos estão roteáveis.
3. Suba os seus arquivos nos `LoadImage` / `LoadVideo`.
4. Ajuste o prompt — ele já vem completo e comentado.
5. **Run**. O vídeo sai em `output/video/`.

### Rascunhe barato, finalize caro

Primeira passada: `model = Seedance 2.0 Mini`, `resolution = 480p`, `duration = 4`.
Confirmou enquadramento e identidade? Aí `Seedance 2.0` + `1080p` + duração cheia.
No workflow 7: `480p` + trecho de 3–6 s antes de qualquer coisa.

---

## O que faz a diferença no resultado

### 1. Cite as referências no prompt — senão elas são ignoradas

O modelo enxerga as referências por **rótulo posicional**, na ordem em que os slots estão
ligados:

| Slot | Vira no prompt |
|---|---|
| `image_1` | `@Image1` |
| `image_2` | `@Image2` |
| `video_1` | `@Video1` |
| `audio_1` | `@Audio1` |

**Mudou as ligações? Renumere o prompt.** O nó imprime um aviso no console quando você liga
uma referência que o prompt nunca cita.

> ⚠️ Prompt copiado do bundle `../video-person-swap-seedance-2/` **não funciona aqui sem
> traduzir**: lá a sintaxe é `Image 1` (partner), aqui é `@Image1` (fal), e na Replicate
> seria `[Image1]`. Mesmo modelo, três sintaxes.

### 2. Foto **e** vídeo da mesma pessoa é melhor que qualquer um sozinho

A **foto** ancora o rosto com uma nitidez que vídeo comprimido não dá. O **vídeo** ensina o
jeito de andar, o ritmo e os gestos. É por isso que o workflow 5 (`combo-completo`) é o mais
convincente — e é exatamente a combinação foto + vídeo seu + lugar.

### 3. Foto de **corpo inteiro**

Referência só de rosto produz proporção de corpo errada. Frontal, nítida, luz neutra,
**uma pessoa só** no quadro.

### 4. Descreva a luz

O Seedance recria o plano do zero. Quanto mais explícito o prompt sobre **luz, lente, timing e
mecânica do movimento**, menos ele inventa. Os prompts do bundle já trazem blocos
`IDENTITY` / `MOTION` / `WARDROBE` / `LIGHTING` / `CAMERA` / `REALISM` — edite, não apague.

---

## Limites e custo

### Limites de referência (o nó valida antes de gastar)

| Tipo | Máximo |
|---|---|
| Imagens | 9 · ≤30 MB cada · lado entre 300 e 6000 px |
| Vídeos | 3 · **somados entre 2 e 15 s** · total <50 MB · cada um entre ~480p e ~720p |
| Áudios | 3 · somados ≤15 s · ≤15 MB cada · exige ≥1 imagem ou vídeo |
| **Total** | **12 arquivos** somando tudo |
| Duração da saída | **4 a 15 s** por chamada |

### A armadilha de custo

A cobrança é por token sobre `(duração do vídeo de ENTRADA + duração da SAÍDA)`.

**"Vídeo de referência é mais barato" é falso.** A *taxa* por segundo cai (US$ 0,18/s em vez
de US$ 0,30/s a 720p), mas a base cresce: uma saída de **5 s** guiada por um vídeo de **10 s**
bilha como **15 s** ≈ **US$ 2,72** — cerca de US$ 0,54 por segundo de saída, quase o dobro.

**Corte o vídeo de referência ao mínimo que ainda ensina o movimento.** O workflow 4
(dois vídeos) é o mais caro do bundle.

---

## O passe final: upscale (gere barato, amplie depois)

Identidade mora em **pixel de rosto**. Num plano aberto a 480p o seu rosto tem uns 60×60 px —
é por isso que ele escorrega no meio do clipe.

A jogada certa não é gerar direto em alta: é **gerar barato e ampliar depois**. O modelo de
vídeo é o componente caro; o upscale é cobrado à parte e sai bem mais barato por segundo. E
um upscale por difusão **reconstrói** detalhe de rosto em vez de só esticar pixel.

Workflow **`upscale-passe-final`**, nó **`Video BYOK · Upscale`**, dois motores:

| Motor | Quando escolher |
|---|---|
| **SeedVR** *(padrão)* — `fal-ai/seedvr/upscale/video` | Difusão; **reconstrói** detalhe. Costuma ser melhor em **rosto** |
| **Topaz** — `fal-ai/topaz/upscale/video` | Controle fino (denoise, compressão, grão) e **interpolação de fps** |

**Fluxo recomendado:** rascunhe em 480p/4 s → gere a versão boa em 720p → **amplie 2×**.

⚠️ **Amplie por último.** Ampliar antes de outra etapa de geração só faz o modelo seguinte
pagar mais caro para processar pixel que ele vai refazer. A ordem é:

```
gerar (barato) → [Wan Animate, se for editar o plano] → upscale → áudio
```

> Este passe conserta **definição**, não **semelhança**. Se o modelo te deu outro rosto,
> ampliar entrega o rosto errado em alta resolução.

---

## Passando dos 15 segundos

O Seedance gera no máximo 15 s por chamada. O workflow 6 mostra a técnica canônica:

```
Reference-to-video → CLIPE 1 → Último Frame → Image-to-Video → CLIPE 2 → …
```

Repita o par *Último Frame + Image to Video* quantas vezes quiser. Três regras:

1. **Diga no prompt que é continuação** — "continue the shot from this exact frame", "same
   person, same clothing, same location, same lighting". Sem isso ele troca a cena.
2. **Último frame borrado?** Suba o `offset_from_end` para 1–3.
3. **Mesma resolução e mesmo aspect ratio** em todos os elos.

Para cena longa, use `generate_audio = false` em todos os clipes: cada chamada geraria uma
trilha independente e a emenda soaria cortada. Monte o áudio na edição.

```bash
cd ~/ComfyUI/output/video
printf "file '%s'\n" cena-longa_clipe1*.mp4 cena-longa_clipe2*.mp4 > lista.txt
ffmpeg -f concat -safe 0 -i lista.txt -c copy cena-longa.mp4
```

---

## Troubleshooting

| Sintoma | Causa provável | Correção |
|---|---|---|
| Nós não aparecem depois do `setup.sh` | Servidor não reiniciado | `bash ~/ComfyUI/run.sh` |
| `FAL_KEY nao encontrada` | Chave não gravada, ou servidor subiu antes | Grave no `secrets.env` e reinicie |
| HTTP 401 | Chave inválida ou sem crédito | Confira em <https://fal.ai/dashboard/billing> |
| Fica minutos "parado" | Cold start / fila da fal | Normal. O console mostra a posição na fila. **O Cancel do ComfyUI funciona** neste bundle |
| Referência ignorada | Prompt não cita `@Image1`/`@Video1` | Cite na ordem dos slots (o console avisa) |
| `Maximo 3 videos…` / `12 arquivos` | Passou do limite do modelo | Reduza as referências |
| `'Seedance 2.0 Fast' nao aceita 1080p` | Fast e Mini só vão a 720p | Troque o modelo ou a resolução |
| Rosto muda ao longo do clipe | Clipe longo / foto fraca | 4–6 s e foto frontal nítida |
| Proporção de corpo errada | Referência só de rosto | Foto de **corpo inteiro** |
| Trocou a pessoa errada | Prompt ambíguo | Diga a posição: *"the person on the left, in the dark jacket"* |
| Cenário mudou sem eu pedir | É o Seedance recriando a cena | Descreva o lugar no prompt, ou use o workflow **7** |
| Áudio sumiu no workflow 7 | O endpoint Wan não devolve áudio | Remuxe: `ffmpeg -i saida.mp4 -i original.mp4 -c:v copy -map 0:v:0 -map 1:a:0 -shortest final.mp4` |
| Vídeo borrado no workflow 7 | `guidance_scale > 1.0` num modelo destilado | Volte para **1.0** |
| Erro de moderação / geração recusada | Política do provedor sobre rosto real | Ver abaixo |

Mais casos: `.agents/skills/task-debug-generation`.

---

## ⚖️ Uso responsável — leia antes de usar o rosto de alguém

**Use apenas o rosto de quem autorizou** — inclusive o seu. Colocar a imagem de outra pessoa
num vídeo sem consentimento pode violar direito de imagem e leis de *likeness*, além dos
termos dos provedores.

Dois fatos concretos que valem citar:

- A **BytePlus ModelArk** (a API de origem do Seedance) **proíbe explicitamente** subir
  imagem ou vídeo de referência com rosto de pessoa real, e exige um fluxo de **QR code no
  console + verificação facial + consentimento do titular** para registrar um *asset*
  autorizado. É o mesmo pedágio que o bundle `../video-person-swap-seedance-2/` enfrenta com
  a verificação H5 do comfy.org.
- A **fal.ai** e a **Replicate** **não expõem** nenhum campo de verificação de identidade —
  só um `end_user_id` opcional. **Ausência de campo não é permissão.** A fal se declara um
  *proxy* para a ByteDance, então a política de origem pode ser aplicada na inferência mesmo
  sem aviso no schema. Se uma geração for recusada por moderação, é isso.

Não foi possível ler os termos de uso da fal durante a pesquisa (as páginas devolvem HTTP 429
de forma persistente). **Leia <https://fal.ai/terms> e a política de uso aceitável você mesmo**
antes de uso comercial.

Marque como sintético o que for publicado. Regras de rotulagem de conteúdo gerado por IA
existem em várias jurisdições e estão mudando rápido.

---

## Como este bundle se compara aos irmãos

| Bundle | Rota | Modelo | Faz |
|---|---|---|---|
| **`video-seedance25-byok`** (este) | **`FAL_KEY`** | Seedance 2.x + Wan Animate | 7 combinações de foto/vídeo/lugar. Sem login |
| `../video-person-swap-seedance-2/` | Login comfy.org | Seedance 2.0 partner | Troca de pessoa com **asset verificado** (verificação facial H5) |
| `../video-person-replace/` | `FAL_KEY` | Wan 2.2 Animate + Pixverse | Edita o vídeo original (mesmo caso do workflow 7 daqui) |

Este bundle é o único que roda **sem nenhuma conta comfy.org** e o único que já vem
pré-cabeado para o Seedance 2.5.

---

## Referências

- Card de API deste bundle: [`API_REFERENCE_video-seedance25-byok.md`](API_REFERENCE_video-seedance25-byok.md)
- Nós de API online (catálogo geral): `.agents/skills/knowledge-comfyui-api-nodes`
- Anúncio oficial do Seedance 2.5:
  <https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5>
- Schema ao vivo (reconferir antes de mudanças):
  `curl -s "https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=bytedance/seedance-2.0/reference-to-video"`
