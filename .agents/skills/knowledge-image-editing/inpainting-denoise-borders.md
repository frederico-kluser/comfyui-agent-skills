# Inpainting — Força, Bordas e Differential Diffusion

Controlar a intensidade da regeneração e evitar costuras visíveis.

## Denoise
- **0.8-1.0** — regenera completamente a área mascarada.
- **0.5-0.7** — equilibra original com novo conteúdo.
- **0.3-0.5** — refina mantendo a estrutura original.

## Feathering (evitar costura)
- `Grow mask` (buffer) + `Gaussian Blur Mask` (feathering) — suavizam a transição.
- `blend_pixels` 16-32 no Crop & Stitch.

## Differential Diffusion (soft inpainting)
Nó nativo do ComfyUI. Trata a máscara como gradiente (não binária).
- Cadeia: `Gaussian Blur Mask` → `Differential Diffusion` (caminho do modelo) → `InpaintModelConditioning` → KSampler.
- Funciona com checkpoints comuns (não precisa de modelo de inpaint dedicado).
- Denoise 0.6-0.8.

## Referências
- `docs/image-editing.md` §1
- Encodar a máscara → [inpainting-mask-encode](inpainting-mask-encode.md)
