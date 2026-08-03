---
name: knowledge-runpod-provisioning
description: >-
  Setup reproduzível do ComfyUI no RunPod para SCAIL-2/Wan/Flux: o provisioning.sh (padrão AI-Dock + aria2c
  -x16), o manifesto exato de modelos (repo HuggingFace → arquivo → pasta), a lista de custom nodes, o
  download automático de workflows e os caveats (SageAttention, ComfyUI nightly, HF_TOKEN, pasta do SAM).
  Use ao provisionar um pod, baixar/atualizar modelos, ou editar o script — mesmo sem citar a skill. Traz
  scripts/provisioning.sh pronto. Para escolher GPU/custo, veja knowledge-runpod-infra.
metadata:
  version: 0.2.0
  type: knowledge
---
# RunPod — Provisionamento (ComfyUI + modelos)

Setup automatizado e reproduzível. O artefato pronto é `scripts/provisioning.sh` (nesta skill): instala
custom nodes, baixa modelos nas pastas certas com `aria2c -x16 -s16` e baixa workflows.

## Quando usar
"Provisionar/subir o pod", "baixar os modelos", "instalar os custom nodes", "configurar o ComfyUI", editar/variar
o script (GGUF vs fp8, Wan 2.2 t2v, Flux com encoders separados).

## Técnicas (um arquivo por técnica)

| Técnica | Arquivo | O que cobre |
|---------|---------|-------------|
| Provisioning script | [provisioning-script.md](provisioning-script.md) | 3 caminhos (template, manual, one-liner) |
| Manifesto de modelos | [model-manifest.md](model-manifest.md) | Repo → arquivo → pasta, ~90GB total |
| Custom nodes | [custom-nodes.md](custom-nodes.md) | Lista de repos, core vs custom |
| Caveats | [caveats.md](caveats.md) | SageAttention, nightly, tokens, resolução, variar script |

## Referências (nível 3, sob demanda)
- `scripts/provisioning.sh` — script completo e editável (arrays `NODES`/`MODELS`/`WORKFLOWS`).
- `docs/config-runpod.md` — guia completo (estrutura AI-Dock, velocidade, SageAttention).
- Cadeia: subir o pod → `task-launch-runpod-pod`; GPU/custo → `knowledge-runpod-infra`.

## Evolução
Append em `LEARNINGS.md` quando um repo/arquivo/branch de modelo mudar (confira a aba *Files* do HF), quando um
node novo for necessário, ou quando um download falhar. Atualize `scripts/provisioning.sh` junto. Destile se
estável (`version++`). Diff git para revisão.
