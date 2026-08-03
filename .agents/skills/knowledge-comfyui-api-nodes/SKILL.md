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
  version: 0.2.0
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

**Princípio (do usuário):** *"fal vs Comfy não decide qualidade — o MODELO decide."*
⚠️ **Correção (2026-08-03):** a inferência antiga *"os modelos bons só estão no fal"* **caducou**. Nós partner **antigos**
ainda existem (`GeminiImageNode` = Gemini 2.5; `VeoVideoGenerationNode` = Veo 2), mas ao lado deles o comfy.org hoje serve a
**geração atual**: `GeminiNanoBanana2` (Gemini **3.1** Flash Image), `ByteDanceSeedreamNode` (Seedream **5.0**/4.5),
`ByteDance2ReferenceNode` (**Seedance 2.0**). **Sempre confira o `/object_info` ao vivo antes de assumir que um modelo só
existe no fal** — a lista muda a cada release. fal continua valendo p/ **gastar crédito fal já pago** e p/ o que o partner não serve.

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
| `Wan2214b_animate_{move,replace}_character_fal` | `seed` INT (def **24**) + `shift` INT (def **8**) — campos próprios | (live `/object_info`) sem slot `"fixed"`; saída é **URL** (`video_url`+`frames_zip_url`) → padrão A; `variations`=nº de saídas |

