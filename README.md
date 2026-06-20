# ComfyUI Commercials — RunPod Ops & Agent Skills

Base de conhecimento + sistema de **Agent Skills** para autorar **workflows de vídeo e de edição de
imagem IA** (SCAIL-2, Wan 2.1/2.2, Flux, Flux Fill/Kontext, Qwen-Image-Edit, SAM/inpaint) no **ComfyUI**
e empacotá-los como **bundles prontos para o RunPod.io**.

Não é um app: o valor está (1) na pesquisa curada em `docs/`, (2) nas skills em `.agents/skills/` que
injetam esse conhecimento sob demanda, e (3) nos **projetos de workflow** entregáveis em `workflows/`.

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
  task-*/                 #   tarefas (create-commercial, build-workflow, launch-pod, debug,
                          #            package-workflow-project, edit-image)
  meta-*/                 #   evolução e consolidação
workflows/                # PROJETOS de workflow entregáveis (1 pasta por projeto)
  person-swap-scail2/     #   ex.: troca de pessoa em vídeo (SCAIL-2) — json + README + setup.sh
AGENTS.md  ·  CLAUDE.md   # always-on (symlink)
```

## Como usar
**Com um agente** (recomendado): faça o pedido em linguagem natural ("crie um workflow para trocar a
pessoa de um vídeo", "qual GPU para 720p?", "deu OOM"). O `project-router` seleciona as skills e executa.

**Criar um projeto de workflow** (`workflows/<nome>/`): a skill `task-package-workflow-project` adapta um
exemplo known-good e gera o trio `<nome>.json` + `README.md` + `setup.sh`. Cada projeto tem seu próprio README.

**Rodar um workflow no RunPod**:
1. Suba um pod ComfyUI (→ skill `task-launch-runpod-pod`).
2. No pod, rode o `setup.sh` do projeto como root (instala nodes + baixa modelos + o `.json`).
3. Abra o ComfyUI (porta 8188), carregue o workflow e siga o README do projeto.

## Projetos de workflow
| Projeto | O que faz | Técnica |
|---|---|---|
| [`person-swap-scail2`](workflows/person-swap-scail2/) | Substitui uma pessoa num vídeo por outra a partir de uma foto | SCAIL-2 Replacement (wrapper kijai) |
| [`scail2-native-3rdparty`](workflows/scail2-native-3rdparty/) | SCAIL-2 **nativo** (workflow de terceiros) + **CatVTON-Flux** clothing transfer (2 passos: tryoff-preprocess → scail2-animation). Original preservado em `scail2-native-3rdparty.json` | SCAIL-2 nativo (core) + CatVTON-Flux + SegFormer |
| [`inpaint-region-cropstitch`](workflows/inpaint-region-cropstitch/) | Edita só uma região da imagem e recola (inpaint + Crop&Stitch) + scripts Python | Flux Fill / SDXL-inpaint |
| [`instruction-edit-kontext`](workflows/instruction-edit-kontext/) | Edita a imagem por instrução de texto, sem máscara | Flux Kontext |
| [`qwen-image-edit`](workflows/qwen-image-edit/) | Edição por instrução (objeto/fundo/texto na imagem), bilíngue | Qwen-Image-Edit 2511 |
| [`outpaint-extend`](workflows/outpaint-extend/) | Estende o enquadramento (outpainting) | Flux Fill |
| [`remove-background`](workflows/remove-background/) | Remove/troca o fundo (alpha transparente) | RMBG / BiRefNet / SAM3 |

## Memória evolutiva (e suas salvaguardas)
Skills de tarefa rodam um passo `<evolution>` ao concluir e registram aprendizados em `LEARNINGS.md`.
`meta-evolution` decide criar/atualizar/descartar skills; `meta-consolidation` faz GC periódico (dedup,
contradições, orçamento de tokens). **Toda mudança é um diff git para revisão humana** — conteúdo gerado
por LLM é rascunho até a curadoria. Só se persiste aprendizado de tarefa que passou nos critérios (estilo Voyager).

## Convenções e segurança
- Modelos vão em `ComfyUI/models/<subpasta>` no Network Volume (`/workspace`). ComfyUI na porta 8188.
- SCAIL-2/Wan destilado (LightX2V): **cfg=1**, 6–8 steps, shift 1; dims **÷32** (SCAIL-2). Itere em 480p, finalize em 720p.
- **Nunca** commitar tokens (`HF_TOKEN`, `CIVITAI_TOKEN`, `.env`). `setup.sh` lê tokens do ambiente, nunca embute.
- Pare o pod ao terminar (cobrança por segundo).

## Mapa de skills
Catálogo completo: [`.agents/skills/catalog.md`](.agents/skills/catalog.md). Convenções de autoria e o
mecanismo de evolução: skills `meta-evolution` e `meta-consolidation`.
