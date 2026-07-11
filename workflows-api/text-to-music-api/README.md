# text-to-music-api — gera trilha sonora comercializável por API

> **Card Informativo**

| | |
|---|---|
| 🎯 **Faz** | Gera **faixas instrumentais/ambient** (e vocais, se quiser) — prontas para loop, comercializáveis num jogo pago |
| 🧠 **Técnica** | Text-to-music por **API online** (sem GPU) **ou** ACE-Step **local** — 3 caminhos (abaixo) |
| 💳 **Custo/billing** | **comfy.org créditos** (nó Stability) · **Replicate** ~US$0,095/faixa · **fal** por chamada · **Local** = US$0 |
| 🔌 **Provedores/Nós** | `StabilityTextToAudio` (partner, clicável) · `fishaudio/ace-step-1.5` (Replicate) · `fal-ai/ace-step` · nós **core** ACE-Step (local) |
| 📥 **Entrada** | Um `preset` de estilo (tags/prompt) — instrumental por padrão; letra opcional |
| 📤 **Saída** | `.wav`/`.flac` **lossless, loopável** em `output/` (ou `ComfyUI/output/audio/`) |
| ⚖️ **Licença** | ACE-Step **MIT/Apache** · Stable Audio hospedado **cede a posse do output** (§4.a) → comercial perpétuo (ver [Licença](#licença)) |
| 🧱 **Requer** | Login comfy.org (cloud clicável) · Node 18+ (script) · ComfyUI + ~8GB VRAM (local) |
| 🟡 **Status** | Workflows validados contra o `/object_info` ao vivo (nós + widgets). Falta **smoke real** (precisa de créditos/chave) |

## Os 3 caminhos (todos comercializáveis)

| Caminho | Arquivo / como | Modelo · licença | Custo | Quando usar |
|---|---|---|---|---|
| **A) Cloud clicável** 🏆 | **`text-to-music-cloud.json`** (abre no ComfyUI) | **Stable Audio 2.5** · ToS hospedada **cede posse** do output (§4.a), sobrevive ao cancelamento (§12.e), **sem teto de US$1M** (isso é só dos pesos self-hosted) | créditos comfy.org | Quer clicar e gerar **dentro do ComfyUI**, comercial-limpo |
| **B) Cloud em lote** | **`gerar_trilhas.mjs`** (script Node) | **ACE-Step 1.5 (MIT)** no Replicate · ToS do host **dá posse + sobrevive** (§5/§9.5) | ~US$0,10/faixa | Gerar **dezenas** de faixas de madrugada; licença a mais limpa |
| **C) Local grátis** | **`text-to-music-local.json`** (ComfyUI) | **ACE-Step v1 (Apache-2.0)** · você roda os pesos, **nenhum host** | **US$0** | Tem ~8GB de VRAM (você tem: RTX 4070) — grátis, sem intermediário |

> **Descartados** para jogo pago (pesquisa de licença): **MusicGen** (`Replicate meta/musicgen`) = pesos **CC-BY-NC não-comercial**; **Sonilo** (`SoniloTextToMusic`) = comercial só no tier pago e **sem cláusula de sobrevivência** ("vender pra sempre" não confirmado); **Suno/Udio** = em litígio. Detalhes e citações em [`API_REFERENCE`](./API_REFERENCE_text-to-music-api.md#licenças).

## Status
🟡 **Rascunho funcional** — `text-to-music-cloud.json` e `text-to-music-local.json` validados contra o `/object_info` **ao vivo** (todos os nós existem, widgets alinhados, save em **lossless**); `gerar_trilhas.mjs` escrito contra os schemas confirmados de fal/Replicate. Falta o **smoke real** (gerar 1 faixa) — exige créditos comfy.org (A), `REPLICATE_API_TOKEN`/`FAL_KEY` (B) ou o checkpoint (C).

## Pré-requisitos
- **A) Cloud clicável:** ComfyUI logado em **platform.comfy.org** com **créditos** (o nó Stability é partner). Máquina 8GB basta.
- **B) Cloud lote:** Node.js 18+ e `REPLICATE_API_TOKEN` (r8_…) ou `FAL_KEY`.
- **C) Local:** ComfyUI + **~8GB VRAM**. ACE-Step é **core** (sem custom node); só o checkpoint.

## Setup
```bash
REPLICATE_API_TOKEN=r8_...  FAL_KEY=...  bash setup.sh
DOWNLOAD_CHECKPOINT=1  bash setup.sh    # opcional — baixa o modelo local (~3.5GB)
```
Copia/baixa o bundle para `~/ComfyUI/user/default/workflows/text-to-music-api/`, instala as libs Node do script e grava as chaves (do ambiente) em `~/ComfyUI/secrets.env`. **Nenhum segredo versionado.**

