# RunPod — Modelo → VRAM → GPU

Mapeamento do que cada modelo precisa e qual GPU escolher.

## Tabela

| Modelo | full | fp8 | GGUF | GPU recomendada |
|---|---|---|---|---|
| Flux.1 dev | ~24 | ~12–16 | Q4 6–8 / Q8 12–13 | RTX 4090 |
| Wan/SCAIL-2 14B **480p** | ~54–65 | ~16–24 | 6–17 | **RTX 5090** (fp8/GGUF) |
| Wan/SCAIL-2 14B **720p** | ~65–80 | ~40–50 | — | **A100 80GB** / H100 / H200 |

## Notas
- fp8: ~mesma qualidade, −20–40% VRAM.
- GGUF: cabe em GPU menor, +10–30% tempo.
- bf16/fp16: só com VRAM sobrando.

## Referências
- `docs/runpod-guide.md`
- Árvore de decisão → [decision-tree](decision-tree.md)
