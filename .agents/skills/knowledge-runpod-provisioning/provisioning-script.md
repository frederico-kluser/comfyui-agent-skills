# RunPod — Provisioning Script

Setup automatizado e reproduzível. O artefato pronto é `scripts/provisioning.sh` (nesta skill): instala
custom nodes, baixa modelos nas pastas certas com `aria2c -x16 -s16` e baixa workflows.

## Como rodar (3 caminhos)

### 1. Template (recomendado)
Hospede `scripts/provisioning.sh` num Gist público; no template AI-Dock/ComfyUI defina:
- `PROVISIONING_SCRIPT=<raw_url>`
- `HF_TOKEN`, `CIVITAI_TOKEN`
- `COMFYUI_ARGS=--fast`
- Volume ≥200GB, container ≥30GB, CUDA 12.8.

### 2. Manual
Web terminal/JupyterLab → `wget <raw_url> -O provisioning.sh && bash provisioning.sh`.

### 3. One-liner
Geradores tipo `deploy.promptingpixels.com`.

## Referências
- `scripts/provisioning.sh` — script completo e editável (arrays `NODES`/`MODELS`/`WORKFLOWS`).
- `docs/config-runpod.md`
- Manifesto de modelos → [model-manifest](model-manifest.md)
