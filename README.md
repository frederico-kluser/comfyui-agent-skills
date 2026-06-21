# ComfyUI Commercials — RunPod Ops & Agent Skills

Base de conhecimento + sistema de **Agent Skills** para autorar **workflows de vídeo e de edição de
imagem IA** (SCAIL-2, Wan 2.1/2.2, Flux, Flux Fill/Kontext, Qwen-Image-Edit, SAM/inpaint) no **ComfyUI**
e empacotá-los como **bundles prontos para rodar** — por **API online** (Veo 3.1, Kling, Nano Banana, Seedance; sem GPU) ou **self-hosted no RunPod.io** (GPU alugada).

Não é um app: o valor está (1) na pesquisa curada em `docs/`, (2) nas skills em `.agents/skills/` que
injetam esse conhecimento sob demanda, e (3) nos **projetos de workflow** entregáveis em `workflows-api/`
(rodam por API online, sem GPU) e `workflows-cloud/` (self-hosted em GPU RunPod).

> Para **agentes de código** (Claude Code, Cursor, Codex…) a porta de entrada é o `AGENTS.md` +
> `.agents/skills/project-router`. Este README é a porta de entrada para **humanos**.

## Por que existe
Produzir vídeo no ComfyUI/RunPod envolve muito conhecimento não-óbvio e volátil (paths de modelo,
parâmetros de sampler, VRAM/GPU, custom nodes, custo por segundo). Em vez de despejar tudo num
arquivo gigante (que degrada o agente — ETH Zurich, arXiv:2602.11988), o conhecimento é **fatiado em
skills carregadas sob demanda** (progressive disclosure) e **evolui com o uso**, sempre com revisão humana.

## Arquitetura (3 camadas)
1. **`AGENTS.md`** (always-on, mínimo) — comandos e convenções não-óbvias; aponta para o router.
   `CLAUDE.md` é symlink para ele.
2. **`.agents/skills/`** (fonte única; symlink `.claude/skills/`) — skills de **conhecimento** (memória
   semântica), de **tarefa** (procedural, com passo `<evolution>` + `LEARNINGS.md`) e **meta** (evolução/GC).
3. **`project-router`** — despacha TODA tarefa para a cadeia de skills certa antes de implementar.

## Estrutura
```
docs/                     # relatórios de pesquisa (a fonte: SCAIL-2, workflows, RunPod, provisioning)
.agents/skills/           # o sistema de skills (catálogo em catalog.md)
  project-router/         #   roteador
  knowledge-*/            #   conhecimento — vídeo (scail2, comfyui-workflows, runpod-infra/-provisioning)
                          #              + imagem (image-editing, image-masking, comfyui-api, image-enhance)
                          #              + API online (comfyui-api-nodes: partner/fal/Replicate)
  task-*/                 #   tarefas (create-commercial, create-commercial-api, build-workflow, launch-pod,
                          #            debug, package-workflow-project, edit-image)
  meta-*/                 #   evolução e consolidação
workflows-api/            # bundles que rodam por API online, sem GPU (commercial-ondokai, mask-edit-cloud, outfit-swap-api)
workflows-cloud/          # bundles self-hosted em GPU RunPod (person-swap, scail2-native, inpaint, kontext, qwen, outpaint, remove-bg)
AGENTS.md  ·  CLAUDE.md   # always-on (symlink)
```