## Catálogo de nós (nome EXATO → o que é → rota/verdict)
**Vídeo (I2V/T2V/extend):**
- `Veo31_fal` — Veo 3.1, máx. qualidade, **24 fps**, durações 4/6/8s, 720p/1080p, **sem campo negative** (negativos em prosa).
- 🏆 **Seedance 2.0 (partner, comfy credits)** — `ByteDance2ReferenceNode` (reference-to-video: imagens + **vídeos** + áudios + assets), `ByteDance2TextToVideoNode`, `ByteDance2FirstLastFrameNode`. Saída **`VIDEO` nativo** (padrão B). `model` = `Seedance 2.0` (até **1080p**) ou `Seedance 2.0 Fast` (teto 720p). `duration` **4–15 s**, `ratio` `adaptive`, `generate_audio`. Seed **não é determinística** (só força re-run — está no tooltip). Refs: **9 imagens · 3 vídeos · 3 áudios**. → ver "Seedance 2.0 · humano real" abaixo.
- `SeedanceImageToVideo_fal` / `SeedanceProImageToVideo_fal` — Seedance 1.x; 480p = **rascunho barato**; Pro tem `end_image` + negative + seed.
- `KlingImage2VideoNode` / `KlingTextToVideoNode` / `KlingVideoExtendNode` / `KlingCameraControlI2VNode`+`KlingCameraControls` (partner) — Kling v2.x; câmera = **só 1 eixo ≠ 0** (range −10..+10); `KlingVideoExtendNode` encadeia `video_id`.
- `Kling*_fal` (`Kling25TurboPro_fal`, `Kling26Pro_fal`, `KlingO3Pro_fal`…), `MiniMax*`/`MinimaxHailuoVideoNode`, `LumaVideoNode`, `OpenAIVideoSora2`, `LtxvApi*`, `PixverseImageToVideoNode`, `GrokVideoNode`, `ByteDanceImageToVideoNode` (Seedance partner — `seedance-1-5-pro` tem 1080p+`generate_audio`).
**Vídeo→Vídeo (transformar um vídeo existente — entra por core `LoadVideo` → input `video`):**
- **Restyle/edit:** `RunwayAleph2VideoToVideoNode` (🏆 restyle in-context, vídeo 2–30s, partner) · `GrokVideoEditNode` (clipe ≤8.7s/50MB, partner) · `KlingOmniVideoToVideoEdit_fal` (edit + inserir elementos por referência).
- **Motion-transfer / animar personagem (substituto-API do SCAIL-2):** `Wan2214b_animate_{move,replace}_character_fal` (imagem do sujeito + vídeo-guia) · `KlingV3ProMotionControl_fal`/`KlingV3StandardMotionControl_fal`.
- **Extend:** `GrokVideoExtendNode` (arquivo 2–15s, partner) · `KlingVideoExtendNode` (só `video_id`, **não** arquivo; encadeia) · `ViduExtendVideoNode` (arquivo, partner) · método Veo-handoff (`GetImageRangeFromBatch(-1)`).
**Imagem (gerar/editar) — 🏆 os 2 melhores por crédito comfy.org:**
- `GeminiNanoBanana2` (partner, "Nano Banana 2" = **Gemini 3.1 Flash Image**) — **tem seed**, `thinking_level` `MINIMAL|HIGH` (HIGH resolve perspectiva/oclusão/luz), `resolution` 1K/2K/4K, `aspect_ratio` `auto` (herda a entrada), **até 14 refs** via `BatchImagesNode`, `system_prompt` editável. Saídas: `IMAGE` · `STRING` · `thought_image` (o rascunho do raciocínio — bom p/ depurar).
- `ByteDanceSeedreamNode` (partner, "Seedream 4.5 & 5.0") — `seedream 5.0 lite`=`seedream-5-0-260128` (**14** refs, saída PNG) · `seedream-4-5-251128` (10 refs) · `seedream-4-0-250828`. ⚠️ **piso de pixels na saída: 3.686.400 (≈2560×1440) no 4.5/5.0** (921.600 no 4.0) — preset menor **rejeita antes de cobrar**. Teto ~10,4 MP no 5.0, ~16,7 MP no 4.5/4.0. `ByteDanceSeedreamNodeV2` tem o **mesmo display name** mas schema V3 → **widgets incompatíveis**; prefira a V1.
- Outros: `NanoBananaPro_fal` (Gemini 3, **sem seed**) · `FluxUltra_fal` · `Ideogram*` · `Recraft*` · `OpenAIDalle3`/`OpenAIGPTImage1`/`OpenAIGPTImageNodeV2`.
**Editar (instrução/inpaint):** `FluxProKontext_fal`/`FluxProKontextMulti_fal` (Kontext Max, face-swap/repose) · `FluxPro1Fill_fal` (inpaint) · `FluxEraseNode` (erase, partner, sem prompt) · `FluxVTONode`/`KlingVirtualTryOnNode` (try-on) · `QwenImageEditPlusLoRA_fal` (🏆 manter rosto+roupa; guidance 4.0, steps 32; **cold-start ~8 min**) · ⚠️ `NanoBananaEdit_fal` = Gemini 2.5 = **fraco** ("devolve a foto") → use Kontext Max ou Nano Banana **Pro**.
**Upscale:** `Upscaler_fal` (Clarity, redesenha → `creativity≈0.2` p/ retrato) · `Seedvr_Upscaler_fal` (SeedVR2, fidelidade sem perder identidade) · `TopazImageEnhance` · local grátis = `4x-UltraSharp` (ESRGAN).
**Áudio/3D:** `ElevenLabs*` (TTS/STT/SFX/clone de voz — **não** música) · `Meshy*`/`Tencent*` (3D).
**Música (text-to-music):** nós **partner clicáveis** de música — 🏆 **`SoniloTextToMusic`** (Sonilo, 0,53/seg — **único servido pelo comfy.org**, confirmado na tabela de preços + smoke; comercial só no tier pago, **sem cláusula de sobrevivência** → licença fraca; treino licenciado Shutterstock = baixo risco) · ✅ `ByteDanceSeedAudio` (Seed Audio 1.0, ~45/min, licença não verificada) · ⛔ **`StabilityTextToAudio`** (Stable Audio: existe no código e a ToS hospedada §4.a **seria** limpa, MAS **o comfy.org NÃO serve o endpoint** → `API Error: Not Found` **404**; NÃO está na tabela de preços) · `Replicate meta/musicgen` (`comfyui-replicate`) = **CC-BY-NC NÃO-comercial** ⛔. A licença mais limpa segue sendo **ACE-Step** por **script** (fal `fal-ai/ace-step` → `audio.url` WAV; Replicate `fishaudio/ace-step-1.5`, ~US$0,095/faixa) **ou** pelo grafo **core local** (`EmptyAceStepLatentAudio`→`TextEncodeAceStepAudio`→`KSampler` euler/simple/50/cfg5 + `ModelSamplingSD3` shift 5→`VAEDecodeAudio`→`SaveAudio`; checkpoint `ace_step_v1_3.5b.safetensors`, ~8GB VRAM, **sem custom node**). Instrumental = `lyrics` `[inst]`/`[instrumental]`. **Licença é o que decide o provedor:** ACE-Step **1.5=MIT / v1=Apache-2.0** → comercial perpétuo/irrevogável; no **Replicate** a ToS **dá posse do output e sobrevive ao cancelamento** (§5+§9.5) → melhor p/ vender "para sempre". 🔴 **Suno/Udio** = em litígio (Sony/UMG/Warner); ⛔ **Mubert/Beatoven** = direito atrelado à assinatura ativa. ⚠️ **créditos comfy.org NÃO dão direito por si**: a ToS do comfy.org define "Output" só como conteúdo **visual** → áudio de partner é regido pela ToS do **provedor** (o único servido é o Sonilo (licença fraca) → p/ direito comercial LIMPO use ACE-Step script/local). ⚠️ **valide na tabela de preços do comfy.org o que é REALMENTE servido** — o nó existir no `/object_info` ≠ o endpoint estar no ar (Stable Audio dá 404). Template Sonilo: `api_sonilo_t2m.json`. Bundle pronto: `workflows-api/text-to-music-api/`. Formato p/ loop: **WAV/FLAC/OGG, nunca MP3** (padding de encoder quebra o loop).
> **Não existe** node dedicado de face-swap/try-on tipo FASHN/IDM-VTON; `PixverseSwapNode_fal` é **vídeo**. P/ swap/repose use **Kontext Max multi** ou **Nano Banana Pro**.

