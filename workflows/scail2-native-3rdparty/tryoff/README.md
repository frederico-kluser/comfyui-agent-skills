# scail2-native-3rdparty/tryoff — Clothing Transfer + SCAIL-2 Animation

> **Pipeline em 2 passos:** (1) extrai a vestimenta de um frame do vídeo-condutor e aplica à foto de
> referência via CatVTON-Flux, (2) anima o resultado via SCAIL-2 nativo. Objetivo artístico/cultural
> (Carnaval).

Workflows separados resolvem o problema de VRAM: CatVTON-Flux + FLUX.1-dev (~20 GB 8-bit) e SCAIL-2
(~17.7 GB fp8) não cabem simultaneamente em GPUs de 24 GB.

## O que faz

### Workflow 1 — `tryoff-preprocess.json` (Clothing Transfer)

```
VHS_LoadVideo (frame 0) → ImageFromBatch → SegformerB2ClothesUltra ──MASK (roupa do vídeo)──┐
LoadImage (foto referência) ──────────────IMAGE─────────────────────────────────────────→ TryOffRunNode
                                                                                             │
TryOffQuantizerNode (8Bit) → TryOffModelNode (cat-tryoff-flux) → TryOffFluxFillModelNode (FLUX.1-dev)
                                                                                             │
                                                                                          pipe
                                                                                             ↓
                                                    tryoff_image (slot 1) ──→ SaveImage (reference_processed_*.png)
```

1. **VHS_LoadVideo** carrega o vídeo-condutor com `frame_load_cap=1` (apenas o primeiro frame)
2. **SegformerB2ClothesUltra** segmenta automaticamente a roupa presente nesse frame (16 categorias configuráveis)
3. **TryOffRunNode** recebe a foto de referência (`image_in`) + a máscara de roupa do vídeo (`mask_in`) + o pipeline Flux Fill (`pipe`)
4. O modelo cat-tryoff-flux preenche a região mascarada na foto de referência, adotando a aparência do vídeo
5. **SaveImage** salva o resultado como `reference_processed_*.png`

### Workflow 2 — `scail2-animation.json` (SCAIL-2)

Workflow SCAIL-2 nativo original (63 nós, 3 grupos), com:
- **LoadImage** apontando para `reference_processed_00001_.png` (saída do workflow 1)
- **REPLACE=True** por padrão (substitui a pessoa do vídeo pela referência processada)
- Restante do pipeline intacto: SAM3 tracking, SCAIL2ColoredMask, WanSCAILToVideo, KSampler, RIFE, VideoCombine

## Pré-requisitos

| Requisito | Mínimo | Recomendado |
|-----------|--------|-------------|
| GPU VRAM | 24 GB (RTX 4090) | 32 GB+ (RTX 5090) |
| ComfyUI | 0.3.60+ nightly | master (mais recente) |
| CUDA | 12.4+ | 12.8+ |
| PyTorch | 2.5+ | 2.6+ |
| Disco | ~100 GB livres | ~150 GB |

**⚠️ 24 GB é apertado.** O workflow 1 carrega cat-tryoff-flux (~8 GB 8-bit) + FLUX.1-dev (~12 GB fp8). O workflow 2 carrega SCAIL-2 fp8 (~17.7 GB). Rode-os **sequencialmente** (feche/recarregue o ComfyUI entre eles para liberar VRAM).

## Setup (RunPod, root)

```bash
export HF_TOKEN=hf_...
bash setup.sh
```

Instala 9 custom nodes, baixa modelos SCAIL-2 + CatVTON-Flux + SegFormer + FLUX.1-dev, e ambos os workflows. Reinicie o ComfyUI após.

## Como usar (:8188)

### Passo 1 — Clothing Transfer

1. Abra `tryoff-preprocess.json` no ComfyUI.
2. No nó **VHS_LoadVideo** (1), carregue o vídeo-condutor (ex: dançarino de Carnaval).
   - `frame_load_cap=1` carrega só o primeiro frame. Para usar outro frame, aumente o cap e ajuste `skip_first_frames`.
3. No nó **LoadImage** (3), carregue a foto de referência (sambista).
4. No nó **SegformerB2ClothesUltra** (4), configure as categorias de roupa a extrair do vídeo:
   - `upper_clothes` = ☑ (camisa/blusa/top)
   - `pants` = ☑ (calça/shorts)
   - `dress` = ☑ (vestido/saia)
   - Desmarque `face`, `hair`, `left_arm`, `right_arm` para não incluir pele/rosto na máscara
5. Ajuste o **prompt** no TryOffRunNode (8) conforme o resultado desejado.
6. Execute (Ctrl+Enter). Saída em `output/reference_processed_*.png`.

### Passo 2 — SCAIL-2 Animation

1. **Feche/recarregue o ComfyUI** para liberar VRAM (Ctrl+Shift+R no navegador).
2. Abra `scail2-animation.json`.
3. No nó **LoadImage** (58), carregue `reference_processed_00001_.png` (saída do passo 1).
4. No nó **VHS_LoadVideo** (113), carregue o mesmo vídeo-condutor.
5. Escreva os prompts positivo/negativo (nós 6 e 7) descrevendo o movimento e a cena.
6. Confira **REPLACE** (nó 172) = **True**.
7. Execute. Saída em `output/SCAIL-2_*.mp4` (32 fps, RIFE ×2).

## Parâmetros

### SegformerB2ClothesUltra — Refinamento da máscara