## Como usar
**Com um agente** (recomendado): faça o pedido em linguagem natural ("crie um workflow para trocar a
pessoa de um vídeo", "qual GPU para 720p?", "deu OOM"). O `project-router` seleciona as skills e executa.

**Criar um projeto de workflow** (`workflows-cloud/<nome>/` self-hosted, ou `workflows-api/<nome>/` por API): a skill
`task-package-workflow-project` adapta um exemplo known-good e gera o trio `<nome>.json` + `README.md` + `setup.sh`. Cada
README abre com um **Card Informativo** (faz · técnica · GPU/VRAM **ou** custo/billing · entrada · saída · modelos · status)
e segue a mesma ordem de seções.

**Rodar um workflow no RunPod**:
1. Suba um pod ComfyUI (→ skill `task-launch-runpod-pod`).
2. No pod, rode o `setup.sh` do projeto como root (instala nodes + baixa modelos + o `.json`).
3. Abra o ComfyUI (porta 8188), carregue o workflow e siga o README do projeto.

**Rodar um bundle por API** (sem GPU): no ComfyUI local, rode o `setup.sh` do bundle (`workflows-api/<nome>/`) — instala o
nó fal + grava a `FAL_KEY` (de `~/ComfyUI/secrets.env`) + baixa os `.json`; faça login em comfy.org p/ os nós partner
(Kling/FluxVTON). A geração roda no provedor. Conhecimento: `knowledge-comfyui-api-nodes`.

## Projetos de workflow
> Legenda de status: 🟢 pronto · 🟡 rascunho a validar no pod. Cada projeto abre com um **Card Informativo**
> (faz · técnica · GPU/VRAM · entrada · saída · modelos · status) no topo do seu README.

### ☁️ Por API online — `workflows-api/` (sem GPU, paga por chamada)
| Projeto | O que faz | Provedores/Nós | Billing | Status |
|---|---|---|---|---|
| [`commercial-ondokai`](workflows-api/commercial-ondokai/) | Comercial de ~30s (9 cenas) com protagonista sintético consistente | Nano Banana Pro + Veo 3.1 + Kling + Seedance | fal + Comfy | 🟡 |
| [`mask-edit-cloud`](workflows-api/mask-edit-cloud/) | Edita uma região (máscara) na nuvem **ou** local e recola sem tocar o resto | `FluxPro1Fill_fal` + SAM/DINO local | fal / local | 🟡 |
| [`outfit-swap-api`](workflows-api/outfit-swap-api/) | Troca a roupa/look mantendo pose, rosto e fundo | `FluxVTONode` · `NanoBananaPro_fal` | Comfy / fal | 🟡 |

## 🖥️ Self-hosted em GPU — `workflows-cloud/` (RunPod)

### 🎬 Vídeo & Animação (SCAIL-2)
| Projeto | O que faz | Técnica | GPU/VRAM | Status |
|---|---|---|---|---|
| [`person-swap-scail2`](workflows-cloud/person-swap-scail2/) | Troca a pessoa de um vídeo por outra (a partir de 1 foto), preservando o movimento | SCAIL-2 Replacement (wrapper kijai) | 32–80 GB | 🟡 |
| [`scail2-native-3rdparty`](workflows-cloud/scail2-native-3rdparty/) | SCAIL-2 **nativo** (2 passos) + **CatVTON-Flux** clothing transfer. Original preservado em `scail2-native-3rdparty.json` | SCAIL-2 core + CatVTON-Flux + SegFormer | 24 GB+ | 🟡 |

### 🖼️ Edição de imagem
| Projeto | O que faz | Técnica | GPU/VRAM | Status |
|---|---|---|---|---|
| [`inpaint-region-cropstitch`](workflows-cloud/inpaint-region-cropstitch/) | Edita só uma região (máscara) e recola sem tocar o resto (+ scripts Python) | Flux Fill / SDXL-inpaint + Crop&Stitch | 16–24 GB | 🟡 |
| [`instruction-edit-kontext`](workflows-cloud/instruction-edit-kontext/) | Edita a imagem por instrução de texto, sem máscara | Flux.1 Kontext [dev] | ~16 GB | 🟡 |
| [`qwen-image-edit`](workflows-cloud/qwen-image-edit/) | Edição por instrução (objeto/fundo/texto na imagem), bilíngue | Qwen-Image-Edit 2511 | 16–24 GB | 🟡 |

### 🔭 Enquadramento & Fundo
| Projeto | O que faz | Técnica | GPU/VRAM | Status |
|---|---|---|---|---|
| [`outpaint-extend`](workflows-cloud/outpaint-extend/) | Estende o enquadramento (outpainting) | Flux.1 Fill [dev] | 16–24 GB | 🟡 |
| [`remove-background`](workflows-cloud/remove-background/) | Remove/troca o fundo (PNG com canal alpha) | RMBG / BiRefNet / BEN2 / SAM3 | Modesta | 🟢 |

## Memória evolutiva (e suas salvaguardas)
Skills de tarefa rodam um passo `<evolution>` ao concluir e registram aprendizados em `LEARNINGS.md`.
`meta-evolution` decide criar/atualizar/descartar skills; `meta-consolidation` faz GC periódico (dedup,
contradições, orçamento de tokens). **Toda mudança é um diff git para revisão humana** — conteúdo gerado
por LLM é rascunho até a curadoria. Só se persiste aprendizado de tarefa que passou nos critérios (estilo Voyager).

## Convenções e segurança
- **API online vs self-hosted:** `workflows-api/` (modelo roda no provedor; chaves em `~/ComfyUI/secrets.env`, **nunca** `~/.secrets`; ver `knowledge-comfyui-api-nodes`) · `workflows-cloud/` (você roda em GPU RunPod).
- Modelos vão em `ComfyUI/models/<subpasta>` no Network Volume (`/workspace`). ComfyUI na porta 8188.
- SCAIL-2/Wan destilado (LightX2V): **cfg=1**, 6–8 steps, shift 1; dims **÷32** (SCAIL-2). Itere em 480p, finalize em 720p.
- **Nunca** commitar tokens (`HF_TOKEN`, `CIVITAI_TOKEN`, `.env`). `setup.sh` lê tokens do ambiente, nunca embute.
- Pare o pod ao terminar (cobrança por segundo).

## Mapa de skills
Catálogo completo: [`.agents/skills/catalog.md`](.agents/skills/catalog.md). Convenções de autoria e o
mecanismo de evolução: skills `meta-evolution` e `meta-consolidation`.
