# Inpaint Crop & Stitch — Padrão Ouro

Editar só uma parte da imagem e recolar sem tocar pixels fora da máscara.

## Cadeia
`✂️ Inpaint Crop` (recorta ao redor da máscara + contexto, redimensiona à resolução nativa) → sampling → `✂️ Inpaint Stitch` (costura de volta com blend nas bordas).

## Parâmetros
- **`context_expand_pixels/factor`** — quanto contexto ao redor da máscara (coerência).
- **`blend_pixels`** 16-32 — feathering da recolagem.
- **`rescale_factor`** — >1 para mais detalhe; <1 evita "dupla cabeça".

## Performance
Modo **GPU** é default e **30x-100x** mais rápido que CPU.

## Configuração recomendada
- Use `InpaintModelConditioning` (denoise<1).
- Máscara 100% opaca (#FFFFFF).
- Combine com [Differential Diffusion](inpainting-denoise-borders.md) para bordas suaves.

## Projeto de referência
`workflows-cloud/inpaint-region-cropstitch` — workflow completo.

## Referências
- `docs/image-editing.md` §3
- Recolar via código/API → `knowledge-comfyui-api`
