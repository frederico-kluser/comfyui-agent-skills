# LEARNINGS — knowledge-image-masking

> Memória episódica. Append-only (data + fonte: usuário > inferência). `meta-consolidation` deduplica/promove/poda.
> Promova ao corpo o que virar padrão estável (≥2× ou confirmado). Revisão humana via git diff.

<!-- ## AAAA-MM-DD — título
- **Contexto**: <alvo a mascarar>
- **Aprendizado**: <detector/modelo melhor por tipo, gotcha de máscara>
- **Fonte**: usuário | inferência
- **Ação**: promover? / atualizar description? -->

## 2026-06-19 — SAM3_VideoTrack: rastreio por texto em vídeo (probação)
- **Contexto**: workflow SCAIL-2 nativo de terceiros (`workflows/scail2-native-3rdparty/`).
- **Aprendizado**: `SAM3_VideoTrack` segmenta um **conceito por texto** (ex.: "human") e o **rastreia ao
  longo dos frames** do vídeo, gerando `SAM3_TRACK_DATA` (≠ máscara estática de imagem). Alimenta o
  `SCAIL2ColoredMask`. Útil sempre que a máscara precisa seguir um sujeito no tempo. Ver [[knowledge-scail2-native]].
- **Fonte**: inferência. **Ação**: promover ao corpo (§ semântico) se reaparecer.

_(novas entradas abaixo)_
