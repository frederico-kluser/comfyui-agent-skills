# mask-edit-cloud — Editar uma região por máscara (nuvem fal OU local), recolando sem tocar o resto

> Seleciona uma região (por **texto**, ex.: *"a camisa"*), edita **só ela** (inpaint na nuvem via **Flux.1 Fill Pro**
> ou local grátis via SDXL) e **recola** sobre a original com `ImageCompositeMasked` — tudo fora da máscara fica
> **byte-idêntico**. Numa máquina de 8 GB: a **máscara** roda local (SAM+GroundingDINO em precisão cheia) e a
> **geração** vai para a nuvem.

|  |  |
|---|---|
| 🎯 Faz | Edita uma região (máscara) e recola sem alterar o resto da imagem |
| 🧠 Técnica | Selecionar (SAM/DINO por texto) → inpaint (**fal Flux Fill** OU **SDXL local**) → `ImageCompositeMasked` |
| 💳 Custo/billing | **fal credits** (rota nuvem, melhor qualidade) **ou** 100% local grátis (rota SDXL) |
| 🔌 Provedores/Nós | `FluxPro1Fill_fal` (fal) · `GroundingDinoSAMSegment` (local) · `ImageCompositeMasked` (core) |
| 📥 Entrada | 1 imagem + (texto da região **ou** máscara pintada no MaskEditor) |
| 📤 Saída | Imagem editada (resto byte-idêntico) |
| 🧩 Modelos | `sam_vit_h` + GroundingDINO **SwinB** (local) · Flux.1 Fill Pro (fal) · `sd_xl_base` (opcional, rota local) |
| 🧱 Requer | `comfyui_segment_anything` + `ComfyUI-KJNodes` (+ `ComfyUI-fal-API` p/ a rota nuvem) |
| 🟡 Status | Replicado da máquina local (validar nós/chave) |

📇 **Card de API (inputs/params por nó):** [`API_REFERENCE_mask-edit.md`](API_REFERENCE_mask-edit.md)

> Os modelos cloud (Nano Banana / Kontext / Seedream) editam a imagem **toda** e às vezes "devolvem a foto intacta".
> A abordagem por máscara é **determinística sobre o que muda**. Seleção da região → `knowledge-image-masking`;
> edição → `knowledge-image-editing`; nós fal/seed gates → `knowledge-comfyui-api-nodes`.

## Os arquivos
| Arquivo | O que faz | Nó-chave |
|---|---|---|
| `00_LEIA-ME_comece_aqui` | Índice + a técnica select→edit→paste-back | (só nota) |
| `01_selecionar_regiao_texto` | Texto → máscara (preview antes de editar) | `GroundingDinoSAMSegment` |
| `02_inpaint_local_sdxl_composite` | Inpaint **grátis local** da região + recola | `CheckpointLoaderSimple` (SDXL) + `KSampler` |
| `03_inpaint_nuvem_fal_composite` | Inpaint **nuvem** (Flux Fill, máx. qualidade) + recola | `FluxPro1Fill_fal` |
| `04_crop_stitch_alta_res` | Recorta→gera a 1024→costura de volta (melhor detalhe em 8 GB) | `ImageCropByMaskAndResize` / `ImageUncropByMask` |
| `replace_via_codigo.py` | Recolagem **fora do ComfyUI** (PIL paste com borda borrada) | — |

## Fluxo
```
LoadImage → GroundingDinoSAMSegment("a camisa", threshold 0.3) ─MASK→ GrowMaskWithBlur(expand 10, blur 8) ─┐
                                                                                                          │
  ROTA NUVEM (03):  MaskToImage ─→ FluxPro1Fill_fal(image, mask_image, seed=0)  ──┐                       │
  ROTA LOCAL (02):  VAEEncode + SetLatentNoiseMask + DifferentialDiffusion        │  → ImageCompositeMasked ←┘ (original = destino)
                    → KSampler(denoise 0.75) → VAEDecode                          │       → (ColorMatch 0.4) → SaveImage
```

## Pré-requisitos
- **Máscara é local** (cabe em 8 GB): `sam_vit_h` + GroundingDINO **SwinB** em precisão cheia.
- **Rota nuvem** (`03`): `FAL_KEY`. **Rota local** (`02`/`04`): `sd_xl_base_1.0` (grátis, opcional no setup).

## Setup
```bash
export HF_TOKEN=...           # acelera o download dos modelos de máscara
export FAL_KEY=...            # só p/ a rota nuvem (03); o setup grava em config.ini a partir do ambiente
INSTALL_SDXL=1 bash setup.sh  # INSTALL_SDXL=1 baixa ~6.5GB do sd_xl_base p/ a rota local (omita p/ só-nuvem)
```

## Como usar (:8188)
1. `01_selecionar_regiao_texto` — escreva a região em **inglês simples** (*"the shirt"*), ajuste `threshold` (0.25–0.4; caia p/ 0.2 se não achar) e veja o **preview** da máscara.
2. Edite com **`03`** (nuvem, máx. qualidade) **ou** **`02`** (local grátis). Para detalhe alto numa região pequena, use **`04`** (crop&stitch).
3. A saída sempre termina em `ImageCompositeMasked` sobre a original (o resto não passa pelo VAE).

## Parâmetros não-óbvios
| Onde | Campo | Valor | Nota |
|---|---|---|---|
| `FluxPro1Fill_fal` | `seed` | **`0`** = aleatório | **`-1` TRAVA** (gate `!= 0`). `mask_image` é **IMAGE** → use `MaskToImage` |
| `KSampler` (rota local) | `denoise` | 0.5–0.6 leve · 0.8–0.9 forte | `sd_xl_base` **não é** modelo de inpaint → `VAEEncode`+`SetLatentNoiseMask`+`DifferentialDiffusion` (NÃO `InpaintModelConditioning`) |
| `GrowMaskWithBlur` | `expand`/`blur_radius` | 10 / 8 | costura sem emenda |
| `ColorMatch` | `method`/`strength` | `hm-mkl-hm` / 0.4 | 0.3–0.6 |
| `ImageCropByMaskAndResize` | `base_resolution`/`padding` | 1024 / 32 | maior ganho em 8 GB |

## Troubleshooting
| Problema | Solução |
|---|---|
| `FluxPro1Fill_fal` "travou"/seed | Use `seed=0` (não `-1`). fal bloqueia sem barra de progresso (normal) |
| Região não mudou | denoise baixo (suba p/ 0.8+) ou máscara pequena (aumente `expand`) |
| Mudou além da região | confirme que `ImageCompositeMasked` usa a **mesma** máscara; sem inpaint-conditioning, baixe o denoise |
| Borda visível | suba `GrowMaskWithBlur.blur_radius` (8–16) |
| `GroundingDinoSAMSegment` não acha | baixe `threshold` p/ 0.2 ou use um substantivo simples em inglês |
| Nós vermelhos | Manager → Install Missing (`comfyui_segment_anything`, KJNodes, fal-API) |

## Referências
- `knowledge-image-masking` (seleção), `knowledge-image-editing` (inpaint), `knowledge-comfyui-api-nodes` (fal/seed gates), `knowledge-comfyui-api` (recolagem via código).
- Equivalente self-hosted (RunPod): `workflows-cloud/inpaint-region-cropstitch/`.
- Fonte: `config/06-ai-agents/comfyui-edicao-por-mascara.md`.
