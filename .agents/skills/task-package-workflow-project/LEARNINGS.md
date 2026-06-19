# LEARNINGS — task-package-workflow-project

> Memória episódica desta tarefa. Append-only (data + fonte: usuário > inferência).
> `meta-consolidation` deduplica/promove/poda. Promova ao corpo o que virar padrão estável
> (≥2× ou confirmado pelo usuário). Revisão humana via git diff.

<!-- Formato:
## AAAA-MM-DD — <título>
- **Contexto**: <projeto/técnica>
- **Aprendizado**: <base boa, ajuste de setup.sh, passo manual do README, anti-padrão>
- **Fonte**: usuário | inferência
- **Ação**: promover ao corpo? / nova knowledge skill?
-->

## 2026-06-19 — Primeiro bundle: person-swap-scail2 (probação)
- **Contexto**: empacotar o workflow de troca de pessoa em vídeo (SCAIL-2 Replacement).
- **Aprendizado**: (1) o exemplo SCAIL público do kijai (`wanvideo_2_1_14B_SCAIL_pose_control_example_01.json`,
  67 nós) é **pose-control**, não replacement-específico — a wiring do Replacement (máscara colorida + flag)
  precisa ser conferida no pod. (2) Para anotar um JSON UI sem corromper, **clone um `MarkdownNote` já
  existente** no arquivo e troque id/pos/texto (estrutura garantida). (3) `setup.sh` que baixa o próprio
  `.json` do repo público (`raw.githubusercontent.com/.../main/workflows/<proj>/<proj>.json`) deixa o
  bundle "1 arquivo p/ subir e rodar".
- **Fonte**: inferência (pesquisa via gh api + docs do projeto).
- **Ação**: manter em probação até validar no pod; se o padrão "clonar nó p/ anotar" e "setup baixa o
  próprio json" se repetirem, promover ao corpo da SKILL.md.

_(novas entradas abaixo)_
