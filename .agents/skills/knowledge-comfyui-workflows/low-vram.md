# Low-VRAM — Ordem de Ataque

Estratégias para caber na VRAM, da mais efetiva à mais drástica.

## 1. WanVideoBlockSwap
`blocks_to_swap` default 20, máx **40** (o 14B tem 40 blocos; o 1.3B tem 30).
Economiza 10–15GB ao custo de ~5–15% de velocidade.

## 2. Quantização
fp8 scaled → GGUF (city96, em `models/unet`). Reduz VRAM 2–8×.

## 3. Tiled VAE + flags
- Tiled VAE decode.
- `--lowvram`/`--novram`.

## 4. Reduza frames antes da resolução
Frames multiplicam VRAM mais rápido que resolução.
Mantenha múltiplos de 32.

## LoRA de aceleração
`WanVideoLoraSelect` (de `models/loras`, encadeável).
- **LightX2V** = 4 passos sem CFG (cfg=1) — `enable_cfg=false` senão borra.
- Wan **2.2** usa dois modelos (high+low noise) → dois Model Loaders + dois LoRA selects.

## Referências
- `docs/workflow-guide.md`
- Debug → `task-debug-generation`
