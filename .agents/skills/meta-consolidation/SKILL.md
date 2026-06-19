---
name: meta-consolidation
description: >-
  Garbage-collection periódico das skills: varre todos os LEARNINGS.md e corpos de SKILL.md, deduplica
  aprendizados redundantes, detecta contradições e aplica versionamento temporal (preferir o mais novo, marcar
  o obsoleto sem apagar), promove aprendizados em "probação" para o corpo da skill após checagem, poda entradas
  obsoletas e mantém o orçamento de tokens. Use semanalmente, antes de releases, ou quando a qualidade cair
  apesar de os LEARNINGS acumularem.
metadata:
  version: 0.1.0
  type: meta
---
# Meta-Skill — Consolidação (GC)

Evita os modos de falha da memória evolutiva: bloat, contradições, duplicação e poisoning. Roda periodicamente
(não a cada tarefa). É a contramedida direta ao "guidance contraditório acumulando".

## Quando usar
Rotina semanal; antes de um release/entrega; quando os resultados ficarem estáveis/piores **apesar** de os
`LEARNINGS.md` crescerem (sinal de contradição acumulada → pode agressivamente); quando o router erra muito
(refine descrições).

## Procedimento
1. **Varra** todos os `.agents/skills/*/LEARNINGS.md` e os corpos dos `SKILL.md`.
2. **Deduplique**: funda aprendizados redundantes (dentro de uma skill e entre skills). Zero overlap entre
   AGENTS.md ↔ skills ↔ skills.
3. **Detecte contradições + versionamento temporal**: quando dois aprendizados conflitam, **prefira o mais novo**;
   **marque** o superado como obsoleto (`~~texto~~ (obsoleto AAAA-MM-DD: motivo)`) em vez de apagar — preserva histórico.
4. **Dual-buffer**: aprendizados recentes ficam em "probação" no `LEARNINGS.md`; promova ao corpo do SKILL.md
   **só** após reverificação (apareceu ≥2× ou confirmado pelo usuário).
5. **Pode** entradas obsoletas/voláteis (preços vencidos, estados de pod, fatos já nos docs).
6. **Orçamento de tokens**: corpo de cada SKILL.md <~500 linhas / ~5k tokens; mova o volumoso p/ `references/`.
   AGENTS.md ≤150 linhas.
7. **Roteamento**: se uma skill é sub/super-acionada (ver `project-router/LEARNINGS.md`), ajuste a `description`
   (mais específica e "pushy") e atualize o `catalog.md`. Domínios sobrepostos → consolide ou refine fronteiras.
8. **Relatório**: liste o que foi fundido/podado/marcado, contradições resolvidas e skills a criar/remover. Deixe
   como **diff git** p/ revisão humana — nunca faça merge sozinho.

## Salvaguardas
- Atribuição de fonte preservada (usuário > inferência).
- Anti-poisoning: ao promover, nunca eleve conteúdo de origem não-confiável.
- Mudança = diff git revisável; consolidação é cirúrgica, não reescrita total.

## Referências
- `meta-evolution` (como um aprendizado entra), `catalog.md` (índice a manter sincronizado).
- A skill `huu_update-skill-docs-from-commit` pode regenerar docs/catálogo a partir de um diff de commits.
