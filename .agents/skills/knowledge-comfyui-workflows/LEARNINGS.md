# LEARNINGS — knowledge-comfyui-workflows

> Memória episódica desta skill. Append-only (data + fonte: usuário > inferência).
> `meta-consolidation` deduplica/promove/poda. Promova ao corpo o que virar padrão estável
> (≥2× ou confirmado pelo usuário). Revisão humana via git diff.

<!-- Formato:
## AAAA-MM-DD — <título>
- **Contexto**: <workflow/tarefa>
- **Aprendizado**: <nó novo, default mudado, incompatibilidade, organização que funcionou>
- **Fonte**: usuário | inferência
- **Ação**: promover ao corpo? / atualizar description?
-->

## 2026-06-19 — Padrão de organização limpo (probação)
- **Contexto**: workflow SCAIL-2 nativo de terceiros (63 nós, muito legível).
- **Aprendizado**: combinar **Set/Get (KJNodes)** + um **Subgraph** (encapsular o bloco SAM3) + **Primitives
  nomeados** como controles de topo (`DURAÇÃO`, `REPLACE`) + uma **MarkdownNote com os links de download dos
  modelos** + 3 grupos ("MODELS / INPUTS / SAMPLER+OUTPUT") deixa um workflow grande navegável. Bom template.
- **Fonte**: inferência. **Ação**: promover ao corpo (§ Organização) se reaparecer.

_(novas entradas abaixo)_
