# Outpainting — Estender Imagem

Expandir a imagem para além das bordas originais, preenchendo o novo espaço de forma coerente.

## Fluxo básico
`Pad Image for Outpainting` (adiciona borda + cria a máscara) → Flux Fill / modelo de inpaint.

## Extend com Crop & Stitch
`Extend Image for Outpainting` (CropAndStitch):
- Recorta, redimensiona, faz outpaint e recompõe.
- Traz rescale/blend/restitch automáticos.

## Modelos recomendados
- **Flux Fill** — state of the art para outpaint.
- Modelos de inpaint SDXL — alternativa mais leve.

## Projeto de referência
`workflows-cloud/outpaint-extend` (workflow completo).

## Referências
- `docs/image-editing.md` §4
- Modelos → `knowledge-runpod-provisioning`
