---
name: knowledge-image-editing
description: >-
  Conhecimento de edição de imagem no ComfyUI: inpainting (VAE Encode for Inpainting vs Set Latent
  Noise Mask vs InpaintModelConditioning, denoise, feathering, Differential Diffusion, Inpaint
  Crop&Stitch), edição por instrução sem máscara (Flux Kontext, Qwen-Image-Edit), composição e os
  modelos (Flux Fill/Kontext/Qwen/Flux.2/Z-Image/SDXL) + otimização. Use ao editar/inpaint/alterar
  uma imagem, trocar objeto/cor/fundo por máscara ou por instrução — mesmo sem citar a skill.
  Selecionar a região → knowledge-image-masking; recolar via código/API → knowledge-comfyui-api.
metadata:
  version: 0.1.0
  type: knowledge
---
# ComfyUI — Edição de Imagem (inpaint + instrução)

Duas filosofias que se combinam: (a) **máscara + denoise** (inpainting clássico) e (b) **edição por
instrução textual** (Flux Kontext, Qwen-Image-Edit) que dispensa máscara para muitas tarefas.

## Quando usar
"Editar/alterar/inpaint uma imagem", "trocar objeto/cor/fundo", "mudar X para Y na foto", escolher
o nó de máscara ou o modelo de edição, corrigir bordas/cor pós-inpaint.

## Encodar a máscara (a escolha define a qualidade)
- **VAE Encode (for Inpainting)**: `grow_mask_by` 6-8px (zona-tampão). **Exige denoise = 1.0** (menor borra). "True inpainting"; melhor com modelos de inpaint dedicados.
- **Set Latent Noise Mask**: ruído só na região; permite **denoise parcial 0.3-0.8** (img2img localizado). Usa `VAE Encode` normal antes.
- **InpaintModelConditioning**: o **recomendado** em 2026 — condiciona +/−/latente de uma vez e permite **denoise baixo mesmo com modelo de inpaint** (ex.: 0.45), sem perder coerência.
- ⚠️ "Conditioning (Set Mask)" **não** é inpainting (aplica prompt a uma área).

## Força e bordas
- `denoise`: 0.8-1.0 regenera; 0.5-0.7 equilibra; 0.3-0.5 refina.
- `Grow mask` (buffer) + `Gaussian Blur Mask` (feathering) evitam costura visível.
- **Differential Diffusion** (soft inpainting, nó nativo): `Gaussian Blur Mask` → `Differential Diffusion` (caminho do modelo) → `InpaintModelConditioning` → KSampler. Trata a máscara como gradiente; funciona com checkpoints comuns; denoise 0.6-0.8.

## Inpaint Crop & Stitch (padrão de ouro p/ "editar só uma parte e recolar")
`✂️ Inpaint Crop` (recorta ao redor da máscara + contexto, redimensiona à resolução nativa) → sampling →
`✂️ Inpaint Stitch` (costura de volta **sem tocar pixels fora da máscara**, blend nas bordas). Params:
`context_expand_pixels/factor` (coerência), `blend_pixels` 16-32 (feathering da recolagem), `rescale_factor`
(>1 detalhe / <1 evita "dupla cabeça"). Modo **GPU** é default e **30x-100x** mais rápido que CPU. Use
`InpaintModelConditioning` (denoise<1) e máscara 100% opaca (#FFFFFF).

## Edição por instrução (sem máscara)
- **Flux Kontext [dev]** (12B): edita por texto mantendo consistência. `guidance_scale` padrão **2.5** (0-20). Prompt direto: "Change the leather jacket to a blue denim jacket". `flux1-dev-kontext_fp8_scaled` (16GB). Carrega clip_l + t5xxl + ae.
- **Qwen-Image-Edit 2511** (20B): edição bilíngue de texto na imagem, troca de objeto/fundo, relighting. LoRA Lightning 4 passos; ~10 passos, CFG 1.0.
- Combine instrução + inpaint mascarado quando precisar de controle cirúrgico de uma região.

## Modelos (repo → arquivo → pasta)
- **Flux Fill** (inpaint/outpaint): `flux1-fill-dev.safetensors` → `diffusion_models/` (+ clip_l, t5xxl → `text_encoders/`, `ae.safetensors` → `vae/`).
- **Flux Kontext**: `flux1-dev-kontext_fp8_scaled.safetensors` → `diffusion_models/`.
- **Qwen-Image-Edit 2511**: modelo Qwen + Qwen2.5-VL + VAE (workflow nativo). **SDXL-inpainting** p/ rápido/leve.
- Manifesto/baixar → `knowledge-runpod-provisioning` (padrão aria2c) ou o `setup.sh` do projeto.

## Otimização
Sampler: Flux/Fill euler/res_multistep; Kontext guidance ~2.5; Qwen ~10 passos CFG 1.0; SDXL `dpmpp_2m`+`karras`
25-30 passos CFG 6-7; Lightning/Turbo 4-8 passos. **fp8** (`--fast`, −40% VRAM) / **GGUF** (Q8/Q5 ≈ fp16). **SageAttention**
(`--sage-attention`). Resolução nativa 1024 (SDXL/Flux/Qwen). Erros: bordas → grow+blur+Differential; desvio de cor Flux → Color Match.

## Referências (nível 3)
- `docs/image-editing.md` (fonte completa). Projetos: `workflows-cloud/inpaint-region-cropstitch`, `instruction-edit-kontext`, `qwen-image-edit`, `outpaint-extend`.
- Cadeia: selecionar região → `knowledge-image-masking`; recolar via código/API → `knowledge-comfyui-api`; upscale/relight/controlnet → `knowledge-image-enhance`.

## Evolução
Append em `LEARNINGS.md` ao descobrir um nó/param melhor, um modelo novo, ou um anti-padrão (bordas/cor). Destile
no corpo se estável (`version++`). Diff git p/ revisão.
