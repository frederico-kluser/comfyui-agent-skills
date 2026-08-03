# SCAIL-2 — Parâmetros e Prompts

Configuração canônica do sampler e boas práticas de prompt.

## Sampler (consenso da comunidade)
- **sampler**: euler
- **scheduler**: simple
- **steps**: 6 (CLI oficial usa 8 — teste os dois)
- **cfg**: 1.0 (a guidance vem da LoRA destilada via `SamplerCustom`)
- **shift**: 1

## Frames e resolução
- Padrão/máx: **81 frames** (~5s).
- Saída 30 fps no VHS — mas o modelo roda a **16 fps**.
- Gere a 16 fps e **interpole** (RIFE/FILM); não suba o `force_rate`.
- Largura/altura **divisíveis por 32** (832×480 base 480p; 704×1280 vertical).

## Vídeo longo
Context Windows (context_length 81, overlap 16) ou o nó `SCAIL Auto Extend`.

## CLI oficial
`generate.py` + LightX2V: `--sample_steps 8 --sample_shift 1 --sample_guide_scale 1.0`, lora_alpha 1.0.

## Prompts
Treinado com prompts **longos e detalhados** que descrevem o vídeo gerado.
Prompts curtos/vazios funcionam, mas pioram o resultado.
Dica oficial: use um VLM (ex.: Gemini) para ler a imagem de referência + o movimento e gerar o prompt.

## Referências
- `docs/SCAIL-2.md`
- Debug → `task-debug-generation`
