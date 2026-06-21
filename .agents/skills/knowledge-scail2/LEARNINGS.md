# LEARNINGS — knowledge-scail2

> Memória episódica desta skill. Append-only (data + fonte: usuário > inferência).
> `meta-consolidation` deduplica/promove/poda. Promova ao corpo do SKILL.md o que virar
> padrão estável (≥2× ou confirmado pelo usuário). Revisão humana via git diff.

<!-- Formato:
## AAAA-MM-DD — <título>
- **Contexto**: <tarefa/situação>
- **Aprendizado**: <o que NÃO era óbvio: param, path, gotcha, anti-padrão>
- **Fonte**: usuário | inferência
- **Ação**: promover ao corpo? / atualizar description?
-->

## 2026-06-19 — Caminho NATIVO do ComfyUI (probação)
- **Contexto**: análise de um workflow SCAIL-2 nativo de terceiros (`workflows-cloud/scail2-native-3rdparty/`).
- **Aprendizado**: além do wrapper kijai, há o caminho **nativo** com nós **core** (`WanSCAILToVideo`,
  `SCAIL2ColoredMask`, `UNETLoader`, `ModelSamplingSD3`, `KSampler`) — ver [[knowledge-scail2-native]]. Nele o
  **shift** vem de `ModelSamplingSD3 ≈ 5` (≠ o `--sample_shift 1` do CLI: espaços de parâmetro diferentes,
  não é contradição). `replacement_mode` é um booleano (Animation/Replacement). A máscara colorida é gerada
  por **texto** (SAM3), não pintada. SAM 3.1 carregado em `models/checkpoints/`.
- **Fonte**: inferência. **Ação**: a confirmar no pod; nuançar o "shift 1" no corpo se confirmado.

_(novas entradas abaixo)_
