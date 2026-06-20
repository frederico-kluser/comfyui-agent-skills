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

## 2026-06-20 — Card Informativo + estrutura uniforme em todos os READMEs
- **Contexto**: padronização dos 7 projetos em `workflows/` (sem alterar `.json`/`setup.sh`).
- **Aprendizado**: (1) Todo README abre com um **Card Informativo** (tabela limpa): `🎯 Faz · 🧠 Técnica ·
  🎮 GPU/VRAM · 📥 Entrada · 📤 Saída · 🧩 Modelos · status` (+ `🧱 Requer` p/ pré-condição dura, ex.: ComfyUI
  nightly). (2) Mesma ordem de seções em todos: Card → Status → Pré-req → Setup → Como usar → Parâmetros →
  Validação → Troubleshooting → Referências. (3) **Não renomear pasta/arquivo do projeto**: o `setup.sh` baixa
  `…/main/workflows/<proj>/<proj>.json` por URL fixa — renomear quebra o download (logo "distribuição" = melhorar
  catálogo/apresentação, não mover arquivos). (4) Catálogo da raiz agrupado por categoria (Vídeo & Animação ·
  Edição de imagem · Enquadramento & Fundo) com colunas técnica/GPU/status + legenda 🟢/🟡. (5) Onde há JSON de
  API (scail2-native), o README aponta para os `API_REFERENCE_*.md` (cards por nó).
- **Fonte**: usuário (pediu cards informativos + distribuição intuitiva/profissional; escolheu "tabela limpa").
- **Ação**: promovido ao corpo da SKILL.md (Contrato da pasta + passo 4). Convenção estável.

_(novas entradas abaixo)_
