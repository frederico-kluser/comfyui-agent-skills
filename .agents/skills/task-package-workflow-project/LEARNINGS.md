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

## 2026-06-20 — Split: `workflows/` → `workflows-cloud/` + `workflows-api/`
- **Contexto**: o repo passou a ter duas pastas de bundle, separadas pelo **destino da inferência**: `workflows-cloud/` (self-hosted em GPU RunPod — os 7 projetos originais) e `workflows-api/` (modelo roda num provedor hospedado, fal/partner, **sem GPU**).
- **Aprendizado**: (1) `git mv workflows workflows-cloud` quebra TODA URL fixa `…/main/workflows/<proj>/…` nos `setup.sh` (confirma o learning de 2026-06-19) → corrigido com `sed 's#main/workflows/#main/workflows-cloud/#'` nos `setup.sh` + replace dos 7 nomes de projeto nos `.md`; os dirs runtime `$COMFY/user/default/workflows` **não** mudam. (2) **Bundle-API** difere do contrato-GPU: Card troca `🎮 GPU/VRAM` por `💳 Custo/billing` + `🔌 Provedores/Nós`; `setup.sh` instala `ComfyUI-fal-API` + **grava `FAL_KEY` do ambiente** (sem baixar modelos pesados) e roda **local** (8GB ok), não root-no-pod. (3) bundle-API multi-arquivo (ex.: `commercial-ondokai/` = 19 JSONs) → 1 README de pipeline + `API_REFERENCE_*.md` por nó. (4) `docs/` (relatórios de pesquisa) **não** são editados no rename.
- **Fonte**: usuário (pediu o split + replicar a stack de comercial por API).
- **Ação**: promovido ao corpo (Contrato de 2 pastas + gotcha Bundle-API). Convenção estável.

_(novas entradas abaixo)_
