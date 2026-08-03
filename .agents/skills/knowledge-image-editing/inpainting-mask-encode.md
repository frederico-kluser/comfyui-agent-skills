# Inpainting — Encodar a Máscara

A escolha do nó de encoding define a qualidade do inpainting. Três opções, em ordem de recomendação:

## InpaintModelConditioning — 🏆 recomendado (2026)
Condiciona +/−/latente de uma vez. Permite **denoise baixo mesmo com modelo de inpaint** (ex.: 0.45), sem perder coerência.
- Use com `Gaussian Blur Mask` para feathering.
- Compatível com Differential Diffusion.

## VAE Encode (for Inpainting)
`grow_mask_by` 6-8px (zona-tampão). **Exige denoise = 1.0** (menor borra).
- "True inpainting"; melhor com modelos de inpaint dedicados.

## Set Latent Noise Mask
Ruído só na região; permite **denoise parcial 0.3-0.8** (img2img localizado).
- Usa `VAE Encode` normal antes.
- Bom para refinamentos sutis.

## ⚠️ Não é inpainting
"Conditioning (Set Mask)" — aplica prompt a uma área, mas **não** faz inpainting.

## Referências
- `docs/image-editing.md` §1
- Força e bordas → [denoise e bordas](inpainting-denoise-borders.md)
- Crop & Stitch → [crop-stitch](crop-stitch.md)
