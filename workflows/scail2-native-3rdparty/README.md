# scail2-native-3rdparty — SCAIL-2 nativo + CatVTON-Flux Clothing Transfer

> **Autoria de terceiros (comunidade).** O `scail2-native-3rdparty.json` foi **fornecido pelo usuário** e está
> **preservado sem edição** (grafo original intacto). Crédito a quem o montou.

**Dois pipelines complementares** para animação com SCAIL-2:

| Arquivo | O que faz |
|---------|-----------|
| `scail2-native-3rdparty.json` | **Original preservado** — SCAIL-2 nativo (troca/anima pessoa, máscara SAM3 por texto, toggle Replace) |
| `tryoff-preprocess.json` | **Pré-processamento** — extrai vestimenta de um frame do vídeo e aplica na foto de referência via CatVTON-Flux |
| `scail2-animation.json` | **Animação** — SCAIL-2 com referência processada (LoadImage → saída do tryoff, REPLACE=True) |

## Fluxo completo (2 passos)

```
Passo 1: tryoff-preprocess.json
  VHS_LoadVideo(frame 0) → Segformer (máscara da roupa) ──MASK──┐
  LoadImage (foto referência) ──IMAGE─────────────────────→ TryOffRunNode → SaveImage
                                                               ↑ pipe
  TryOffQuantizerNode(8Bit) → TryOffModelNode → TryOffFluxFillModelNode(FLUX.1-dev)
  Saída: reference_processed_*.png

Passo 2: scail2-animation.json
  LoadImage ← reference_processed_*.png
  VHS_LoadVideo (vídeo completo) → SAM3 → SCAIL2ColoredMask → WanSCAILToVideo → KSampler → RIFE → VideoCombine
  REPLACE=True | Saída: SCAIL-2_*.mp4 (32 fps)
```

> ⚠️ Rode os workflows **sequencialmente** (feche/recarregue o ComfyUI entre eles).
> GPU mínima: 24 GB (RTX 4090). Workflow único exigiria >35 GB.

## Pré-requisitos (tryoff)

| Requisito | Mínimo |
|-----------|--------|
| GPU VRAM | 24 GB (RTX 4090) — 32 GB+ recomendado |
| ComfyUI | 0.3.60+ nightly |
| CUDA | 12.4+ |
| Disco | ~100 GB livres |

### Custom nodes adicionais (instalados pelo setup.sh)
- **ComfyUI-Flux-TryOff** — nós TryOffQuantizerNode, TryOffModelNode, TryOffFluxFillModelNode, TryOffRunNode
- **ComfyUI_LayerStyle** — nó SegformerB2ClothesUltra (segmentação de roupa)
- **ComfyUI-VideoHelperSuite** — VHS_LoadVideo

### Modelos adicionais
| Modelo | Pasta | Tamanho |
|--------|-------|---------|
| cat-tryoff-flux (xiaozaa) | `models/cat-tryoff-flux/` | ~12 GB |
| FLUX.1-dev (Black Forest Labs) | `models/checkpoints/FLUX.1-dev/` | ~23 GB |
| SegFormer B2 Clothes (mattmdjaga) | `models/segformer_b2_clothes/` | ~1 GB |

## Setup (RunPod, root)
```bash
export HF_TOKEN=...
bash setup.sh
```
Instala **10 custom nodes** (7 originais + 3 tryoff), baixa **todos** os modelos (SCAIL-2 + CatVTON-Flux + SegFormer + FLUX.1-dev) e os 3 `.json`. Reinicie o ComfyUI.

## Como usar (:8188)

### Passo 1 — Clothing Transfer
1. Abra `tryoff-preprocess.json`.
2. **VHS_LoadVideo** (1): carregue o vídeo-condutor. `frame_load_cap=1` usa o primeiro frame.
3. **LoadImage** (3): carregue a foto da sambista (referência).
4. **SegformerB2ClothesUltra** (4): ative as categorias de roupa (upper_clothes, pants, dress).
5. Ajuste o **prompt** no TryOffRunNode (8) conforme o resultado desejado.
6. Execute. Saída: `output/reference_processed_*.png`.

