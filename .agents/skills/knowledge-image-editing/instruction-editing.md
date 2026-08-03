# Edição por Instrução (Sem Máscara)

Editar imagem descrevendo a mudança em texto, sem precisar pintar máscara.

## Flux Kontext [dev] (12B) — 🏆 recomendado
Edita por texto mantendo consistência da cena.
- **`guidance_scale`** padrão **2.5** (range 0-20).
- Prompt direto: "Change the leather jacket to a blue denim jacket".
- Modelo: `flux1-dev-kontext_fp8_scaled` (16GB) → `diffusion_models/`.
- Carrega clip_l + t5xxl + ae.

## Qwen-Image-Edit 2511 (20B)
Edição bilíngue de texto na imagem.
- Troca de objeto/fundo, relighting.
- LoRA Lightning 4 passos; ~10 passos, CFG 1.0.

## Combine com máscara
Quando precisar de controle cirúrgico: instrução textual + inpaint mascarado na região específica.

## Projetos de referência
- `workflows-cloud/instruction-edit-kontext`
- `workflows-cloud/qwen-image-edit`

## Referências
- `docs/image-editing.md` §1
- Modelos → [editing-models](editing-models.md)
