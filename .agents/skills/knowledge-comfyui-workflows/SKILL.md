---
name: knowledge-comfyui-workflows
description: >-
  Conhecimento de construção de workflows no ComfyUI (foco vídeo): grafo de nós e tipos/cores de slot,
  os dois formatos JSON (UI vs API), a cadeia WanVideoWrapper (I2V/T2V), Context Windows para vídeo
  >81 frames, técnicas low-VRAM (block swap, fp8/GGUF, tiled VAE), organização (groups/subgraphs/get-set)
  e erros comuns. Use ao montar, adaptar, exportar ou entender qualquer workflow de vídeo/imagem — mesmo
  sem citar a skill. Não cobre os parâmetros específicos do SCAIL-2 (ver knowledge-scail2).
metadata:
  version: 0.1.0
  type: knowledge
---
# ComfyUI — Construção de Workflows (vídeo)

ComfyUI é programação visual procedural: nós = operações, fios = dados tipados. O grafo é um DAG executado
por dependência com cache (só re-roda nós cujas entradas mudaram).

## Quando usar
Montar/adaptar workflow, entender um JSON alheio, exportar para API, lidar com vídeo longo, otimizar VRAM,
organizar um grafo grande. Para diagnosticar falhas → `task-debug-generation`.

## Fundamentos
- Workflow txt→imagem: Load Checkpoint (→MODEL/CLIP/VAE) → CLIP Text Encode (+/−) → Empty Latent → KSampler → VAE Decode → Save Image.
- Slots são **fortemente tipados** (só conecta a mesma cor): MODEL (lilás), CLIP (amarelo), VAE (vermelho),
  CONDITIONING (laranja), LATENT (rosa), IMAGE (azul), MASK (verde), CLIP_VISION.
- KSampler `widgets_values` é lista **posicional**: `[seed, control_after_generate, steps, cfg, sampler_name, scheduler, denoise]`.
- Atalhos: `Ctrl+Enter` (queue), `Ctrl+B` (bypass), `Ctrl+M` (mute), `Ctrl+G` (group).

## Dois formatos JSON (distinção crítica)
- **UI/LiteGraph** (salvo/carregado na tela): tem `nodes[]`, `links[]`, `groups[]`, posições — **não roda**
  direto no `/prompt`.
- **API/prompt** (Dev mode → "Save (API Format)"): dict plano `{id: {class_type, inputs}}`; conexões =
  `[node_id, output_index]`. É o que vai no `POST /prompt`.
- Metadados embutidos em PNG/mp4 (`VHS_VideoCombine save_metadata`) permitem arrastar o arquivo de volta —
  mas redes sociais **removem** metadados. **Sempre salve o JSON** (export), com nome datado.

## Cadeia WanVideoWrapper (Kijai) — vídeo
```
WanVideoModelLoader ─model─► WanVideoSampler ─samples─► WanVideoDecode ─► VHS_VideoCombine
LoadWanVideoT5TextEncoder ─► WanVideoTextEncode ─text_embeds─► (Sampler)
WanVideoEmptyEmbeds (T2V)  ─image_embeds─► (Sampler)   [I2V: WanVideoImageToVideoEncode + WanVideoClipVisionEncode]
WanVideoVAELoader ─vae─► (Decode)
```
- **I2V**: troque `WanVideoEmptyEmbeds` por `WanVideoImageToVideoEncode` (start_image via VAE + CLIP-vision
  `clip_vision_h`). `num_frames` default **81**, passo 4 (`((n-1)//4)*4+1`); `noise_aug_strength` adiciona
  movimento/nitidez; `start_latent_strength` menor = mais movimento; `tiled_vae` economiza memória.
- **Sampler**: entradas `model, image_embeds, text_embeds, shift, steps, cfg, seed, scheduler`; opcionais
  `context_options`, `cache_args/teacache_args`, `denoise_strength`, `samples` (v2v).
- `WanVideoTextEncodeCached` descarrega o T5 (sem pegada de VRAM/RAM). Prompt travel: prompts separados por `|`.

## Vídeo longo — Context Windows
`WanVideoContextOptions` → input `context_options` do Sampler. Divide em janelas sobrepostas que são geradas e
mescladas. Params: `context_schedule` (uniform_standard/looped/static), `context_frames` (81), `context_stride`
(4), `context_overlap` (16), `freenoise` (True). `delta = context_frames − context_overlap`. ⚠️ Incompatível
com o nó MultiTalk I2V. Alternativa SCAIL-2: `Brobert-in-aus/scail-auto-extend` (chunking + ancoragem +
color-match automáticos).

## Low-VRAM (ordem de ataque)
1. `WanVideoBlockSwap` — `blocks_to_swap` default 20, máx **40** (o 14B tem 40 blocos; o 1.3B tem 30).
   Economiza 10–15GB ao custo de ~5–15% de velocidade.
2. fp8 scaled → GGUF (city96, em `models/unet`, reduz VRAM 2–8×).
3. tiled VAE decode; `--lowvram`/`--novram`.
4. Reduza **frames** antes da resolução (frames multiplicam VRAM mais rápido). Mantenha múltiplos de 32.
- LoRA de aceleração: `WanVideoLoraSelect` (de `models/loras`, encadeável). LightX2V = 4 passos sem CFG
  (cfg=1) — `enable_cfg=false` senão borra. Wan **2.2** usa dois modelos (high+low noise) → dois Model
  Loaders + dois LoRA selects.

## Organização
Groups (`Ctrl+G`, titule "01-Modelos", "02-Prompt"...), Reroute (rgthree), Get/Set (KJNodes — variáveis globais,
evita fios cruzados), Bypass (pula o nó, dados passam) vs Mute (mata o ramo), Primitives (compartilhar seed/size).
**Subgraphs** (2026): encapsular uma seção como super-nó, aninhável, publicável (≥0.3.63 "Subgraph Blueprints");
nós internos "Inputs"/"Outputs" expõem slots. ⚠️ Ainda há bugs (previews ao vivo, Power Lora Loader dentro de subgraph).

## API (automação)
Porta 8188 (HTTP+WS). `POST /prompt {prompt: <api_json>, client_id}` → acompanhe via `/ws?clientId=`; resultados
em `/history/{id}`, arquivos em `/view`. O UI-JSON **não** roda no `/prompt` (precisa do formato API).

## Ficha de reprodução (sempre)
Um workflow guarda nós/conexões/params, **não** os modelos/custom nodes/paths. Registre: fonte, data, custom
nodes, versão do ComfyUI, modelos (+hash), seed/size/sampler/steps/cfg. Nomeie `AAAAMMDD-proposito-vN.json`.

## Referências (nível 3, sob demanda)
- `docs/workflow-guide.md` — guia completo (nós, JSON detalhado, recursos 2026, links da comunidade).
- Cadeia: parâmetros SCAIL-2 → `knowledge-scail2`; erros → `task-debug-generation`; montar do zero → `task-build-workflow`.

## Evolução
Append em `LEARNINGS.md` quando descobrir um nó novo, um default que mudou, um padrão de organização que
funcionou, ou uma incompatibilidade. Destile no corpo se virar estável (`version++`). Diff git para revisão.
