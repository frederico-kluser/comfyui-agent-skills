# person-swap-scail2 — Troca de pessoa em vídeo (SCAIL-2 Replacement)

Substitui uma **pessoa num vídeo** por **outra a partir de uma foto**, preservando o
movimento e a cena. Você anexa o **vídeo-condutor** + a **foto de referência**; o workflow
transfere a identidade da foto para a pessoa do vídeo (SCAIL-2 Replacement Mode).

- **Técnica:** SCAIL-2 (sobre Wan 2.1 14B) — ver conhecimento em `.agents/skills/knowledge-scail2`.
- **Base do grafo:** adaptado do exemplo oficial `wanvideo_2_1_14B_SCAIL_pose_control_example_01.json`
  (kijai/ComfyUI-WanVideoWrapper) — 68 nós, formato UI.

> ⚠️ **Status — rascunho a validar no pod.** O suporte do SCAIL-2 no ComfyUI ainda evolui
> (issue #2031) e **não há um workflow "oficial estável" único**. O grafo base é **pose-control**;
> a wiring exata do **Replacement** (máscara colorida + flag de replace) deve ser conferida ao
> abrir no ComfyUI. Trate este `.json` como ponto de partida curado, não como garantido runnable.

## Pré-requisitos
- **GPU/VRAM:** 480p → RTX 5090 (32GB, fp8); 720p → A100 80GB. Escolha/custo → `knowledge-runpod-infra`.
- **ComfyUI nightly/master** (o nó `Create SCAIL-2 Colored Mask` é **core**, não custom).
- **Network Volume** com os modelos (o `setup.sh` baixa). Pod → `task-launch-runpod-pod`.

## Setup (no RunPod, como root/admin)
Suba o `setup.sh` no pod (web terminal/JupyterLab) e rode:
```bash
# opcional: exporte tokens p/ modelos gated
export HF_TOKEN=...        # huggingface.co/settings/tokens (read)
export CIVITAI_TOKEN=...   # se precisar de LoRAs do CivitAI
bash setup.sh
```
Ele instala os custom nodes, garante o ComfyUI nightly, baixa os modelos SCAIL-2 nas pastas certas
(`aria2c -x16`) e coloca este workflow em `ComfyUI/user/default/workflows/`. Reinicie o ComfyUI
(Manager → Restart) e pressione `R` para recarregar os modelos.

Alternativa via template AI-Dock: hospede o `setup.sh` num Gist e use `PROVISIONING_SCRIPT=<raw_url>`
(detalhes em `knowledge-runpod-provisioning`).

## Como usar (no ComfyUI :8188)
1. **Carregue o workflow**: arraste `person-swap-scail2.json` para o canvas (ou Workflows → Open).
2. **Anexe os inputs**:
   - **Vídeo-condutor** → nó `VHS_LoadVideo` (suba o arquivo; ele vai para `ComfyUI/input/`).
   - **Foto de referência** → nó `LoadImage` (a identidade que vai substituir a pessoa do vídeo).
3. **Gere a máscara colorida** (obrigatória) marcando a pessoa a substituir: SAM 3.1
   (`Sam2Segmentation`/`SAM3_VideoTrack`) → `Create SCAIL-2 Colored Mask`. Convenção de cor:
   preto = fundo não aparece; branco = fundo aparece; cor = região do personagem ↔ movimento.
4. **Replacement vs Animation**: para **trocar a pessoa preservando a cena** (este caso), use
   **Replacement Mode** (máscara da região a substituir). Animation Mode coloca o personagem da
   foto numa cena nova.
5. **Parâmetros** (já nos defaults, ajuste se preciso): sampler **euler**, scheduler **simple**,
   **6–8 steps**, **cfg 1**, **shift 1**, dims **÷32** (832×480 base 480p), **≤81 frames**/passada.
   Vídeo longo → `WanVideoContextOptions` ou o nó `scail-auto-extend`.
6. **Rode** (`Ctrl+Enter`). Saída via `VHS_VideoCombine` (mp4). Para 30fps suave, interpole com RIFE.
7. **(Opcional) Refino facial**: CodeFormer/`facerestore_cf` ou ReActor para nitidez do rosto.

## Modelos (o `setup.sh` baixa — repo → arquivo → pasta)
| Componente | Repo HF → arquivo | Pasta |
|---|---|---|
| SCAIL-2 (difusão) | `Comfy-Org/SCAIL-2` → `diffusion_models/wan2.1_14B_SCAIL_2_fp8_scaled.safetensors` | `diffusion_models/` |
| DPO lora (mãos/rosto) | `Comfy-Org/SCAIL-2` → `loras/wan2.1_SCAIL_2_DPO_lora_bf16.safetensors` | `loras/` |
| LoRA aceleração | `lightx2v/...` → `Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors` | `loras/` |
| Text encoder | `Comfy-Org/Wan_2.1_ComfyUI_repackaged` → `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | `text_encoders/` |
| VAE | `…` → `wan_2.1_vae.safetensors` | `vae/` |
| CLIP Vision | `…` → `clip_vision_h.safetensors` | `clip_vision/` |
| SAM 3.1 (máscara) | `Comfy-Org/sam3.1` → `sam3.1_multiplex_fp16.safetensors` | `sam/` (+symlink `checkpoints/`) |
| Pose (NLF/ViTPose/Onnx) | **auto-download** pelos nós | — |

Manifesto completo e variações (GGUF, etc.) → `knowledge-runpod-provisioning`.

## Validação (faça antes de confiar)
- Carregar o `.json` **sem nós vermelhos**. Vermelho em `Create SCAIL-2 Colored Mask` = ComfyUI não
  está nightly → `git pull` em `$COMFY` + reiniciar. Outros vermelhos → Manager → "Install Missing Custom Nodes".
- Rodar um clipe **curto em 480p** primeiro (barato) e confirmar a troca de identidade preservando o movimento.
- Problemas (OOM, vídeo preto, máscara) → `.agents/skills/task-debug-generation`.

## Referências
- `.agents/skills/knowledge-scail2` (paths, parâmetros, máscara, gotchas) · `knowledge-comfyui-workflows` (grafo/nós)
- `.agents/skills/knowledge-runpod-provisioning` (modelos/script) · `knowledge-runpod-infra` (GPU/custo)
- `docs/SCAIL-2.md` · `docs/workflow-guide.md`
