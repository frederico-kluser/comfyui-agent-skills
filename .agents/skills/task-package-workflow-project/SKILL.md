---
name: task-package-workflow-project
description: >-
  Empacota um workflow entregável como um "projeto" versionado em workflows/<nome>/ contendo o
  <nome>.json (ComfyUI), um README.md de configuração e um setup.sh que sobe ao RunPod e roda como
  root. Use sempre que o pedido for "criar um workflow para X", "empacotar/entregar um workflow",
  "montar um projeto de workflow" ou disponibilizar um pipeline pronto para o pod — mesmo sem citar
  a skill. Adapta um exemplo known-good (não escreve JSON do zero). Difere de task-build-workflow
  (que monta o grafo no ComfyUI); esta EMPACOTA o bundle no repo.
metadata:
  version: 0.1.0
  type: task
---
# Tarefa — Empacotar um Projeto de Workflow

Entrega um workflow como **bundle reproduzível** no repo: uma pasta por projeto com o grafo, as
instruções e o provisioning. O usuário sobe o `.sh` no RunPod, roda como root, abre o `.json` e usa.

## Quando usar
"Criar um workflow para <tarefa>", "empacotar/entregar um workflow", "montar um projeto de workflow",
"deixar pronto para subir no pod". Para apenas montar/depurar o grafo no ComfyUI (sem empacotar) →
`task-build-workflow` / `task-debug-generation`.

## Contrato da pasta (obrigatório)
```
workflows/<nome-do-projeto>/      # kebab-case; o nome descreve a tarefa (ex.: person-swap-scail2)
├── <nome-do-projeto>.json        # workflow ComfyUI (formato UI, carregável arrastando)
├── README.md                     # abre com Card Informativo (tabela) + seções padronizadas (pré-req, setup, como usar, parâmetros, validação, troubleshooting, refs)
└── setup.sh                      # provisioning RunPod (root): nodes + modelos DO workflow + baixa o .json
```

## Procedimento
1. **Roteie o conhecimento** (via `project-router`): identifique a técnica e carregue a knowledge skill
   certa (`knowledge-scail2`, `knowledge-comfyui-workflows`, etc.). Não reinvente o que já está nelas.
2. **Adapte um exemplo known-good** — NÃO escreva o JSON do zero (os docs avisam: JSON à mão é frágil).
   Baixe um exemplo oficial (ex.: `kijai/ComfyUI-WanVideoWrapper/example_workflows/...` via `gh api` →
   `base64 -d` direto para o arquivo) e faça ajustes **seguros** (clonar um nó existente para adicionar
   um `MarkdownNote` de instruções; mudar defaults). Valide com `python3 -c "import json;json.load(...)"`.
3. **Escreva o `setup.sh`** como fork focado de
   `.agents/skills/knowledge-runpod-provisioning/scripts/provisioning.sh`: só os custom nodes e modelos
   QUE ESTE workflow usa; garanta pré-condições (ex.: ComfyUI nightly p/ SCAIL-2); baixe o próprio `.json`
   do repo público para `ComfyUI/user/default/workflows/`. Rode `bash -n setup.sh`.
4. **Escreva o `README.md`** (estrutura padrão). Comece com o **Card Informativo** — tabela limpa no topo:
   `🎯 Faz · 🧠 Técnica · 🎮 GPU/VRAM · 📥 Entrada · 📤 Saída · 🧩 Modelos · 🟢/🟡 Status` (+ `🧱 Requer` só se
   houver pré-condição dura, ex.: ComfyUI nightly). Depois, **na mesma ordem em todos os projetos**: pré-req
   (GPU/VRAM → `knowledge-runpod-infra`); setup; **como anexar os inputs** (qual nó recebe o vídeo, qual recebe a
   foto; passos manuais como gerar máscara ou clicar no `PointsEditor`); parâmetros não-óbvios (tabela); **passos
   de validação no pod**; troubleshooting (tabela) → `task-debug-generation`; referências. Referencie as knowledge
   skills; não duplique o conteúdo delas.
5. **Registre no catálogo**: adicione o projeto à lista de `workflows/` no `README.md` raiz (e, se virar
   um tipo recorrente, uma cadeia no `catalog.md`).
6. **Valide** (estrutural agora; funcional no pod): JSON parseia; `bash -n setup.sh`; sem segredos no `.sh`.

## Gotchas
- **Honestidade:** marque o `.json` como rascunho a validar no pod quando a técnica for nova/instável
  (ex.: SCAIL-2). Não prometa "runnable" sem teste — explique a validação no README.
- **Sem tokens** no `setup.sh` (lê `HF_TOKEN`/`CIVITAI_TOKEN` do ambiente). Nunca versione segredos.
- **Reuso:** modelos/paths vêm de `knowledge-runpod-provisioning`; não recopie manifestos divergentes.
- O `setup.sh` roda como **root** no pod (instala apt/git, baixa modelos) — isso é esperado e seguro no pod descartável.

## Referências
- `knowledge-runpod-provisioning` (script base, manifesto), `knowledge-comfyui-workflows` (grafo/JSON),
  `task-build-workflow` (montar o grafo), `task-launch-runpod-pod` (subir o pod).
- Exemplo de referência: `workflows/person-swap-scail2/` (primeiro bundle).

## <evolution> (ao concluir)
1. O bundle ficou consistente (JSON válido, `bash -n` ok, README cobre anexar inputs + validação)? Só então persista.
2. Persista: um exemplo-base bom para uma técnica, um ajuste de `setup.sh` que funcionou, um passo manual
   não-óbvio do README, um anti-padrão. Ignore o óbvio/volátil.
3. Append em `LEARNINGS.md` (data + fonte: usuário > inferência). Destile no corpo se recorrente (`version++`).
4. Se a técnica for nova e recorrente, proponha uma knowledge skill via `meta-evolution`.
5. Diff git p/ revisão humana — não faça merge sozinho.
