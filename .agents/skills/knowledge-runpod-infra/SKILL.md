---
name: knowledge-runpod-infra
description: >-
  Conhecimento de infraestrutura RunPod para vídeo/imagem IA: tiers de GPU com preço (jun/2026),
  Pods vs Serverless, Secure vs Community Cloud, Network Volume, mapa modelo→VRAM→GPU, árvore de decisão
  de GPU, tempos de geração e otimização de custo. Use para escolher GPU, estimar custo, decidir storage,
  ou planejar produção — mesmo sem citar a skill. Para o script de setup e o manifesto de modelos, veja
  knowledge-runpod-provisioning.
metadata:
  version: 0.1.0
  type: knowledge
---
# RunPod — Infraestrutura, GPU e Custo

RunPod cobra **por segundo**. Três produtos: **Pods** (GPU dedicada interativa — use p/ ComfyUI), **Serverless**
(API que escala a zero — use p/ produção/automação), Clusters (multi-nó).

## Quando usar
"Qual GPU uso?", "quanto custa?", "Pod ou Serverless?", "preciso de Network Volume?", planejar orçamento de um
projeto, decidir Secure vs Community, ou quando subir de tier (480p→720p).

## Preços On-Demand (Secure Cloud, jun/2026)
| GPU | VRAM | US$/h | Uso para Wan/SCAIL-2 14B |
|---|---|---|---|
| RTX 4090 | 24 | 0,69 | 480p OK (fp8/GGUF); **não roda 720p no 14B** |
| RTX 5090 | 32 | 0,99 | **Melhor custo-benefício 480p**; ~2× a 4090 |
| A40 / A6000 | 48 | 0,44 / 0,49 | folga de VRAM, mais lenta |
| L40S | 48 | 0,86 | throughput médio |
| A100 PCIe / SXM | 80 | 1,39 / 1,49 | **ponto doce p/ 720p** + clipes longos |
| H100 PCIe | 80 | 2,89 | 720p rápido (~2× A100) |
| H200 | 141 | 4,39 | clipes 10s+/multi-personagem 720p sem OOM |
| B200 | 180 | 5,89 | topo |
Community Cloud ~10–30% mais barato (sem Network Volume). Spot/Interruptible 50–70% mais barato (pode ser
recuperado, SIGTERM ~5s).

## Modelo → VRAM → GPU
| Modelo | full | fp8 | GGUF | GPU recomendada |
|---|---|---|---|---|
| Flux.1 dev | ~24 | ~12–16 | Q4 6–8 / Q8 12–13 | RTX 4090 |
| Wan/SCAIL-2 14B **480p** | ~54–65 | ~16–24 | 6–17 | **RTX 5090** (fp8/GGUF) |
| Wan/SCAIL-2 14B **720p** | ~65–80 | ~40–50 | — | **A100 80GB** / H100 / H200 |
- fp8: ~mesma qualidade, −20–40% VRAM. GGUF: cabe em GPU menor, +10–30% tempo. bf16/fp16: só com VRAM sobrando.

## Árvore de decisão
- Só imagem (SDXL/Flux): **RTX 4090**.
- Vídeo 480p barato (fp8/GGUF): **RTX 5090** (US$0,99/h). Mais barato ainda: 4090.
- Vídeo 720p estável no 14B: **A100 80GB** (US$1,49/h); **H100** se quiser ~2× velocidade.
- Clipes 10s+/multi-personagem 720p: **H200** (sair de 5s→10s 720p passa de 80GB).
- Produção/API que escala a zero: **Serverless** (worker-comfyui).

## Network Volume (essencial)
Só na **Secure Cloud**. Persiste modelos/saídas entre pods (boot de minutos→segundos). ~US$0,07/GB/mês
(100GB ≈ US$7/mês). Sugestão: **150–200GB** p/ vídeo. Travado por região — crie na região da GPU que vai usar.

## Custo de projeto
Custo ≈ (tempo/clipe em h) × (US$/h) × (nº de clipes + iterações) + storage. Ex.: 50 clipes 720p Wan 14B
~9min na A100 ≈ 50×0,15h×1,49 ≈ **US$11**. **Maior alavanca: itere em 480p, finalize em 720p** (480p ~2–3×
mais barato por iteração). SCAIL-2 com LightX2V 6–8 steps: ~1–3 min/5s 480p na 4090/5090 (estimativa — sem
benchmark oficial; valide no seu pod).

## Disciplina de custo
- **Pare o pod** ao terminar (cobra por segundo). Volume Disk parado cobra **em dobro** — guarde tudo no Network Volume.
- **Terminate** apaga container/volume efêmero (perde o que não está no Network Volume).
- Sem egress fees (baixar/subir renders é grátis). **Um job de vídeo por GPU** (vídeo não faz batch como imagem → OOM).

## Caveats
- Preços flutuam por região/disponibilidade — confirme em runpod.io/pricing.
- CUDA **12.8** obrigatório p/ Blackwell (RTX 5090/B200) → template "ComfyUI Blackwell Edition".
- "Zero GPUs on restart": GPU esgotada na região ao religar pod parado → tente outra região (modelos no
  Network Volume recriam rápido).

## Referências (nível 3, sob demanda)
- `docs/runpod-guide.md` — guia completo (Serverless, tabela cheia, troubleshooting).
- Cadeia: setup passo a passo do pod → `task-launch-runpod-pod`; script/modelos → `knowledge-runpod-provisioning`.

## Evolução
Append em `LEARNINGS.md` quando preços/tiers mudarem, quando medir um tempo real de geração no seu pod, ou
quando uma GPU/região se mostrar melhor. Destile se virar estável (`version++`). Diff git para revisão.
