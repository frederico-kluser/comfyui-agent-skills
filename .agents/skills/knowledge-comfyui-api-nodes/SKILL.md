---
name: knowledge-comfyui-api-nodes
description: >-
  Conhecimento dos nós de API ONLINE do ComfyUI (modelo roda num provedor hospedado, paga por chamada): nós
  nativos partner (comfy.org credits) vs fal (`*_fal`) vs Replicate; catálogo de provedores/modelos (Veo 3.1,
  Nano Banana Pro, Kling, Seedance, Flux Pro/Kontext/Fill, Sora, Luma, Ideogram, Recraft, ElevenLabs) com os
  nomes de nó EXATOS; os seed gates que TRAVAM o nó; billing, chaves (secrets.env/FAL_KEY/login) e a decisão
  API-vs-self-hosted (regra dos 8GB). Use ao montar/rodar qualquer workflow que chame um modelo hospedado,
  escolher provedor, estimar créditos ou debugar um nó fal "travado" — mesmo sem citar a skill. NÃO cobre a API
  HTTP do próprio ComfyUI (ver knowledge-comfyui-api) nem GPU self-hosted/RunPod (ver knowledge-runpod-infra).
metadata:
  version: 0.1.0
  type: knowledge
---
# ComfyUI — Nós de API Online (geração hospedada)

O ComfyUI vira um **front-end de orquestração**: o grafo chama um modelo que roda **na nuvem do provedor**, paga-se
**por chamada**. Numa máquina de 8 GB isso é o caminho principal — a regra é *"nada de GGUF/quantizado/inferior
local"*: os modelos de ponta não cabem em 8 GB em precisão cheia, e a nuvem entrega um modelo **melhor e mais
rápido**. A GPU local só faz **máscara (SAM/GroundingDINO), composição (`ImageCompositeMasked`) e upscale ESRGAN**.

## Quando usar
"Rodar/montar workflow por API", "Veo/Kling/Nano Banana/Seedance/Flux Pro", "qual provedor", "quanto custa em
créditos", "nó `*_fal` travou", "fal vs Comfy", configurar `FAL_KEY`/login. Para a **API HTTP do próprio ComfyUI**
(`/prompt`, automação por código) → `knowledge-comfyui-api`. Para **alugar GPU** e rodar o modelo você mesmo → `knowledge-runpod-infra`.

## As 3 rotas (billing + credencial)
| Rota | Nós | Cobrança | Credencial |
|---|---|---|---|
| **Partner Nodes** (comfy.org) | `partner/*`: `Kling*`, `FluxVTONode`, `FluxEraseNode`, `GeminiNanoBanana2`, `OpenAIDalle3`, `Ideogram*`, `Recraft*`… | **Comfy credits** (free tier ~400 cr/mês) | **Login** `platform.comfy.org` (sem arquivo). Chave só com `--listen` |
| **fal.ai** (`ComfyUI-fal-API`, gokayfem) | sufixo **`*_fal`** | fal credits | `FAL_KEY` (env ou `custom_nodes/ComfyUI-fal-API/config.ini` `[API]`) |
| **Replicate** (`comfyui-replicate`) | nós Replicate | Replicate | `REPLICATE_API_TOKEN` (+ `import_schemas.py`) |

**Princípio (do usuário):** *"fal vs Comfy não decide qualidade — o MODELO decide."* Vários nós **partner** expõem só
versões **antigas** (`GeminiImageNode` = Gemini 2.5; `VeoVideoGenerationNode` = Veo 2) → a qualidade máxima vem do
**fal** (Veo 3.1, Nano Banana **Pro**/Gemini 3, Flux 1.1 Pro Ultra, Kontext Max). Ir pra fal serve p/ **gastar o crédito fal já pago**.

