# Otimização de Edição

Configurações de sampler, quantização e performance para edição de imagem.

## Samplers por modelo
| Modelo | Sampler | Scheduler | Passos | CFG |
|--------|---------|-----------|--------|-----|
| Flux/Fill | euler | res_multistep | — | — |
| Kontext | — | — | — | guidance ~2.5 |
| Qwen | — | — | ~10 | 1.0 |
| SDXL | dpmpp_2m | karras | 25-30 | 6-7 |
| Lightning/Turbo | — | — | 4-8 | — |

## Quantização (VRAM)
- **fp8** (`--fast`, −40% VRAM).
- **GGUF** (Q8/Q5 ≈ fp16).

## Aceleração
- **SageAttention** (`--sage-attention`).

## Resolução nativa
- 1024 para SDXL/Flux/Qwen.

## Erros comuns
- **Bordas visíveis** → grow+blur+Differential Diffusion.
- **Desvio de cor no Flux** → Color Match.

## Referências
- `docs/image-editing.md` §5
