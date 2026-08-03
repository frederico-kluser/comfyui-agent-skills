# Fundamentos do Grafo ComfyUI

ComfyUI é programação visual procedural: nós = operações, fios = dados tipados. O grafo é um DAG executado
por dependência com cache (só re-roda nós cujas entradas mudaram).

## Cadeia txt→imagem
Load Checkpoint (→MODEL/CLIP/VAE) → CLIP Text Encode (+/−) → Empty Latent → KSampler → VAE Decode → Save Image.

## Tipos de slot (cores)
Só conecta mesma cor: MODEL (lilás), CLIP (amarelo), VAE (vermelho), CONDITIONING (laranja), LATENT (rosa), IMAGE (azul), MASK (verde), CLIP_VISION.

## KSampler widgets_values
Lista **posicional**: `[seed, control_after_generate, steps, cfg, sampler_name, scheduler, denoise]`.

## Atalhos
`Ctrl+Enter` (queue), `Ctrl+B` (bypass), `Ctrl+M` (mute), `Ctrl+G` (group).

## Referências
- `docs/workflow-guide.md`
- Montar do zero → `task-build-workflow`
