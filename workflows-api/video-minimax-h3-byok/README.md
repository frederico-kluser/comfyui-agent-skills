# video-minimax-h3-byok — me colocar num vídeo com o MiniMax H3, 100% online

> Oito workflows para pôr **você** (ou outra pessoa) dentro de um vídeo, combinando **foto**,
> **vídeo de referência**, **foto ou vídeo do lugar** e até a **sua voz**. Roda **sem GPU** e
> **sem login/crédito do comfy.org**: a única credencial é a sua **`MINIMAX_API_KEY`**.

|  |  |
|---|---|
| 🎯 Faz | Gera um vídeo (com áudio) a partir das suas referências, pela API da MiniMax |
| 🧠 Técnica | MiniMax H3 **reference-to-video**, **image-to-video** (first/last frame) e **text-to-video** |
| 💳 Custo/billing | Conta MiniMax pré-paga. **Zero crédito comfy.org** |
| 🔌 Rota | **BYOK puro** — `Authorization: Bearer $MINIMAX_API_KEY` direto na `api.minimax.io` |
| 📥 Entrada | Sua foto · seu vídeo · foto ou vídeo do lugar · sua voz (nas combinações de cada workflow) |
| 📤 Saída | `VIDEO` nativo **com áudio gerado junto**, em `output/video/` |
| 🧩 Modelo | `MiniMax-H3` (API v2) — vídeo **e** áudio na mesma passada |
| 🧱 Requer | `MINIMAX_API_KEY` com saldo. Os nós vêm **dentro deste bundle** |
| 🟡 Status | Endpoints confirmados ao vivo (401 documentado sem chave); nós carregados e grafos conferidos contra o schema. **Ainda não executados contra a API com chave real** |

📇 **Card de API:** [`API_REFERENCE_video-minimax-h3-byok.md`](API_REFERENCE_video-minimax-h3-byok.md)

---

## ⚠️ Antes de tudo: as duas "MiniMax H3" não são a mesma coisa

Existem **dois caminhos** com o mesmo nome, e eles não se misturam:

| | **Este bundle** (API) | O tutorial do comfy.org |
|---|---|---|
| Onde o modelo roda | **Na nuvem da MiniMax** | **Na sua GPU**, local |
| O que você precisa | Uma **chave de API** e saldo | Baixar ~dezenas de GB de `.safetensors` e ter VRAM de sobra |
| Arquivos | Nenhum | `minimax_h3_fl2va_pruned_int8_convrot.safetensors`, `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`, VAEs… |
| Custo | Por geração | Grátis depois do download — se a GPU aguentar |
| Nesta máquina (8 GB) | ✅ funciona | ❌ não cabe |

O <https://docs.comfy.org/tutorials/video/minimax/minimax-h3> descreve o caminho **local
(open-weights)**. Como você pediu **tudo online**, este bundle usa o outro caminho: a
**API v2** documentada em
<https://platform.minimax.io/docs/api-reference/video-generation-v2-create>.

Uma consequência prática: no modelo local as referências são citadas como `<Picture 1>` /
`<Video 1>`. **Na API não é assim** — veja "Como citar as referências" abaixo.

---

## Como pegar a chave (5 minutos, tudo pelo navegador)

1. **Crie a conta** em <https://platform.minimax.io> → *Sign up* (e-mail ou Google).
   > Existe uma plataforma separada para a China continental, com **outro domínio e outro
   > host de API**. Este bundle aponta para a internacional (`api.minimax.io`). Para trocar,
   > exporte `MINIMAX_API_HOST` — não é preciso editar código.
2. **Abra o Console** (canto superior direito da plataforma).
3. No menu lateral, vá em **API Keys** → **Create new API key**.
   Dê um nome e **copie o valor na hora**: ele aparece **uma única vez**.
   > Na página *User Center → Basic Information* fica também o seu **Group ID**. A API v2 de
   > vídeo **não pede Group ID** — ele só é usado por endpoints mais antigos. Guarde mesmo assim.
4. **Adicione crédito** em *Billing / Recharge*. A conta é pré-paga: sem saldo, a geração
   falha com `insufficient_balance_error` (HTTP 402).
5. **Grave a chave** e reinicie o ComfyUI:

```bash
printf 'MINIMAX_API_KEY=%s\n' "SUA_CHAVE" >> ~/ComfyUI/secrets.env
chmod 600 ~/ComfyUI/secrets.env
bash ~/ComfyUI/run.sh
```

6. **Confirme** rodando o nó **Testar a chave** dentro de qualquer workflow (custo zero).
   Ele diz se a credencial foi aceita — e avisa que aceitação **não é saldo**.

> 🔐 A chave nunca vai para o repositório: fica no `secrets.env`, que é gitignored e
> carregado pelo `run.sh`. Os nós também a leem direto do arquivo caso o servidor tenha
> subido sem a variável de ambiente.

---

## Instalação

```bash
bash setup.sh
```

