---
name: knowledge-scail2
description: >-
  Conhecimento operacional do SCAIL-2 (animação de personagem end-to-end sobre Wan 2.1 14B):
  arquivos e paths exatos de modelo, variantes e VRAM (fp8/GGUF), a máscara colorida obrigatória,
  modos Animation/Replacement, parâmetros do sampler (euler/simple, 6–8 steps, cfg 1, shift 1,
  81 frames) e gotchas. Use ao gerar/animar com SCAIL-2, escolher quantização ou debugar
  máscara/qualidade — mesmo sem citar a skill. Não cobre infra/preço de GPU (ver knowledge-runpod-infra).
metadata:
  version: 0.2.0
  type: knowledge
---
# SCAIL-2 — Geração e Animação de Personagem

SCAIL-2 (zai-org, jun/2026; backbone Wan 2.1-14B-I2V) anima uma imagem de referência a partir de um
vídeo-condutor **sem mapas de esqueleto** — suporta single/multi-personagem, substituição e motion de
animais. Roda no ComfyUI (caminho nativo Comfy-Org ou wrapper Kijai).

## Quando usar
Pedidos de "animar personagem/pessoa", "transferir movimento", "substituir personagem", "SCAIL-2",
problemas de máscara/dedos/rosto, ou escolha de quantização para caber na VRAM.

## Técnicas (um arquivo por técnica)

| Técnica | Arquivo | O que cobre |
|---------|---------|-------------|
| Arquivos de modelo | [model-files.md](model-files.md) | Paths, repos, estrutura de diretórios |
| Quantização (VRAM) | [quantization.md](quantization.md) | fp8/GGUF/Q8/fp16 — qual usar com cada GPU |
| Máscara colorida | [colored-mask.md](colored-mask.md) | Convenção de cores, SAM3_VideoTrack, nó core |
| Parâmetros | [parameters.md](parameters.md) | Sampler, frames, resolução, prompts |
| Gotchas | [gotchas.md](gotchas.md) | Warnings inofensivos, degradação, overhead |

## Referências (nível 3, sob demanda)
- `docs/SCAIL-2.md` — guia completo (arquitetura, comparações, workflows da comunidade).
- Cadeia: montar o grafo → `knowledge-comfyui-workflows`; baixar os modelos → `knowledge-runpod-provisioning`.
- Grafo nativo → `knowledge-scail2-native`

## Evolução
Ao descobrir um parâmetro melhor, um path/arquivo novo, um gotcha ou uma correção do usuário: append em
`LEARNINGS.md` (data + fonte: usuário > inferência) e, se virar padrão estável, destile no corpo acima
(incremente `version`). Só persista o que NÃO é óbvio nem volátil. Mudança = diff git para revisão humana.