### Passo 2 — SCAIL-2 Animation
1. **Feche/recarregue o ComfyUI** para liberar VRAM.
2. Abra `scail2-animation.json`.
3. **LoadImage** (58): carregue `reference_processed_00001_.png`.
4. **VHS_LoadVideo** (113): carregue o mesmo vídeo-condutor.
5. Escreva prompts positivo/negativo. Confira **REPLACE** = True.
6. Execute. Saída: `output/SCAIL-2_*.mp4`.

## Parâmetros do tryoff

### SegformerB2ClothesUltra — Refinamento da máscara
| Parâmetro | Default | Descrição |
|-----------|---------|-----------|
| 16 boolean toggles | upper/pants/dress=true | Categorias de roupa |
| `detail_erode` | 6 | Encolhe a máscara |
| `detail_dilate` | 6 | Expande a máscara |
| `black_point` / `white_point` | 0.3 / 0.95 | Threshold binário |

### TryOffRunNode
| Parâmetro | Default | Range |
|-----------|---------|-------|
| `num_steps` | 50 | 1–100 |
| `guidance_scale` | 30.0 | 1–100 |
| `width` × `height` | 768×1024 | 128–1024 |

### SCAIL-2 (workflow original)
Mantidos: `steps=6`, `cfg=1`, `shift=5`, `DURAÇÃO=81`. Ver `knowledge-scail2`.

## Troubleshooting

| Problema | Solução |
|----------|---------|
| OOM no workflow 1 | Mude Quantizer para `4Bit`; reduza resolução para 512×768 |
| Máscara não cobre toda a roupa | Ative mais toggles; aumente `detail_dilate` para 10–15 |
| Pele artificial/plástica | Reduza `guidance_scale` para 8–15; refine o prompt |
| SCAIL-2 regenera roupa | Mantenha REPLACE=True; teste DPO LoRA |
| FLUX.1-dev não baixa | `git clone https://huggingface.co/black-forest-labs/FLUX.1-dev $COMFY/models/checkpoints/FLUX.1-dev` |
| Nós vermelhos | Manager → Install Missing Custom Nodes |

## Limitações conhecidas
- **cat-tryoff-flux é treinado para try-OFF (remoção de roupa), não try-ON (aplicação).** Funciona bem para vídeo nu → referência nua. Resultado incerto para transferir fantasias complexas.
- Apenas **1 frame do vídeo** é usado como fonte da vestimenta.

## Modelos (SCAIL-2 original)
| Arquivo | Pasta |
|---|---|
| `wan2.1_14B_SCAIL_2_fp8_scaled.safetensors` (Comfy-Org/SCAIL-2) | `diffusion_models/` |
| `Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors` (lightx2v) | `loras/` |
| `umt5_xxl_fp8_e4m3fn_scaled.safetensors` (Comfy-Org/Wan_2.1_repackaged) | `text_encoders/` |
| `wan_2.1_vae.safetensors` | `vae/` |
| `clip_vision_h.safetensors` | `clip_vision/` |
| `sam3.1_multiplex_fp16.safetensors` (Comfy-Org/sam3.1) | `checkpoints/` |
| `rife49.pth` (vem com o Frame-Interpolation) | — |

## Referências
- `knowledge-scail2`, `knowledge-scail2-native`, `knowledge-comfyui-workflows`
- `knowledge-image-editing`, `knowledge-image-masking`
- [ComfyUI-Flux-TryOff](https://github.com/asutermo/ComfyUI-Flux-TryOff)
- [CatVTON-Flux](https://github.com/nftblackmagic/catvton-flux)
- [ComfyUI_LayerStyle](https://github.com/chflame163/ComfyUI_LayerStyle)