Instala os nós (**symlink** — nada é copiado), testa a credencial contra a API de verdade e
deixa os `.json` no painel Workflows. Depois **reinicie o ComfyUI**.

---

## Escolha o workflow pela combinação que você tem

| # | Arquivo | Você entrega | O que sai |
|---|---|---|---|
| 1 | `eu-foto__lugar-foto` | 📷 sua foto + 📷 foto do lugar | Você naquele lugar, cena nova |
| 2 | `eu-foto__performance-video` | 📷 sua foto + 🎬 vídeo de performance | Você fazendo aquele movimento |
| 3 | `eu-foto__lugar-video` | 📷 sua foto + 🎬 vídeo do lugar | Você dentro daquele plano |
| 4 | `eu-video__lugar-video` | 🎬 seu vídeo + 🎬 vídeo do lugar | Seu jeito de se mover, no outro lugar |
| 5 | **`combo-completo`** | 📷 foto + 🎬 vídeo seu + 📷 lugar | **O mais convincente** |
| 6 | **`eu-foto__minha-voz`** | 📷 sua foto + 🔊 sua voz | **Você falando, com o seu timbre** |
| 7 | `cena-longa-encadeada` | 📷 foto + 📷 lugar | Cena **acima de 15 s**, encadeada |
| 8 | `so-texto` | ✍️ só o prompt | Plano de cobertura — **o teste mais barato** |

**Comece pelo 8.** É a chamada mais barata que existe: se sair vídeo, a rota inteira
(chave → upload → fila → download) está funcionando.

### O que o H3 **não** faz

Nenhum modo dele **edita** um vídeo existente. Ele sempre **recria** a cena. Para *"pega o
meu vídeo e troca quem aparece nele, mantendo enquadramento, cortes e os outros atores"*, o
caminho é o Wan 2.2 Animate — workflow 7 de [`../video-seedance25-byok/`](../video-seedance25-byok/)
ou o bundle [`../video-person-replace/`](../video-person-replace/).

---

## Como citar as referências (a armadilha nº 1)

⚠️ **Aqui não se usa `@Image1`.** Cada rota tem a sua sintaxe, para o mesmo tipo de tarefa:

| Rota | Sintaxe no prompt |
|---|---|
| **MiniMax H3 API (este bundle)** | **linguagem natural**: *"reference image 1"*, *"reference video 1"*, *"reference audio 1"* |
| MiniMax H3 open-weights (comfy.org, local) | `<Picture 1>`, `<Video 1>` |
| Seedance na fal (`../video-seedance25-byok/`) | `@Image1`, `@Video1` |
| Seedance partner (comfy.org) | `Image 1`, `Video 1` |

A numeração segue a **ordem dos slots ligados**. Exemplo tirado da própria documentação da
MiniMax:

> *"Character speaks: Follow the wind, live free. … **Voice timbre follows reference audio 1**."*

**Mudou as ligações? Renumere o prompt.**

---

## Limites da API (o nó valida antes de gastar)

| Tipo | Máximo | Detalhe |
|---|---|---|
| Imagens de referência | **9** | ≤30 MB · lado entre **256 e 5760 px** · proporção **0,4–2,5** · JPG/PNG/WEBP/HEIC/HEIF |
| Vídeos de referência | **3** | ≤50 MB · **2–15 s cada, somados ≤15 s** · 23,976–60 fps · MP4/MOV (H.264/H.265) |
| Áudios de referência | **3** | ≤15 MB · 2–15 s cada, somados ≤15 s · WAV/MP3 · **nunca sozinho** |
| Duração da saída | **4 a 15 s** | por chamada |
| Resolução | **`768P` ou `2K`** | são os dois únicos valores |
| Prompt | **7000 caracteres** | e é **sempre obrigatório**, em todos os modos |

Três regras estruturais que valem lembrar:

1. **Todo request precisa de um item de texto não-vazio** — mesmo no image-to-video.
2. **Image-to-video e reference-to-video são mutuamente exclusivos.** Se houver qualquer
   `reference_*`, não pode haver `first_frame`/`last_frame`. Por isso são nós separados.
3. **`ratio` só existe no text-to-video**, onde é **obrigatório**. Nos outros modos o formato
   é `adaptive`, herdado das referências.

---

## Custo

A MiniMax **não publica** a tabela de preço do vídeo na página de referência da API — ela fica
atrás do link *Pricing* do console, e varia por resolução e duração. **Não vou chutar números.**

O que dá para fazer é medir: ao terminar, o nó imprime no console o campo `usage` que a
própria API devolve — `input_seconds`, `output_seconds`, `input_image_count`. Rode o
workflow **8** em `768P`/4 s uma vez, veja o que descontou do saldo e você terá o seu preço
de referência real.

**Regra de bolso:** rascunhe tudo em `768P` com `duration = 4`. Só suba para `2K` quando o
enquadramento e a identidade já estiverem certos.

---

## Passando dos 15 segundos

O workflow 7 mostra a técnica:

```
Reference-to-video → CLIPE 1 → Último Frame → Image-to-Video → CLIPE 2 → …
```