| Parâmetro | Default | Descrição |
|-----------|---------|-----------|
| 16 boolean toggles | upper/pants/dress=true | Categorias de roupa a segmentar |
| `detail_erode` | 6 | Encolhe a máscara (use se estiver invadindo pele) |
| `detail_dilate` | 6 | Expande a máscara (use se não cobrir toda a roupa) |
| `black_point` | 0.3 | Threshold mínimo (aumente para máscara mais restritiva) |
| `white_point` | 0.95 | Threshold máximo (diminua para incluir áreas incertas) |

### TryOffRunNode — Geração

| Parâmetro | Default | Range | Nota |
|-----------|---------|-------|------|
| `num_steps` | 50 | 1–100 | 30 para teste rápido, 50 para qualidade |
| `guidance_scale` | 30.0 | 1–100 | Reduza para 8–15 se a pele ficar artificial |
| `width` × `height` | 768×1024 | 128–1024 (step 16) | Resolução da saída |
| `seed` | 42 | — | Fixe para reprodutibilidade |

### SCAIL-2 (workflow 2)

| Parâmetro | Default | Nota |
|-----------|---------|------|
| KSampler `steps` | 6 | Canônico para lightx2v |
| KSampler `cfg` | 1.0 | Destilado; >1 borra |
| `shift` | 5 | Otimizado para SCAIL-2 |
| `REPLACE` | True | Substitui pessoa no vídeo |
| `DURAÇÃO (FRAMES)` | 81 | Máximo por passada |
| SAM3 prompt | "human" | Texto para rastrear a pessoa |

## Troubleshooting

| Problema | Causa provável | Solução |
|----------|---------------|---------|
| OOM no workflow 1 | FLUX.1-dev + cat-tryoff-flux > VRAM | Mude TryOffQuantizerNode para `4Bit`; reduza width/height para 512×768 |
| Máscara não cobre a roupa do vídeo | Categorias insuficientes | Ative mais toggles (skirt, belt, shoe); aumente `detail_dilate` para 10–15 |
| Máscara cobre rosto/mãos | Segformer confundiu pele com roupa | Aumente `detail_erode` para 10; diminua `white_point` para 0.85 |
| Pele parece artificial/plástica | `guidance_scale` muito alto | Reduza para 8–15; refine o prompt com tons de pele específicos |
| Imagem gerada não parece com a referência | Máscara muito grande ou prompt ruim | Ajuste a máscara para cobrir APENAS a roupa; refine o prompt |
| SCAIL-2 regenera roupa sobre pele | Modelo treinado com referências vestidas | Mantenha REPLACE=True; teste com DPO LoRA (`wan2.1_SCAIL_2_DPO_lora_bf16.safetensors`) |
| FLUX.1-dev não baixa | Timeout no download automático | `git clone https://huggingface.co/black-forest-labs/FLUX.1-dev $COMFY/models/checkpoints/FLUX.1-dev` |
| Nós vermelhos (TryOff*) | ComfyUI-Flux-TryOff não instalado | Manager → Install Missing Custom Nodes |
| Nós SCAIL-2 core vermelhos | ComfyUI não é nightly | `cd $COMFY && git pull` + reiniciar |
| VHS_LoadVideo ausente | VideoHelperSuite não instalado | Manager → Install Missing Custom Nodes |

## Modelos

### Workflow 1 — TryOff
| Arquivo | Pasta | Tamanho |
|---------|-------|---------|
| cat-tryoff-flux (xiaozaa) | `models/cat-tryoff-flux/` | ~12 GB |
| FLUX.1-dev (Black Forest Labs) | `models/checkpoints/FLUX.1-dev/` | ~23 GB |
| SegFormer B2 Clothes (mattmdjaga) | `models/segformer_b2_clothes/` | ~1 GB |

### Workflow 2 — SCAIL-2
| Arquivo | Pasta | Tamanho |
|---------|-------|---------|
| `wan2.1_14B_SCAIL_2_fp8_scaled.safetensors` | `diffusion_models/` | ~17.7 GB |
| `Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors` | `loras/` | ~1.2 GB |
| `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | `text_encoders/` | ~6 GB |
| `wan_2.1_vae.safetensors` | `vae/` | ~0.5 GB |
| `clip_vision_h.safetensors` | `clip_vision/` | ~0.5 GB |
| `sam3.1_multiplex_fp16.safetensors` | `checkpoints/` | ~4 GB |

## Limitações conhecidas

- **cat-tryoff-flux é treinado para remoção de roupa (try-off), não aplicação (try-on).** O resultado depende da qualidade da máscara e do prompt. Para aplicar vestimentas complexas (fantasias com brilho, penas, adereços), o modelo pode não transferir fielmente os detalhes do tecido.
- **Apenas 1 frame do vídeo é usado** como fonte da vestimenta. Se o vídeo tem variação de roupa (ex: close-up vs plano aberto), escolha o frame mais representativo.
- **VRAM:** mesmo com workflows separados, 24 GB é o mínimo. Em GPUs menores, use quantização 4Bit e resolução reduzida.

## Referências

- `knowledge-scail2` — parâmetros e modelos do SCAIL-2
- `knowledge-scail2-native` — grafo nativo (Set/Get, SAM3, máscara colorida)
- `knowledge-comfyui-workflows` — construção de workflows
- `knowledge-image-editing` — técnicas de inpainting
- `knowledge-image-masking` — segmentação (SegFormer, SAM3)
- `knowledge-runpod-provisioning` — provisioning script base
- [ComfyUI-Flux-TryOff](https://github.com/asutermo/ComfyUI-Flux-TryOff) — custom node
- [CatVTON-Flux](https://github.com/nftblackmagic/catvton-flux) — modelo original
- [ComfyUI_LayerStyle](https://github.com/chflame163/ComfyUI_LayerStyle) — SegFormer node
