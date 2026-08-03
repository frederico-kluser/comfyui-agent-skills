# RunPod — Árvore de Decisão de GPU

Qual GPU alugar para cada tipo de projeto.

## Decisão rápida
- Só imagem (SDXL/Flux): **RTX 4090**.
- Vídeo 480p barato (fp8/GGUF): **RTX 5090** (US$0,99/h). Mais barato ainda: 4090 com GGUF.
- Vídeo 720p estável no 14B: **A100 80GB** (US$1,49/h); **H100** se quiser ~2× velocidade.
- Clipes 10s+/multi-personagem 720p: **H200** (sair de 5s→10s 720p passa de 80GB).
- Produção/API que escala a zero: **Serverless** (worker-comfyui).

## Maior alavanca de custo
**Itere em 480p, finalize em 720p** — 480p ~2–3× mais barato por iteração.

## Tempos estimados (SCAIL-2 LightX2V 6–8 steps)
~1–3 min/5s 480p na 4090/5090 (estimativa — sem benchmark oficial; valide no seu pod).

## Referências
- `docs/runpod-guide.md`
- Preços → [gpu-pricing](gpu-pricing.md)
- Provisionar → `task-launch-runpod-pod`