## Decisão: API vs self-hosted (RunPod)
- **API** (`workflows-api/`) quando: não quer/não pode alugar GPU; quer o **melhor** modelo (Veo/Nano Banana Pro); máquina fraca (8 GB). Paga por chamada.
- **Self-hosted** (`workflows-cloud/`) quando: precisa de modelo **sem API** (SCAIL-2, Wan Animate em GPU), volume alto previsível, controle total de pesos/LoRA. Paga GPU/segundo → `knowledge-runpod-infra`.

## ⚠️ Seed gates (errar o valor TRAVA o nó — a regra mais cara de errar)
Cada nó trata "seed aleatória" diferente; o gate está no código do nó.
| Nó | Valor p/ aleatório | Gate / nota |
|---|---|---|
| `FluxPro1Fill_fal` | **`0`** | `!= 0` → **`-1` TRAVA**. `mask_image` é **IMAGE** (use `MaskToImage`) |
| `FluxProKontext_fal` / `FluxProKontextMulti_fal` (`max_quality`) | **`0`** | gate `> 0` |
| `FluxUltra_fal` (Flux 1.1 Pro Ultra) / `Upscaler_fal` (Clarity) | **`-1`** | gate `!= -1` |
| `SeedanceImageToVideo_fal` / `SeedanceProImageToVideo_fal` | `-1` (tem seed) | reprodutível p/ vídeo |
| `Veo31_fal` · `NanoBananaPro_fal` · `NanoBananaEdit_fal` | **sem seed** | trava por **âncora**; p/ repro use `Veo3FirstLastFrameNode` / `SeedanceProImageToVideo_fal` / `GrokVideoExtendNode` |
| Pixverse `*_fal` | — | **1-indexed** (`keyframe_id=1`; 0 é rejeitado) |
| Wan 2.2 Animate `*_fal` | precisa slot `"fixed"` após o seed | senão `"high"` cai no `shift` (INT) → erro; saída é **LIST** → `variations=1` |

## Catálogo de nós (nome EXATO → o que é → rota/verdict)
**Vídeo (I2V/T2V/extend):**
- `Veo31_fal` — Veo 3.1, máx. qualidade, **24 fps**, durações 4/6/8s, 720p/1080p, **sem campo negative** (negativos em prosa).
- `SeedanceImageToVideo_fal` / `SeedanceProImageToVideo_fal` — Seedance; 480p = **rascunho barato**; Pro tem `end_image` + negative + seed.
- `KlingImage2VideoNode` / `KlingTextToVideoNode` / `KlingVideoExtendNode` / `KlingCameraControlI2VNode`+`KlingCameraControls` (partner) — Kling v2.x; câmera = **só 1 eixo ≠ 0** (range −10..+10); `KlingVideoExtendNode` encadeia `video_id`.
- `Kling*_fal` (`Kling25TurboPro_fal`, `KlingV3Pro_fal`…), `MiniMax*`/`MinimaxHailuoVideoNode`, `LumaVideoNode`, `OpenAIVideoSora2`, `LtxvApi*`, `PixverseImageToVideoNode`, `GrokVideo*`, `Wan2214b_animate_{move,replace}_character_fal` (substituto de SCAIL-2 em 8 GB).
**Imagem (gerar):** `NanoBananaPro_fal` (Gemini 3, **sem seed**, multi-img via `ImageBatch`) · `GeminiNanoBanana2` (partner, **tem seed**) · `FluxUltra_fal` (Flux 1.1 Pro Ultra) · `ByteDanceSeedream*`/Seedream V4.5 (slots `image_1..10`, 4K, tem seed) · `Ideogram*` · `Recraft*` · `OpenAIDalle3`/`OpenAIGPTImage1`.
**Editar (instrução/inpaint):** `FluxProKontext_fal`/`FluxProKontextMulti_fal` (Kontext Max, face-swap/repose) · `FluxPro1Fill_fal` (inpaint) · `FluxEraseNode` (erase, partner, sem prompt) · `FluxVTONode`/`KlingVirtualTryOnNode` (try-on) · `QwenImageEditPlusLoRA_fal` (🏆 manter rosto+roupa; guidance 4.0, steps 32; **cold-start ~8 min**) · ⚠️ `NanoBananaEdit_fal` = Gemini 2.5 = **fraco** ("devolve a foto") → use Kontext Max ou Nano Banana **Pro**.
**Upscale:** `Upscaler_fal` (Clarity, redesenha → `creativity≈0.2` p/ retrato) · `Seedvr_Upscaler_fal` (SeedVR2, fidelidade sem perder identidade) · `TopazImageEnhance` · local grátis = `4x-UltraSharp` (ESRGAN).
**Áudio/3D:** `ElevenLabs*` (TTS/STT/SFX/clone) · `Meshy*`/`Tencent*` (3D).
> **Não existe** node dedicado de face-swap/try-on tipo FASHN/IDM-VTON; `PixverseSwapNode_fal` é **vídeo**. P/ swap/repose use **Kontext Max multi** ou **Nano Banana Pro**.

