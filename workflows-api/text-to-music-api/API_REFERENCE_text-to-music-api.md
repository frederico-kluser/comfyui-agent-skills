# API Reference — text-to-music-api (ACE-Step por API de nuvem)

Gera trilha instrumental/ambient (e, se quiser, com vocal) por **API online**, sem GPU local.
Modelo único em 3 caminhos; **a escolha do provedor é jurídica, não técnica** (ver [Licenças](#licenças)).

## Decisão de provedor (o ponto que importa)

| Caminho | Nó/endpoint | Modelo / licença | Direito comercial | Custo | Quando usar |
|---|---|---|---|---|---|
| **Replicate** 🏆 | `fishaudio/ace-step-1.5` | ACE-Step **1.5 (MIT)** | ToS do Replicate **dá posse do output e SOBREVIVE ao cancelamento** (§5 + §9.5) → vender para sempre ✅ | ~US$0,095/faixa (10/US$1) | **Máxima segurança jurídica** na nuvem |
| **fal** | `fal-ai/ace-step` | ACE-Step **v1 3.5B (Apache-2.0)** | Modelo permissivo (sem restrição no output); **ToS do host fal não verificada** nesta pesquisa | por chamada (lê `FAL_KEY`) | Conveniência (schema confirmado, devolve WAV, casa com o padrão do repo) |
| **Local (ComfyUI)** | nós core ACE-Step | ACE-Step **v1 3.5B (Apache-2.0)** | Você roda os pesos abertos → **nenhuma ToS de host governa o output**. Licença mais limpa possível ✅✅ | **US$0/faixa** | Se tiver ~8GB de **VRAM** — grátis e sem intermediário |

> Regra prática: **para publicar e vender na Steam para sempre**, gere no **Replicate** (ToS verificada) ou **local**.
> O `fal` é ótimo para iterar rápido, mas a ToS do host não entrou no escopo verificado — o modelo Apache-2.0 não
> restringe o output, então o risco é baixo, mas não foi confirmado por fonte primária.

---

## 0) Cloud CLICÁVEL no ComfyUI (nós partner) — 2ª pesquisa

Nós de música por API **já instalados** no ComfyUI (modelo roda no provedor; sem GPU). **A licença decide qual usar.**

| Nó (clicável) | Modelo | Billing | Direito comercial (jogo pago) | Veredito |
|---|---|---|---|---|
| **`StabilityTextToAudio`** 🏆 | Stable Audio 2.5 | créditos comfy.org | ToS hospedada **§4.a CEDE a posse** do output ("we assign to you all of our right, title, and interest in the Outputs"); sobrevive ao cancelamento (§12.e→§10); **teto US$1M é só dos pesos self-hosted, não da API** | ✅ **Melhor cloud clicável** |
| `SoniloTextToMusic` | Sonilo v1.1 | créditos comfy.org | comercial **só no tier pago**; posse fraca ("assigns any rights we may have"); **sem cláusula de sobrevivência** → "vender pra sempre" não confirmado; "perpetual/irrevocable" na ToS corre USER→Sonilo (treino) | 🟡 **atrelado à assinatura** |
| `Replicate meta/musicgen` | MusicGen | Replicate | pesos **CC-BY-NC 4.0 = NÃO-COMERCIAL** (o código é MIT, mas os pesos que geram o áudio não são); o host não concede mais que a licença dos pesos | ⛔ **proibido** em jogo pago |
| ACE-Step via `comfyui-replicate` | ACE-Step 1.5 (MIT) | Replicate | **mais limpo em tese** (MIT), mas: (a) **não vem pré-instalado** (edite `supported_models.json` + `./import_schemas.py`); (b) o README avisa que **saídas de áudio "podem não funcionar"** | 🟡 setup + risco técnico |

> ⚠️ **Créditos comfy.org não dão direito por si**: a ToS do comfy.org define "Output" só como conteúdo **visual** — áudio de partner é regido pela ToS do **provedor** (Stability/Sonilo). Por isso o Stability, que **cede posse**, é o que importa.

### `StabilityTextToAudio` (o nó do `text-to-music-cloud.json`)
saída: `AUDIO` → `SaveAudio` (FLAC lossless). Ordem dos widgets: `model, prompt, duration, seed, [control], steps`.

| Widget | Vale | Nota |
|---|---|---|
| `model` | `stable-audio-2.5` | combo (versão hospedada) |
| `prompt` | estilo/tags | ex.: `dark ambient, deep drones, 80 BPM` |
| `duration` | INT (s) | segundos da faixa |
| `seed` | INT | `control_after_generate=randomize` p/ variar |
| `steps` | INT | ~8 (Stable Audio 2.5 usa poucos passos) |

---

## 1) fal — `fal-ai/ace-step`

Cliente: `@fal-ai/client` · auth: `FAL_KEY` · saída: objeto `audio.url` → **arquivo `.wav`**.

| Campo | Tipo | Default | Significado |
|---|---|---|---|
| `tags` | string | **obrigatório** | Estilo/gênero, separado por vírgula (é o "caption"). Ex.: `dark ambient, deep drones, 80 BPM` |
| `lyrics` | string | `""` | Letra com `[verse]`/`[chorus]`. **Vazio, `[inst]` ou `[instrumental]` = sem vocal** |
| `duration` | float | `60` | Segundos |
| `seed` | int | aleatório | Reprodutibilidade (aleatorize p/ faixa inédita) |
| `number_of_steps` | int | `27` | Passos de difusão |
| `scheduler` | enum | `euler` | `euler` \| `heun` |
| `guidance_type` | enum | `apg` | `cfg` \| `apg` \| `cfg_star` |
| `guidance_scale` | float | `15` | Aderência ao prompt |
| `tag_guidance_scale` | float | `5` | Influência do gênero |
| `lyric_guidance_scale` | float | `1.5` | Aderência ao vocal |

```js
import { fal } from "@fal-ai/client";
fal.config({ credentials: process.env.FAL_KEY });
const r = await fal.subscribe("fal-ai/ace-step", {
  input: { tags: "industrial techno instrumental, distorted synthesizers, 135 BPM", lyrics: "[inst]", duration: 60, seed: 12345 }
});
const url = r.data.audio.url; // .wav
```

## 2) Replicate — `fishaudio/ace-step-1.5`

Cliente: `replicate` · auth: `REPLICATE_API_TOKEN` · GPU L40S (~98s/faixa) · saída: URL de arquivo de áudio.

| Campo | Tipo | Default | Significado |
|---|---|---|---|
| `prompt` | string (≤512) | **obrigatório** | Estilo/gênero/mood/instrumentos (equivale ao `tags` do fal) |
| `lyrics` | string (≤4096) | `""` | Letra multilíngue, ou `[instrumental]` |
| `instrumental` | bool | `false` | **`true` força instrumental** independentemente de `lyrics` |
| `duration` | float | `-1` (auto) | Segundos (10–600); `-1`/≤0 = automático pelo tamanho da letra |
| `infer_step` | int | — | Passos de difusão (1–200; turbo usa 8, base ~50) |
| `guidance_scale` | float | — | Aderência ao prompt (1–15) |
| `shift` | float | — | Timestep shift |
| `seed` | int | aleatório | Reprodutibilidade |
| `thinking` | bool | `false` | LLM chain-of-thought p/ metadados (BPM/tom) |

```js
import Replicate from "replicate";
const replicate = new Replicate({ auth: process.env.REPLICATE_API_TOKEN });
const out = await replicate.run("fishaudio/ace-step-1.5", {
  input: { prompt: "dark ambient, deep drones, 80 BPM", instrumental: true, duration: 60, seed: 12345 }
});
```
> Confira o schema ao vivo em `replicate.com/fishaudio/ace-step-1.5/api` — provedores revisam campos.

## 3) Local — grafo nativo ACE-Step no ComfyUI (`text-to-music-local.json`)

**Nenhum custom node** — ACE-Step é **core** desde o ComfyUI de mai/2025. Só precisa do checkpoint.

- **Checkpoint**: `ace_step_v1_3.5b.safetensors` → `ComfyUI/models/checkpoints/`
  (de `huggingface.co/Comfy-Org/ACE-Step_ComfyUI_repackaged/all_in_one/`)
- **Cadeia**: `CheckpointLoaderSimple` → `ModelSamplingSD3` (shift **5.0**) → `LatentApplyOperationCFG` (+ `LatentOperationTonemapReinhard` 1.0) → `KSampler` → `VAEDecodeAudio` → **`SaveAudio`** (FLAC lossless)
- **Condicionamento**: `TextEncodeAceStepAudio` (widget 1 = `tags`, widget 2 = `lyrics`, widget 3 = 0.99) → `ConditioningZeroOut` (negativo) ; `EmptyAceStepLatentAudio` (segundos, batch)
- **KSampler**: seed(randomize), **steps 50, cfg 5, sampler `euler`, scheduler `simple`, denoise 1**
- **Instrumental**: deixe `lyrics` = `[instrumental]` (ou nomes de instrumentos). Vazio também serve.

| Nó de save | Formato | Loop perfeito? |
|---|---|---|
| **`SaveAudio`** (usado aqui) | **FLAC** (lossless) | ✅ bit-exato, sem padding |
| `SaveAudioOpus` | OGG/Opus | ✅ gapless via pre-skip |
| `SaveAudioMP3` | MP3 | ❌ padding de encoder quebra o loop |

---

## Licenças {#licenças}

Pesquisa multi-fonte (jul/2026), verificação adversarial 3-votos, fontes primárias (ToS oficiais).
Critério = **o direito comercial sobrevive ao cancelamento da assinatura?**

| # | Provedor | Posse ou licença? | Sobrevive ao cancelamento? | Veredito p/ jogo pago |
|---|---|---|---|---|
| 1 | **ACE-Step via Replicate** | **Posse** (Replicate §5.1) | **Sim** (§9.5 lista o §5) | 🏆 **Melhor** — perpétuo, menor risco |
| 2 | **ACE-Step local (open)** | Você roda os pesos (Apache-2.0/MIT) | N/A (sem host) | 🏆 **Licença mais limpa** + grátis |
| 3 | Soundraw | Licença (Soundraw mantém copyright) | **Sim** (perpétuo pós-download) | 🟢 ok, mas sem posse |
| 4 | Loudly | Licença (tier pago) | Provável (não citado explícito) | 🟢 ok |
| 5a | Stable Audio **hospedado** (API/nó `StabilityTextToAudio`) | **Posse cedida** (§4.a) | **Sim** — sobrevive (§12.e→§10); **sem** teto US$1M na API | 🟢 **cloud clicável ok** |
| 5b | Stable Audio **pesos self-hosted** (Community License) | Posse do output | Licença **revogável** + auto-termina acima de **US$1M/ano** | 🔴 não usar (é a licença dos pesos, não da API) |
| 6 | **Suno** (Pro/Premier) | **Posse** (assignment) | Sim (assignment é transferência) | 🔴 **em litígio** (Sony/UMG/Warner) |
| 7 | Udio | ToS não verificada | — | 🔴 **em litígio** |
| 8 | Beatoven.ai | Licença | **Não** ("perpétuo… durante o termo" se contradiz) | ⛔ **atrelado à assinatura** |
| 9 | Mubert (via API) | Licença "time-limited" | **Não** (cessa no fim do período) | ⛔ **atrelado à assinatura** |

**Não verificados** (sem evidência nesta rodada — não assuma): ElevenLabs Music, Google Lyria/Vertex, Aimi, Cassette AI.

### Ressalvas honestas
- **"Posse" pode ser oca**: o US Copyright Office trata obra puramente gerada por IA como **não-registrável**; Suno e Stability
  isentam garantia de que copyright "recai" no output. Ou seja, ninguém tem exclusividade forte — mas isso **não atrapalha seu
  objetivo**: você não precisa ser dono do copyright, precisa do **direito irrevogável de USAR/VENDER**. O caminho ACE-Step (Replicate/local) entrega isso.
- **Hipótese "MIT gruda no output" — parcialmente refutada**: a licença permissiva cobre **código/pesos**, não o áudio gerado
  (o output não é obra derivada do modelo). O direito perpétuo vem da **ToS do host** (Replicate) + **ausência de termos
  restritivos** do modelo — não de uma cláusula da licença MIT/Apache. Rodando **local**, não há host nenhum → o ponto é acadêmico.
- **Litígio Suno/Udio**: processos das majors (jun/2024) **em aberto** em 2026 (Warner fez acordo nov/2025; Sony/UMG seguem). Risco vivo para produto vendido.
- **Formato para loop**: MP3/AAC inserem *encoder delay + padding* (silêncio) no início/fim → quebra o loop no Web Audio API/Electron.
  **WAV, FLAC e Opus/OGG** não têm esse problema. Gere lossless; no Electron, use `loopStart`/`loopEnd` no `AudioBufferSourceNode`.

## Fontes
- Replicate ToS §5.1/§9.5 — https://replicate.com/terms
- ACE-Step (Apache-2.0) — https://github.com/ace-step/ACE-Step · ACE-Step 1.5 (MIT) — https://github.com/ace-step/ACE-Step-1.5
- fal ACE-Step — https://fal.ai/models/fal-ai/ace-step/api · Replicate — https://replicate.com/fishaudio/ace-step-1.5
- Suno ToS — https://suno.com/terms-of-service · Stability — https://stability.ai/license
- Soundraw — https://soundraw.io/license · Loudly — https://www.loudly.com/license-agreement
- Beatoven — https://www.beatoven.ai/tos · Mubert — https://mubert.com/render/docs/subscription-agreement
- Litígio RIAA — https://www.riaa.com/record-companies-bring-landmark-cases-for-responsible-ai-againstsuno-and-udio-in-boston-and-new-york-federal-courts-respectively/
- Loop/padding — https://en.wikipedia.org/wiki/Gapless_playback · Checkpoint ACE-Step — https://huggingface.co/Comfy-Org/ACE-Step_ComfyUI_repackaged
