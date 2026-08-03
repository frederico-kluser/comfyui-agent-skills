# text-to-music-api — gera trilha sonora comercializável por API

> **Card Informativo**

| | |
|---|---|
| 🎯 **Faz** | Gera **faixas instrumentais/ambient** (e vocais, se quiser) — prontas para loop, comercializáveis num jogo pago |
| 🧠 **Técnica** | Text-to-music por **API online** (sem GPU) **ou** ACE-Step **local** — 3 caminhos (abaixo) |
| 💳 **Custo/billing** | **Replicate** ~US$0,10/faixa · **fal** por chamada · **comfy.org créditos** (nó Sonilo) · **Local** = US$0 |
| 🔌 **Provedores/Nós** | `fal-ai/ace-step` · `fishaudio/ace-step-1.5` (Replicate) · `SoniloTextToMusic` (partner, clicável) · nós **core** ACE-Step (local) |
| 📥 **Entrada** | Um `preset` de estilo (tags/prompt) — instrumental por padrão; letra opcional |
| 📤 **Saída** | `.wav`/`.flac` **lossless, loopável** em `output/` (ou `ComfyUI/output/audio/`) |
| ⚖️ **Licença** | ACE-Step **MIT/Apache** = comercial **perpétuo/irrevogável** (o caminho mais limpo) · Sonilo = comercial só no **tier pago** (ver [Licença](#licença)) |
| 🧱 **Requer** | Node 18+ (script, **testado ✅**) · login comfy.org + créditos (Sonilo) · ComfyUI + ~8GB VRAM (local) |
| 🟢 **Status** | **Caminho fal (script) TESTADO** — gerou WAV real. Cloud clicável (Sonilo) e local validados contra o `/object_info` |

## Os 3 caminhos (todos comercializáveis)

| Caminho | Arquivo / como | Modelo · licença | Custo | Status |
|---|---|---|---|---|
| **B) Cloud em lote** 🏆 | **`gerar_trilhas.mjs`** (script Node) | **ACE-Step (MIT/Apache)** no **fal**/Replicate · licença mais limpa (comercial perpétuo) | ~US$0,02–0,10/faixa | ✅ **testado — gerou WAV** |
| **C) Local grátis** | **`text-to-music-local.json`** (ComfyUI) | **ACE-Step v1 (Apache-2.0)** · você roda os pesos, **nenhum host** | **US$0** | 🟡 precisa baixar o modelo (3.5GB) |
| **A) Cloud clicável** | **`text-to-music-cloud.json`** (ComfyUI) | **Sonilo** · comercial **só no tier pago**, **sem cláusula de sobrevivência** (treinado em conteúdo licenciado → baixo risco de litígio) | créditos comfy.org (0,53/seg) | 🟡 clicável, mas licença mais fraca |

> **Para "vender na Steam para sempre", prefira B ou C (ACE-Step MIT/Apache).** O **A (Sonilo)** é o único **clicável cloud** que o comfy.org realmente serve, mas o direito comercial depende do tier pago.
>
> **Descartados:** ⛔ **Stable Audio** (nó `StabilityTextToAudio`) — existe no código do ComfyUI mas **o comfy.org NÃO serve esse endpoint** → dá **`API Error: Not Found` (404)**; ⛔ **MusicGen** (`Replicate meta/musicgen`) = pesos **CC-BY-NC não-comercial**; 🔴 **Suno/Udio** = em litígio. Detalhes em [`API_REFERENCE`](./API_REFERENCE_text-to-music-api.md#licenças).

## Pré-requisitos
- **B) Script (recomendado):** Node.js 18+ e `FAL_KEY` (ou `REPLICATE_API_TOKEN`). Máquina 8GB basta.
- **C) Local:** ComfyUI + **~8GB VRAM** (sua RTX 4070 serve). ACE-Step é **core** (sem custom node); só o checkpoint.
- **A) Sonilo:** ComfyUI logado em **platform.comfy.org** com **créditos**.

## Setup
```bash
FAL_KEY=...  REPLICATE_API_TOKEN=r8_...  bash setup.sh
DOWNLOAD_CHECKPOINT=1  bash setup.sh    # opcional — baixa o modelo local (~3.5GB)
```
Copia/baixa o bundle para `~/ComfyUI/user/default/workflows/text-to-music-api/`, checa o Node e grava as chaves (do ambiente) em `~/ComfyUI/secrets.env`. **O script é zero-dependência (só o `fetch` nativo do Node 18+) — sem `npm install`, sem `node_modules`. Nenhum segredo versionado.**

## Como usar

