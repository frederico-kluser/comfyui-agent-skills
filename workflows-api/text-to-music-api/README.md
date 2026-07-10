# text-to-music-api — gera trilha sonora comercializável por API (ACE-Step)

> **Card Informativo**

| | |
|---|---|
| 🎯 **Faz** | Gera **faixas instrumentais/ambient** (e vocais, se quiser) por **API online** — em lote, prontas para loop |
| 🧠 **Técnica** | Text-to-music com **ACE-Step** (modelo roda no provedor; sem GPU local) |
| 💳 **Custo/billing** | **Replicate** (~US$0,095/faixa, lê `REPLICATE_API_TOKEN`) · **fal** (por chamada, lê `FAL_KEY`) · **Local** = US$0 |
| 🔌 **Provedores/Nós** | `fishaudio/ace-step-1.5` (Replicate) · `fal-ai/ace-step` (fal) · nós **core** ACE-Step (ComfyUI local) |
| 📥 **Entrada** | Um `preset` de estilo (tags/prompt) — instrumental por padrão; letra opcional |
| 📤 **Saída** | `.wav` (nuvem) ou `.flac` (local) em `output/` — **lossless, loopável** |
| ⚖️ **Licença** | ACE-Step **1.5 = MIT**, **v1 = Apache-2.0** → uso comercial **perpétuo e irrevogável** (ver [Licença](#licença)) |
| 🧱 **Requer** | Node.js 18+ (script de nuvem) **ou** ComfyUI + ~8GB VRAM (caminho local) |
| 🟡 **Status** | Grafo local validado (parse + nós core + save FLAC); script pronto. Falta **smoke real** (precisa de chave) |

## Por que ACE-Step (e não Suno/Udio)?

Você quer **vender o jogo na Steam para sempre** — inclusive depois de cancelar a assinatura da API. Pesquisa de
licenças (multi-fonte, verificação adversarial, ToS primárias) apontou:

- ✅ **ACE-Step** é permissivo (**MIT/Apache-2.0**): uso comercial perpétuo, irrevogável, sem royalties, sem atribuição no áudio.
- ✅ Servido no **Replicate**, a ToS do host **te dá a posse do output e sobrevive ao cancelamento** (§5 + §9.5) — o combo mais limpo na nuvem.
- ✅ Rodado **local**, é a licença mais limpa possível (você roda os pesos abertos; nenhum host governa o output).
- 🔴 **Suno/Udio**: apesar de "posse" no tier pago, estão **em litígio** com Sony/UMG/Warner (treino) → risco vivo para produto vendido.
- ⛔ **Mubert / Beatoven**: direito **atrelado à assinatura ativa** — não sobrevivem ao cancelamento. Reprovados no seu requisito.

Tabela completa e citações em **[`API_REFERENCE_text-to-music-api.md`](./API_REFERENCE_text-to-music-api.md)**.

## Status
🟡 **Rascunho funcional** — `text-to-music-local.json` validado (JSON parseia, nós são **core** do ComfyUI, save trocado para
**FLAC lossless**); `gerar_trilhas.mjs` escrito contra os schemas confirmados do fal e do Replicate. Falta o **smoke real**
(gerar 1 faixa), que exige `REPLICATE_API_TOKEN` e/ou `FAL_KEY`.

## Pré-requisitos
- **Caminho nuvem (recomendado):** Node.js 18+ e uma chave — `REPLICATE_API_TOKEN` (r8_…) **ou** `FAL_KEY`. Máquina de **8GB basta** (a geração é na nuvem).
- **Caminho local (bônus):** ComfyUI atual + **~8GB de VRAM**. ACE-Step é **core** (nenhum custom node); só baixe o checkpoint. Em CPU/iGPU roda, mas lento.

## Setup
```bash
REPLICATE_API_TOKEN=r8_...  FAL_KEY=...  bash setup.sh
# opcional, para o caminho LOCAL (baixa o modelo ~3.5GB):
DOWNLOAD_CHECKPOINT=1  bash setup.sh
```
O `setup.sh` copia/baixa o bundle para `~/ComfyUI/user/default/workflows/text-to-music-api/`, instala as libs Node
(`replicate`, `@fal-ai/client`) e grava as chaves (do ambiente) em `~/ComfyUI/secrets.env` (chmod 600). **Nenhum segredo é versionado.**

## Como usar

### A) Nuvem — lote por terminal (sem GPU)
```bash
source ~/ComfyUI/secrets.env
cd ~/ComfyUI/user/default/workflows/text-to-music-api

# 3 variações de CADA preset, no Replicate (ToS mais limpa para vender):
node gerar_trilhas.mjs --provider replicate --preset all --count 3

# 10 faixas de perseguição, no fal, 90s cada:
node gerar_trilhas.mjs --provider fal --preset perseguicao --count 10 --duration 90
```
Cada faixa vira `output/<preset>_<seed>.wav`. Rode um loop grande à noite e acorde com dezenas de trilhas livres de royalties.

### B) Local — ComfyUI (US$0/faixa, licença mais limpa)
1. `DOWNLOAD_CHECKPOINT=1 bash setup.sh` (uma vez).
2. Reinicie o ComfyUI, abra **`text-to-music-local.json`**.
3. Ajuste as **tags** (nó *Text Encode ACE Step Audio*) e **Run**. Sai `.flac` lossless em `ComfyUI/output/audio/`.

## Presets (estética hacker / cyberpunk / Mr. Robot)
Editáveis em **`presets.json`** (campo `tags` vale para fal e Replicate).

| `id` | Uso no jogo | Estilo (tags) |
|---|---|---|
| `menu` | Menu / exploração furtiva de terminal | dark ambient, deep drones, suspenseful, shadowy, **80 BPM** |
| `tensao` | Invasão ativa | trip-hop, muted beats, noir, shadowy bass, cinematic, **90 BPM** |
| `perseguicao` | Fuga / perseguição | industrial techno, aggressive, distorted synths, pulsating bass, **135 BPM** |
| `ambiente` | Leito ambiente contínuo | cyberpunk ambient, glassy pads, subtle glitch, hypnotic, **70 BPM** |
| `confronto` | Quebra de firewall / boss | dark synthwave, driving arpeggios, ominous, tense, **120 BPM** |

**Vocal?** Ponha `instrumental=false` e preencha `lyrics` com `[verse]`/`[chorus]` (no fal, `lyrics`; no Replicate, `lyrics` + `instrumental:false`).

## Parâmetros não-óbvios
| Campo | Vale | Nota |
|---|---|---|
| **provider** | `fal` \| `replicate` | `replicate` = ToS verificada p/ vender; `fal` = schema confirmado + WAV + padrão do repo |
| **instrumental** | padrão **ligado** | fal: `lyrics="[inst]"` · Replicate: `instrumental=true` |
| **duration** | segundos | 60 default; loops curtos (30–90s) tocam melhor no jogo |
| **seed** | aleatório | randomizado por faixa → variação inédita |
| **formato** | WAV/FLAC/OGG | **nunca MP3** para loop (ver abaixo) |

## Loop perfeito e formato (importa para Electron/Web Audio API)
- **Evite MP3/AAC**: o encoder insere *delay + padding* (silêncio) no início/fim → o loop "engasga".
- **Use WAV (nuvem) ou FLAC/Opus-OGG (local)** — lossless, bit-exato, sem padding.
- No Electron, carregue via `decodeAudioData` e toque com `AudioBufferSourceNode` usando `loop=true` + `loopStart`/`loopEnd`.

## Validação
- ✅ `text-to-music-local.json` parseia; nós são **core** (`EmptyAceStepLatentAudio`, `TextEncodeAceStepAudio`, `VAEDecodeAudio`, `SaveAudio`); link áudio→save íntegro.
- ✅ `bash -n setup.sh` ok; sem segredos no `.sh`.
- ⏳ **Smoke real** pendente: `node gerar_trilhas.mjs --preset menu --count 1` (precisa de chave) → deve sair 1 `.wav` em `output/`.

## Troubleshooting
| Sintoma | Causa provável | Ação |
|---|---|---|
| `Falta a lib: rode npm i …` | deps Node ausentes | `cd` no bundle e `npm i replicate @fal-ai/client` (ou `bash setup.sh`) |
| `Defina REPLICATE_API_TOKEN/FAL_KEY` | chave não exportada | `source ~/ComfyUI/secrets.env` antes de rodar |
| Replicate erro de campo | schema mudou | confira `replicate.com/fishaudio/ace-step-1.5/api` e ajuste o `input` |
| Nó vermelho no ComfyUI local | ComfyUI desatualizado | atualize o ComfyUI (ACE-Step é core recente); baixe o checkpoint |
| Loop com "clique"/gap | salvou em MP3 | regere em WAV/FLAC/OGG; corte no zero-crossing |
| OOM no caminho local | pouca VRAM | use a nuvem (recomendado) ou reduza `duration` |

## Referências
- Params, nós e **licenças com citação**: [`API_REFERENCE_text-to-music-api.md`](./API_REFERENCE_text-to-music-api.md)
- Conhecimento de nós de API online: skill `knowledge-comfyui-api-nodes`
- Empacotamento deste bundle: skill `task-package-workflow-project`