⚠️ **Por que o segundo elo muda de nó:** como `reference_*` e `first_frame` são mutuamente
exclusivos, não dá para continuar mandando as referências. O elo seguinte **tem** que ser
image-to-video, ancorado no último frame.

Três regras: diga no prompt que é continuação; suba `offset_from_end` se o último frame
estiver borrado; mantenha a mesma `resolution` em todos os elos. Cada chamada gera uma
trilha de áudio **independente** — em cena longa, monte o som na edição.

---

## Troubleshooting

| Sintoma | Causa provável | Correção |
|---|---|---|
| Nós não aparecem após o `setup.sh` | Servidor não reiniciado | `bash ~/ComfyUI/run.sh` |
| `MINIMAX_API_KEY nao encontrada` | Chave não gravada, ou servidor subiu antes | Grave no `secrets.env` e reinicie |
| HTTP 401 `authorized_error` | Chave inválida/expirada | Gere outra no Console → API Keys |
| HTTP 402 `insufficient_balance_error` | Sem saldo | Recarregue no console da MiniMax |
| HTTP 422 `unprocessable_entity_error` | Moderação bloqueou o conteúdo | Reformule o prompt / troque a referência |
| HTTP 429 `rate_limit_error` | Limite de requisições | Espere e repita |
| `A API exige sempre um item de texto` | Prompt vazio | Escreva o prompt (obrigatório em todos os modos) |
| `Imagem … fora do limite` | Lado <256 ou >5760 px | Redimensione |
| `Proporcao … fora do limite` | Fora de 0,4–2,5 | Recorte para algo próximo de 16:9 ou 9:16 |
| `Audio de referencia nao pode aparecer sozinho` | Só áudio ligado | Ligue também uma foto ou vídeo |
| Referência ignorada | Prompt não cita *"reference image 1"* | Cite na ordem dos slots |
| Fica minutos em `queued` | Fila da MiniMax | Normal — o console mostra o status. **O Cancel do ComfyUI funciona** |
| `video_url` não abre depois | A URL é temporária | Baixe no mesmo dia; ou rode de novo a consulta |
| Cena mudou sozinha | É o H3 recriando o plano | Descreva o lugar no prompt, ou use o bundle do Wan Animate |

Mais casos: `.agents/skills/task-debug-generation`.

---

## ⚖️ Uso responsável

**Use apenas rosto, corpo e voz de quem autorizou** — inclusive você mesmo. Este bundle torna
trivial gerar alguém falando algo que nunca disse; trate isso com o peso que tem.

- **Voz é dado biométrico.** O workflow 6 clona timbre a partir de uma amostra. Vale o mesmo
  critério de consentimento que vale para o rosto.
- A API tem **moderação ativa** (`unprocessable_entity_error`, HTTP 422) e os termos da
  MiniMax proíbem usos que você deve conferir antes de qualquer uso comercial:
  <https://platform.minimax.io> → Terms / Acceptable Use.
- **Marque como sintético** o que for publicado. Regras de rotulagem de conteúdo gerado por
  IA existem em várias jurisdições e estão mudando rápido.

Não li os termos da MiniMax durante a construção deste bundle — **leia você mesmo** antes de
uso comercial ou de publicar material com o rosto de terceiros.

---

## Como este bundle se compara aos irmãos

| Bundle | Chave | Modelo | Faz |
|---|---|---|---|
| **`video-minimax-h3-byok`** (este) | **`MINIMAX_API_KEY`** | MiniMax H3 (API v2) | 8 combinações + **voz clonada** + text-to-video |
| `../video-seedance25-byok/` | `FAL_KEY` | Seedance 2.x + Wan Animate | 7 combinações + **editar o plano original** |
| `../video-person-swap-seedance-2/` | Login comfy.org | Seedance 2.0 partner | Troca de pessoa com verificação facial |
| `../video-person-replace/` | `FAL_KEY` | Wan 2.2 Animate + Pixverse | Edita o vídeo original |

**Qual escolher:** o MiniMax é o único que **gera áudio com timbre clonado** na mesma
passada. O Seedance vai a resoluções maiores (4k) e tem o Wan Animate junto para editar
planos. Os dois são BYOK e não dependem do comfy.org.

---

## Referências

- Card de API: [`API_REFERENCE_video-minimax-h3-byok.md`](API_REFERENCE_video-minimax-h3-byok.md)
- API v2 — criar tarefa: <https://platform.minimax.io/docs/api-reference/video-generation-v2-create>
- API v2 — consultar tarefa: <https://platform.minimax.io/docs/api-reference/video-generation-v2-query>
- Upload de arquivo: <https://platform.minimax.io/docs/api-reference/file-management-upload>
- Guia de vídeo: <https://platform.minimax.io/docs/guides/video-generation>
- Caminho local/open-weights (não usado aqui): <https://docs.comfy.org/tutorials/video/minimax/minimax-h3>
- Nós de API online (catálogo geral): `.agents/skills/knowledge-comfyui-api-nodes`
