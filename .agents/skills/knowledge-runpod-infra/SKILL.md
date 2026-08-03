---
name: knowledge-runpod-infra
description: >-
  Conhecimento de infraestrutura RunPod para vídeo/imagem IA: tiers de GPU com preço (jun/2026),
  Pods vs Serverless, Secure vs Community Cloud, Network Volume, mapa modelo→VRAM→GPU, árvore de decisão
  de GPU, tempos de geração e otimização de custo. Use para escolher GPU, estimar custo, decidir storage,
  ou planejar produção — mesmo sem citar a skill. Para o script de setup e o manifesto de modelos, veja
  knowledge-runpod-provisioning.
metadata:
  version: 0.2.0
  type: knowledge
---
# RunPod — Infraestrutura, GPU e Custo

RunPod cobra **por segundo**. Três produtos: **Pods** (GPU dedicada interativa — use p/ ComfyUI), **Serverless**
(API que escala a zero — use p/ produção/automação), Clusters (multi-nó).

## Quando usar
"Qual GPU uso?", "quanto custa?", "Pod ou Serverless?", "preciso de Network Volume?", planejar orçamento de um
projeto, decidir Secure vs Community, ou quando subir de tier (480p→720p).

## Técnicas (um arquivo por técnica)

| Técnica | Arquivo | O que cobre |
|---------|---------|-------------|
| GPUs e preços | [gpu-pricing.md](gpu-pricing.md) | Tiers, preços on-demand, Community Cloud, Spot |
| Modelo→VRAM→GPU | [model-vram-gpu.md](model-vram-gpu.md) | Mapa de qual GPU para cada modelo/resolução |
| Árvore de decisão | [decision-tree.md](decision-tree.md) | Qual GPU alugar, 480p vs 720p, Serverless |
| Volume e custo | [network-volume-cost.md](network-volume-cost.md) | Network Volume, disciplina, fórmula de custo, caveats |

## Referências (nível 3, sob demanda)
- `docs/runpod-guide.md` — guia completo (Serverless, tabela cheia, troubleshooting).
- Cadeia: setup passo a passo do pod → `task-launch-runpod-pod`; script/modelos → `knowledge-runpod-provisioning`.

## Evolução
Append em `LEARNINGS.md` quando preços/tiers mudarem, quando medir um tempo real de geração no seu pod, ou
quando uma GPU/região se mostrar melhor. Destile se virar estável (`version++`). Diff git para revisão.