## Como usar

### A) Cloud clicável — ComfyUI + Stable Audio (recomendado p/ clicar e gerar)
1. **Login** em platform.comfy.org (Settings → User → Sign In) e garanta **créditos**.
2. Abra **`text-to-music-cloud.json`**.
3. No nó **Stability Text To Audio**: ajuste o **prompt** (use um preset abaixo), `duration` e `steps`. **Run**.
4. Sai `.flac` lossless em `ComfyUI/output/audio/`.

### B) Cloud em lote — script (dezenas de faixas, sem GPU)
```bash
source ~/ComfyUI/secrets.env
cd ~/ComfyUI/user/default/workflows/text-to-music-api
node gerar_trilhas.mjs --provider replicate --preset all --count 3    # ACE-Step 1.5 (MIT), ToS Replicate limpa
node gerar_trilhas.mjs --provider fal --preset perseguicao --count 10
```
Cada faixa vira `output/<preset>_<seed>.wav`.

### C) Local grátis — ComfyUI + ACE-Step (US$0/faixa)
1. `DOWNLOAD_CHECKPOINT=1 bash setup.sh` (uma vez).
2. Reinicie o ComfyUI, abra **`text-to-music-local.json`**, ajuste as **tags** e **Run**.

> **No painel *Workflows* do ComfyUI aparecem só os 2 `.json`** (`…-cloud` e `…-local`) — a sidebar filtra `.json`. Os outros arquivos da pasta (script, `presets.mjs`, docs) **não são workflows** e não abrem tela.

## Presets (estética hacker / cyberpunk / Mr. Robot)
Editáveis em **`presets.mjs`** (campo `tags`); no cloud clicável, cole a string no prompt do nó Stability.

| `id` | Uso no jogo | Estilo (tags) |
|---|---|---|
| `menu` | Menu / exploração furtiva | dark ambient, deep drones, suspenseful, shadowy, **80 BPM** |
| `tensao` | Invasão ativa | trip-hop, muted beats, noir, shadowy bass, cinematic, **90 BPM** |
| `perseguicao` | Fuga / perseguição | industrial techno, aggressive, distorted synths, pulsating bass, **135 BPM** |
| `ambiente` | Leito ambiente contínuo | cyberpunk ambient, glassy pads, subtle glitch, hypnotic, **70 BPM** |
| `confronto` | Quebra de firewall / boss | dark synthwave, driving arpeggios, ominous, tense, **120 BPM** |

## Loop perfeito e formato (Electron/Web Audio API)
- **Evite MP3/AAC**: encoder insere *delay + padding* (silêncio) → o loop "engasga". Por isso os 2 workflows salvam **FLAC** (lossless) e o script baixa **WAV**.
- No Electron: `decodeAudioData` → `AudioBufferSourceNode` com `loop=true` + `loopStart`/`loopEnd`.

## Validação
- ✅ `text-to-music-cloud.json` e `text-to-music-local.json` parseiam; **todos os nós existem no `/object_info` ao vivo**; widgets alinhados; save lossless; links íntegros.
- ✅ `bash -n setup.sh` ok; `node --check gerar_trilhas.mjs` ok; sem segredos no `.sh`.
- ⏳ **Smoke real** pendente (precisa de créditos/chave/checkpoint).

## Troubleshooting
| Sintoma | Causa | Ação |
|---|---|---|
| Nó Stability pede login / "insufficient credits" | sem login/créditos comfy.org | Settings → Sign In em platform.comfy.org; adicione créditos |
| Clico num arquivo e não abre tela | é doc/script, não workflow | Abra só os `.json` (`…-cloud`/`…-local`); o resto não é grafo |
| `Falta a lib …` (script) | deps Node ausentes | `npm i replicate @fal-ai/client` (ou `bash setup.sh`) |
| Loop com "clique"/gap | salvou MP3 | use os workflows (FLAC) ou o script (WAV); corte no zero-crossing |
| OOM no caminho local | pouca VRAM | use A ou B (nuvem) ou reduza `duration` |

## Referências
- Params, nós e **licenças com citação**: [`API_REFERENCE_text-to-music-api.md`](./API_REFERENCE_text-to-music-api.md)
- Nós de API online: skill `knowledge-comfyui-api-nodes` · Empacotamento: `task-package-workflow-project`