### B) Cloud em lote — script (recomendado, testado ✅)
```bash
source ~/ComfyUI/secrets.env
cd ~/ComfyUI/user/default/workflows/text-to-music-api
node gerar_trilhas.mjs --provider fal --preset menu --count 1            # 1 faixa (testado — gera WAV)
node gerar_trilhas.mjs --provider replicate --preset all --count 3       # ACE-Step 1.5 (MIT), ToS Replicate limpa
node gerar_trilhas.mjs --provider fal --preset perseguicao --count 10    # lote
```
Cada faixa vira `output/<preset>_<seed>.wav` (WAVE PCM 16-bit 48kHz, lossless).

### C) Local grátis — ComfyUI + ACE-Step (US$0/faixa)
1. `DOWNLOAD_CHECKPOINT=1 bash setup.sh` (uma vez, baixa 3.5GB).
2. Reinicie o ComfyUI, abra **`text-to-music-local.json`**, ajuste as **tags** e **Run** → `.flac` em `ComfyUI/output/audio/`.

### A) Cloud clicável — ComfyUI + Sonilo (clicável, mas licença mais fraca)
1. **Login** em platform.comfy.org com **créditos**.
2. Abra **`text-to-music-cloud.json`**, ajuste o **prompt** do nó *Sonilo Text To Music* e `duration`. **Run**.
3. Sai `.flac` em `ComfyUI/output/audio/`. ⚠️ Comercial só no **tier pago** do Sonilo.

> **No painel *Workflows* do ComfyUI aparecem só os 2 `.json`** (`…-cloud` e `…-local`) — a sidebar filtra `.json`. Os outros arquivos (script, `presets.mjs`, docs) **não são workflows** e não abrem tela.

## Presets (estética hacker / cyberpunk / Mr. Robot)
Editáveis em **`presets.mjs`** (campo `tags`); no cloud clicável, cole a string no prompt do nó Sonilo.

| `id` | Uso no jogo | Estilo (tags) |
|---|---|---|
| `menu` | Menu / exploração furtiva | dark ambient, deep drones, suspenseful, shadowy, **80 BPM** |
| `tensao` | Invasão ativa | trip-hop, muted beats, noir, shadowy bass, cinematic, **90 BPM** |
| `perseguicao` | Fuga / perseguição | industrial techno, aggressive, distorted synths, pulsating bass, **135 BPM** |
| `ambiente` | Leito ambiente contínuo | cyberpunk ambient, glassy pads, subtle glitch, hypnotic, **70 BPM** |
| `confronto` | Quebra de firewall / boss | dark synthwave, driving arpeggios, ominous, tense, **120 BPM** |

## Loop perfeito e formato (Electron/Web Audio API)
- **Evite MP3/AAC**: encoder insere *delay + padding* (silêncio) → o loop "engasga". Por isso o script baixa **WAV** e os workflows salvam **FLAC** (lossless).
- No Electron: `decodeAudioData` → `AudioBufferSourceNode` com `loop=true` + `loopStart`/`loopEnd`.

## Validação
- ✅ **Smoke test real** (fal): `node gerar_trilhas.mjs --provider fal --preset menu --count 1` → gerou `menu_*.wav` (WAVE PCM 16-bit 48kHz, ~12MB/60s).
- ✅ `text-to-music-cloud.json` (Sonilo) e `text-to-music-local.json` (ACE-Step): nós existem no `/object_info` ao vivo; widgets alinhados; save lossless.
- ✅ `bash -n setup.sh` · `node --check gerar_trilhas.mjs` · sem segredos no `.sh`.

## Troubleshooting
| Sintoma | Causa | Ação |
|---|---|---|
| `API Error: Not Found` no nó Stability | comfy.org **não serve** Stable Audio | Use o nó **Sonilo** (`…-cloud.json`) ou o **script** (fal/Replicate) |
| Nó Sonilo: `Unauthorized: Please login first` | sem login comfy.org | Settings → Sign In em platform.comfy.org + créditos |
| Script: `Defina FAL_KEY…` | chave não exportada | `source ~/ComfyUI/secrets.env` antes de rodar o script |
| Clico num arquivo e não abre tela | é doc/script, não workflow | Abra só os `.json` (`…-cloud`/`…-local`) |
| Loop com "clique"/gap | salvou MP3 | use o script (WAV) ou os workflows (FLAC); corte no zero-crossing |
| OOM no local | pouca VRAM | use B (script, sem GPU) ou reduza `duration` |

## Referências
- Params, nós e **licenças com citação**: [`API_REFERENCE_text-to-music-api.md`](./API_REFERENCE_text-to-music-api.md)
- Nós de API online: skill `knowledge-comfyui-api-nodes` · Empacotamento: `task-package-workflow-project`
