# API Online vs Self-Hosted (RunPod)

Decisão de quando usar API (paga por chamada) vs alugar GPU (paga por segundo).

## API (`workflows-api/`) — use quando:
- Não quer/não pode alugar GPU.
- Quer o **melhor** modelo (Veo/Nano Banana Pro).
- Máquina fraca (8 GB) — a regra é *"nada de GGUF/quantizado/inferior local"*.
- Paga por chamada. A GPU local só faz **máscara (SAM/GroundingDINO), composição (`ImageCompositeMasked`) e upscale ESRGAN**.

## Self-hosted (`workflows-cloud/`) — use quando:
- Precisa de modelo **sem API** (SCAIL-2, Wan Animate em GPU).
- Volume alto previsível.
- Controle total de pesos/LoRA.
- Paga GPU/segundo → `knowledge-runpod-infra`.

## Princípio
*fal vs Comfy não decide qualidade — o MODELO decide.*

## Referências
- Rotas e credenciais → [routes-billing](routes-billing.md)
- GPU/custo → `knowledge-runpod-infra`
