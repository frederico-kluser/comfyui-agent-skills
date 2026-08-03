# Context Windows — Vídeo Longo (>81 frames)

Dividir vídeos longos em janelas sobrepostas que são geradas e mescladas.

## WanVideoContextOptions
Input `context_options` do Sampler. Parâmetros:
- `context_schedule` — uniform_standard/looped/static.
- `context_frames` — 81.
- `context_stride` — 4.
- `context_overlap` — 16.
- `freenoise` — True.

## Delta
`delta = context_frames − context_overlap` — o avanço efetivo entre janelas.

## ⚠️ Incompatível com
MultiTalk I2V — não use os dois juntos.

## Alternativa SCAIL-2
`Brobert-in-aus/scail-auto-extend`: chunking + ancoragem + color-match automáticos.

## Referências
- `docs/workflow-guide.md`
- Cadeia Wan → [wan-video-wrapper](wan-video-wrapper.md)