## ⚠️ Seedance 2.0 · humano real exige asset verificado (trava silenciosa)
`reference_images` / `reference_videos` **recusam pessoa real**. P/ colocar uma pessoa real num vídeo o caminho é:
`LoadImage`→`ByteDanceCreateImageAsset` e `LoadVideo`→`ByteDanceCreateVideoAsset` → saídas `asset_id`+`group_id` →
liga o `asset_id` em `model.reference_assets.asset_N`.
- A verificação é **facial, por link H5** que o nó **loga no CONSOLE DO SERVIDOR** (não aparece na UI) e fica em polling.
- **`group_id`** verificado pula a verificação nas próximas vezes — **só na mesma conta**; 1 pessoa por imagem/vídeo.
- Antes de cada geração o nó revalida (`/proxy/seedance/assets/{id}`): status ≠ `Active` → `Reference asset N ... is not Active`.
- **Rótulos posicionais no prompt:** assets entram **depois** de images/videos/audios e continuam a contagem do mesmo tipo
  (0 refs + asset de imagem → **`Image 1`**; asset de vídeo → **`Video 1`**). ⚠️ a regex de reescrita é `\basset ?(\d{1,2})\b`
  → `asset 1`/`asset1` viram o rótulo, mas **`asset_1` (underscore) NÃO casa** e vai cru p/ o modelo. **Escreva `Image 1`/`Video 1` direto.**
- Padrão dos templates oficiais: o `asset_id` passa por um **`PreviewAny`** antes do Seedance (ele mostra **e repassa** a STRING).

## ⚠️ Schemas V3 (`COMFY_DYNAMICCOMBO_V3` / `COMFY_AUTOGROW_V3`) — como fiar à mão
Nós novos (Seedance 2.0, `BatchImagesNode`, `ByteDanceSeedreamNodeV2`, `OpenAIGPTImageNodeV2`) usam schema V3:
- **DYNAMICCOMBO**: os params vivem **dentro** da opção de `model` escolhida. `widgets_values[0]` = a **chave** da opção
  (ex.: `"Seedance 2.0"`), e o resto segue os params **daquela** opção. Trocar de opção troca a lista de widgets.
- **AUTOGROW**: slots nomeados **`<grupo>.<prefixo><n>`** — `images.image0…` (`BatchImagesNode`, **0-indexado**) e
  `model.reference_images.image_1…` (Seedance, **1-indexado**). O frontend mantém **um slot livre a mais** (`"shape": 7`).
- Widget convertido em input vira socket com o nome completo (ex.: `model.prompt`) e **assume o slot 0**.
- **Ordem dos `widgets_values` ≠ ordem do `/object_info`**: o frontend insere `control_after_generate` **logo depois do `seed`**.
  Reconstruir o nó fora dessa ordem embaralha os widgets **em silêncio**. **Copie a ordem de um template oficial.**

