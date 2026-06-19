# Catálogo de Skills — ComfyUI Commercials (RunPod)

> Índice operacional das skills deste repo (estilo llms.txt). O `project-router` e o
> `AGENTS.md` leem isto para despachar tarefas. O conhecimento detalhado fica em cada
> `SKILL.md` (nível 2) e nos docs em `docs/` (nível 3, sob demanda).
> Fonte única: `.agents/skills/` (symlink: `.claude/skills/`).
> Gerado/curado a partir de `docs/` por `huu_audit-and-improve-skills`.

## Roteador (sempre primeiro)
- **[project-router](project-router/SKILL.md)** — despacha TODA tarefa para a cadeia de skills certa antes de implementar.

## Conhecimento (memória semântica)
| Skill | O que injeta | Fonte |
|---|---|---|
| [knowledge-scail2](knowledge-scail2/SKILL.md) | SCAIL-2: paths de modelo, VRAM/quant, máscara, sampler, gotchas | `docs/SCAIL-2.md` |
| [knowledge-comfyui-workflows](knowledge-comfyui-workflows/SKILL.md) | grafo, JSON UI/API, cadeia WanVideoWrapper, low-VRAM, Context Windows | `docs/workflow-guide.md` |
| [knowledge-runpod-infra](knowledge-runpod-infra/SKILL.md) | tiers de GPU + preço, Pods/Serverless, Network Volume, custo | `docs/runpod-guide.md` |
| [knowledge-runpod-provisioning](knowledge-runpod-provisioning/SKILL.md) | `provisioning.sh`, manifesto de modelos, custom nodes, caveats | `docs/config-runpod.md` |
| [knowledge-image-editing](knowledge-image-editing/SKILL.md) | inpaint, edição por instrução (Kontext/Qwen), composição, modelos, otimização | `docs/image-editing.md` |
| [knowledge-image-masking](knowledge-image-masking/SKILL.md) | seleção/segmentação: MaskEditor, SAM2/3, Florence-2, Grounding DINO, Impact Pack | `docs/image-editing.md` |
| [knowledge-comfyui-api](knowledge-comfyui-api/SKILL.md) | API HTTP (/prompt,/upload,/history,/view) + composição Python (Pillow/NumPy/OpenCV) | `docs/image-editing.md` |
| [knowledge-image-enhance](knowledge-image-enhance/SKILL.md) | upscale, outpaint, relight (IC-Light), ControlNet, IPAdapter, remoção de fundo | `docs/image-editing.md` |
| [knowledge-scail2-native](knowledge-scail2-native/SKILL.md) | grafo NATIVO do SCAIL-2 (WanSCAILToVideo, SCAIL2ColoredMask, SAM3 por texto, toggle Replace, shift 5) | `workflows/scail2-native-3rdparty/` |

## Tarefa (memória procedural)
| Skill | O que faz |
|---|---|
| [task-create-commercial](task-create-commercial/SKILL.md) | pipeline end-to-end de um comercial (Flux→SCAIL-2/Wan→RIFE→upscale→edição) |
| [task-launch-runpod-pod](task-launch-runpod-pod/SKILL.md) | subir um pod ComfyUI pronto para gerar |
| [task-build-workflow](task-build-workflow/SKILL.md) | montar/adaptar um workflow de vídeo |
| [task-debug-generation](task-debug-generation/SKILL.md) | diagnosticar falhas (OOM, vídeo preto, nós vermelhos) |
| [task-package-workflow-project](task-package-workflow-project/SKILL.md) | empacotar um workflow entregável em `workflows/<nome>/` (json + README + setup.sh) |
| [task-edit-image](task-edit-image/SKILL.md) | editar uma imagem fim-a-fim (selecionar → editar → recolar) |

## Meta (auto-evolução)
| Skill | O que faz |
|---|---|
| [meta-evolution](meta-evolution/SKILL.md) | atualiza/cria/descarta skills (diff git, revisão humana, anti-poisoning) |
| [meta-consolidation](meta-consolidation/SKILL.md) | GC periódico: dedup, contradições, versionamento temporal, orçamento de tokens |

## Cadeias típicas (para o router)
| Pedido do usuário | Cadeia de skills |
|---|---|
| "criar/produzir um comercial" | `task-create-commercial` → `knowledge-scail2` + `knowledge-comfyui-workflows` (+ `task-launch-runpod-pod`) |
| "qual GPU / quanto custa / Pod ou Serverless" | `knowledge-runpod-infra` |
| "subir o pod / baixar os modelos / configurar" | `task-launch-runpod-pod` → `knowledge-runpod-provisioning` + `knowledge-runpod-infra` |
| "montar/adaptar um workflow" | `task-build-workflow` → `knowledge-comfyui-workflows` (+ `knowledge-scail2`) |
| "deu OOM / vídeo preto / nó vermelho / não gera" | `task-debug-generation` → `knowledge-comfyui-workflows` |
| "animar personagem com SCAIL-2" | `knowledge-scail2` + `knowledge-comfyui-workflows` |
| "criar um workflow para X / empacotar workflow" | `task-package-workflow-project` → `task-build-workflow` + knowledge da técnica |
| "editar/retocar imagem, trocar objeto/cor/fundo" | `task-edit-image` → `knowledge-image-editing` + `knowledge-image-masking` |
| "editar por instrução (sem máscara)" | `knowledge-image-editing` (projetos `instruction-edit-kontext` / `qwen-image-edit`) |
| "automatizar por API / recolar via código" | `knowledge-comfyui-api` |
| "upscale / outpaint / relight / tirar fundo" | `knowledge-image-enhance` |
| nenhuma skill cobre | `meta-evolution` (propor skill nova) |
