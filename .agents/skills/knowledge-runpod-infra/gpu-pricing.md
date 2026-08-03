# RunPod — GPUs e Preços

RunPod cobra **por segundo**. Três produtos: **Pods** (GPU dedicada interativa — use p/ ComfyUI), **Serverless**
(API que escala a zero — use p/ produção/automação), Clusters (multi-nó).

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

**Community Cloud** ~10–30% mais barato (sem Network Volume).
**Spot/Interruptible** 50–70% mais barato (pode ser recuperado, SIGTERM ~5s).

## Referências
- Preços flutuam por região — confirme em runpod.io/pricing.
- Árvore de decisão → [decision-tree](decision-tree.md)
