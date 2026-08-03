# SCAIL-2 — Escolha de Quantização (VRAM)

Qual variante do modelo usar para cada GPU.

## Tabela VRAM
| VRAM | Variante | Tamanho | Notas |
|------|----------|---------|-------|
| ≤12GB | GGUF Q4_K_M | 10.9 GB | "Daily driver" |
| 12-16GB | GGUF Q5_K_M | — | Meio-termo |
| 16GB | Q8_0 | 17.7 GB | Mais próximo do fp16 |
| 16-24GB | fp8 scaled | 17.7 GB | Bom equilíbrio |
| 24GB (RTX 4090) | fp8_scaled | 17.7 GB | Qualidade máxima na 4090 |
| 32GB+ (RTX 5090)/cloud | fp16 | — | Máxima qualidade |

## Qualidade por quantização
- Q8_0 ≈ fp16.
- fp8 preserva surpreendentemente bem.
- Q4/Q3 adicionam artefatos — use o DPO lora para corrigir mãos/rosto.

## ⚠️ Atenção
Rótulos de VRAM de algumas fontes parecem invertidos (o arquivo fp8 tem só ~17.7 GB).
Trate fp8/mxfp8 como **menor** VRAM e fp16 como **maior**.

## Referências
- `docs/SCAIL-2.md`
- Paths → [model-files](model-files.md)
