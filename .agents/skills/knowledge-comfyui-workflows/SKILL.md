---
name: knowledge-comfyui-workflows
description: >-
  Conhecimento de construção de workflows no ComfyUI (foco vídeo): grafo de nós e tipos/cores de slot,
  os dois formatos JSON (UI vs API), a cadeia WanVideoWrapper (I2V/T2V), Context Windows para vídeo
  >81 frames, técnicas low-VRAM (block swap, fp8/GGUF, tiled VAE), organização (groups/subgraphs/get-set)
  e erros comuns. Use ao montar, adaptar, exportar ou entender qualquer workflow de vídeo/imagem — mesmo
  sem citar a skill. Não cobre os parâmetros específicos do SCAIL-2 (ver knowledge-scail2).
metadata:
  version: 0.2.0
  type: knowledge
---
# ComfyUI — Construção de Workflows (vídeo)

ComfyUI é programação visual procedural: nós = operações, fios = dados tipados. O grafo é um DAG executado
por dependência com cache (só re-roda nós cujas entradas mudaram).

## Quando usar
Montar/adaptar workflow, entender um JSON alheio, exportar para API, lidar com vídeo longo, otimizar VRAM,
organizar um grafo grande. Para diagnosticar falhas → `task-debug-generation`.

## Técnicas (um arquivo por técnica)

| Técnica | Arquivo | O que cobre |
|---------|---------|-------------|
| Fundamentos | [fundamentals.md](fundamentals.md) | Grafo, tipos de slot, KSampler, atalhos |
| Formatos JSON | [json-formats.md](json-formats.md) | UI/LiteGraph vs API/prompt, metadados |
| WanVideoWrapper | [wan-video-wrapper.md](wan-video-wrapper.md) | Cadeia I2V/T2V, sampler, prompt travel |
| Context Windows | [context-windows.md](context-windows.md) | Vídeo >81 frames, overlap, SCAIL Auto Extend |
| Low-VRAM | [low-vram.md](low-vram.md) | Block swap, fp8/GGUF, tiled VAE, LoRA aceleração |
| Organização | [organization.md](organization.md) | Groups, Get/Set, Subgraphs, Bypass vs Mute |
| API Automação | [api-automation.md](api-automation.md) | POST /prompt, WebSocket, /history, /view |
| Ficha de reprodução | [reproduction-sheet.md](reproduction-sheet.md) | O que registrar para reproduzir depois |

## Referências (nível 3, sob demanda)
- `docs/workflow-guide.md` — guia completo (nós, JSON detalhado, recursos 2026, links da comunidade).
- Cadeia: parâmetros SCAIL-2 → `knowledge-scail2`; erros → `task-debug-generation`; montar do zero → `task-build-workflow`.

## Evolução
Append em `LEARNINGS.md` quando descobrir um nó novo, um default que mudou, um padrão de organização que
funcionou, ou uma incompatibilidade. Destile no corpo se virar estável (`version++`). Diff git para revisão.