## 📁 Templates oficiais = a base known-good p/ adaptar
Vêm instalados com o ComfyUI (não precisa baixar): `…/site-packages/comfyui_workflow_templates_media_{api,image,video,other,core}/templates/*.json`.
Achar o exemplo de um nó: `grep -rl "<NodeType>" …/comfyui_workflow_templates*/templates/`.
Úteis aqui: `api_google_nano_banana2_image_edit` · `api_bytedance_seedream_5_0_lite_image_edit` ·
`template_eric_seedance_5_subject_and_outfit_combine` · `api_seedance2_0_r2v_real_human` ·
`template_seedance2_0_viral_videos_character_swap`.

## Gotchas dos nós fal
- **Bloqueiam sem barra de progresso** (`handler.get()` faz polling). Cold-start fica **minutos em `IN_QUEUE`** e ainda COMPLETA — não é travamento. Diagnóstico: `comfyui logs` → request_id → `curl -H "Authorization: Key $FAL_KEY" https://queue.fal.run/<endpoint>/requests/<id>/status`. `/interrupt` **não** mata o nó; só **reiniciar o servidor** mata. Itere em endpoints **warm** (Nano Banana Pro / Seedream / Kontext, ~30–60 s).
- **Vídeo — 2 padrões de saída (decide a fiação e o áudio):** **(A) nós fal `*_fal`** devolvem `video_url (STRING)` → `LoadVideoURL` → `CreateVideo` → `SaveVideo`. ⚠️ essa cadeia extrai **só frames** → **perde o áudio nativo** (baixe a URL original p/ manter). **(B) nós partner** (Veo/Kling/Grok/Runway/ByteDance/Vidu via comfy.org) devolvem **`VIDEO`** nativo → vai **direto no `SaveVideo`** (áudio preservado). Entrada de vídeo (V2V) = core **`LoadVideo`** (saída `VIDEO`); `LoadVideoURL`/`VHS_LoadVideo` dão frames IMAGE, não servem. Erro "Failed to upload video" só aparece no **console do servidor**.
- **Stub trap:** `/object_info/<Node>` devolve **200 com corpo vazio** p/ nós que o Manager conhece mas **não estão carregados** → "aparece na busca" ≠ instalado (confira `python_module` não-nulo). Liste reais: `curl -s :8188/object_info | jq 'keys'`.

## Chaves & segredos (regra do projeto)
- ComfyUI cloud → **`~/ComfyUI/secrets.env`** (`chmod 600`, gitignored), carregado pelo `run.sh`. **Nunca `~/.secrets`** (esse é só dos agentes de código — regra do router).
- `FAL_KEY` (env ou `config.ini`), `REPLICATE_API_TOKEN`; Partner = **login**, sem chave (comfy.org **não tem BYOK** no core; workaround `holo-q/comfy-api-liberation`).
- `HF_TOKEN` p/ baixar os modelos **locais** de apoio (SAM/DINO/ESRGAN). Os `setup.sh` de `workflows-api/` **leem a chave do ambiente** e gravam o `config.ini` — nunca embutem segredo.

## Referências
- Bundles que aplicam isto (todos **partner / créditos comfy.org**, zero custom node): `workflows-api/image-edit-nano-banana-2/` · `workflows-api/image-edit-seedream/` (6 edições de foto cada) · `workflows-api/video-person-swap-seedance-2/` (troca de pessoa em vídeo + fluxo de asset de humano real). Cada um traz um `API_REFERENCE_*.md` com a ordem exata dos `widgets_values`.
- Bundles fal antigos (`commercial-ondokai`, `mask-edit-cloud`, `outfit-swap-api`, `replace-*`, `image-to-video-api`, `video-to-video-api`, `extract-assets-api`, `text-to-music-api`) foram **removidos em 2026-08-03**; recuperáveis no git (commit `e1dd237` e anterior).
- Procedimento do comercial: `task-create-commercial-api`. Editar imagem: `task-edit-image` + `knowledge-image-editing`/`knowledge-image-masking`.
- API HTTP do ComfyUI (automação): `knowledge-comfyui-api`. GPU/custo self-hosted: `knowledge-runpod-infra`.
- Fonte de pesquisa: `config/06-ai-agents/comfyui-cloud-first.md` (+ `comfyui-edicao-por-mascara.md`).

## Evolução
Append em `LEARNINGS.md` ao descobrir: um novo nó/endpoint, um seed gate, um modelo que substituiu outro (versão), um
cold-start medido, ou um gotcha de billing. Atribua a fonte (usuário > inferência). Diff git p/ revisão humana.
