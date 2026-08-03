# Upscaling — Ampliar Imagem

Técnicas para aumentar resolução preservando ou melhorando a qualidade.

## Model Upscale (rápido)
`Upscale Image (using Model)` com ESRGAN/RealESRGAN/**4x-UltraSharp**/4x-Foolhardy-Remacri.
- Apenas uma passada, sem re-difusão.
- Ideal para aumento rápido 2x-4x.

## Ultimate SD Upscale (ssitu)
Tiles + re-difusão para upscaling de alta qualidade.
- Params: `tile_size`, `seam_fix` (evita costura entre tiles), linear/chess.
- Use **ControlNet Tile** para coerência entre tiles.

## SUPIR (kijai/ComfyUI-SUPIR)
Restauração foto-realista com SDXL.
- Pesado: 32GB+ RAM (fp8 ajuda).
- Pipeline comum: SUPIR→2K depois 4x Remacri→8K.

## Referências
- `docs/image-editing.md` §4
- Provisionar modelos → `knowledge-runpod-provisioning`