## Gotchas dos nós fal
- **Bloqueiam sem barra de progresso** (`handler.get()` faz polling). Cold-start fica **minutos em `IN_QUEUE`** e ainda COMPLETA — não é travamento. Diagnóstico: `comfyui logs` → request_id → `curl -H "Authorization: Key $FAL_KEY" https://queue.fal.run/<endpoint>/requests/<id>/status`. `/interrupt` **não** mata o nó; só **reiniciar o servidor** mata. Itere em endpoints **warm** (Nano Banana Pro / Seedream / Kontext, ~30–60 s).
- **Vídeo:** os nós fal fazem upload do VIDEO sozinhos; saída `video_url (STRING)` → `LoadVideoURL` → `CreateVideo` → `SaveVideo`. ⚠️ essa cadeia extrai **só frames** → **perde o áudio nativo** (baixe a URL original p/ manter). Erro "Failed to upload video" só aparece no **console do servidor**.
- **Stub trap:** `/object_info/<Node>` devolve **200 com corpo vazio** p/ nós que o Manager conhece mas **não estão carregados** → "aparece na busca" ≠ instalado (confira `python_module` não-nulo). Liste reais: `curl -s :8188/object_info | jq 'keys'`.

## Chaves & segredos (regra do projeto)
- ComfyUI cloud → **`~/ComfyUI/secrets.env`** (`chmod 600`, gitignored), carregado pelo `run.sh`. **Nunca `~/.secrets`** (esse é só dos agentes de código — regra do router).
- `FAL_KEY` (env ou `config.ini`), `REPLICATE_API_TOKEN`; Partner = **login**, sem chave (comfy.org **não tem BYOK** no core; workaround `holo-q/comfy-api-liberation`).
- `HF_TOKEN` p/ baixar os modelos **locais** de apoio (SAM/DINO/ESRGAN). Os `setup.sh` de `workflows-api/` **leem a chave do ambiente** e gravam o `config.ini` — nunca embutem segredo.

## Referências
- Bundles que aplicam isto: `workflows-api/commercial-ondokai/` (Veo+Nano Banana+Kling+Seedance), `workflows-api/mask-edit-cloud/` (`FluxPro1Fill_fal`), `workflows-api/outfit-swap-api/`.
- Procedimento do comercial: `task-create-commercial-api`. Editar imagem: `task-edit-image` + `knowledge-image-editing`/`knowledge-image-masking`.
- API HTTP do ComfyUI (automação): `knowledge-comfyui-api`. GPU/custo self-hosted: `knowledge-runpod-infra`.
- Fonte de pesquisa: `config/06-ai-agents/comfyui-cloud-first.md` (+ `comfyui-edicao-por-mascara.md`).

## Evolução
Append em `LEARNINGS.md` ao descobrir: um novo nó/endpoint, um seed gate, um modelo que substituiu outro (versão), um
cold-start medido, ou um gotcha de billing. Atribua a fonte (usuário > inferência). Diff git p/ revisão humana.
