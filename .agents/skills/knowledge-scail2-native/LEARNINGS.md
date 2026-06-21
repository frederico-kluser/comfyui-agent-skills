# LEARNINGS — knowledge-scail2-native

> Memória episódica. Append-only (data + fonte: usuário > inferência). `meta-consolidation` deduplica/promove/poda.
> Promova ao corpo o que virar padrão estável (≥2× ou confirmado). Revisão humana via git diff.

## 2026-06-19 — Mapeado do workflow de terceiros (probação)
- **Contexto**: análise do `WORKFLOW - SCAIL2.json` (terceiros) → `workflows-cloud/scail2-native-3rdparty/`.
- **Aprendizado**: (1) O caminho **nativo** existe e usa nós **core** `WanSCAILToVideo` + `SCAIL2ColoredMask`
  (≠ wrapper kijai). (2) `replacement_mode` é UM booleano compartilhado por `SCAIL2ColoredMask` e
  `WanSCAILToVideo` (Animation/Replacement). (3) Máscara é por **texto** via `SAM3_VideoTrack` (concept,
  ex.: "human"), gerando `SAM3_TRACK_DATA` para vídeo e foto. (4) `ModelSamplingSD3` usa **shift 5** no nativo —
  difere do `--sample_shift 1` do CLI (espaços de parâmetro diferentes). (5) SAM 3.1 carregado via
  `CheckpointLoaderSimple` em `models/checkpoints/` (não `sam/`). (6) Org limpa: Set/Get + subgraph + Primitives nomeados.
- **A confirmar no pod**: significado dos slots numéricos intermediários de `WanSCAILToVideo`
  `[512,896,81,1,1,0,1,0,5,True]`; shift ideal (5 vs 1).
- **Fonte**: inferência (dissecação do JSON). **Ação**: promover após validação no pod.

<!-- novas entradas abaixo -->
