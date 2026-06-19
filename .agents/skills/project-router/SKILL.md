---
name: project-router
description: >-
  Roteia TODA tarefa neste repo (ComfyUI, SCAIL-2, Wan 2.1/2.2, Flux, RunPod) para as
  skills certas ANTES de qualquer implementação — mesmo que o usuário não cite skills.
  Use para qualquer pedido: gerar vídeo/imagem, montar/adaptar workflow, subir pod,
  escolher GPU, estimar custo, baixar modelos, debugar geração ou criar comercial.
  Não é fonte de conhecimento — ela despacha; o conteúdo vive nas skills de conhecimento.
metadata:
  version: 0.1.0
  type: router
---
# Project Router

Ponto de entrada único. O conhecimento deste projeto está fatiado em skills carregadas
sob demanda (progressive disclosure). Sua função: montar a cadeia certa de skills e
carregá-las ANTES de agir, para não reler docs nem escanear o repo.

## Protocolo (execute antes de qualquer trabalho)
1. **Classifique a tarefa**: domínio(s) tocado(s) — SCAIL-2 / ComfyUI / RunPod-infra /
   provisioning / comercial; tipo — gerar / montar workflow / setup / debug / decisão de custo;
   complexidade (passo único vs pipeline).
2. **Consulte o catálogo** (`catalog.md` → "Cadeias típicas") e selecione as skills relevantes.
3. **Monte a cadeia**: ordem + o que pode rodar em paralelo via subagentes (contexto isolado
   para análise pesada, p.ex. ler um doc inteiro ou escanear `workflows/`).
4. **Carregue o conhecimento** das skills selecionadas (leia os `SKILL.md`; abra `references`/docs
   de nível 3 só se o `SKILL.md` não bastar).
5. **Execute** a cadeia.
6. **Feche**: garanta que cada skill de tarefa rodou seu passo `<evolution>` (append em
   `LEARNINGS.md` / propor skill nova via `meta-evolution`).

## Cadeias típicas (resumo — ver `catalog.md`)
- Criar comercial → `task-create-commercial` (orquestra `knowledge-scail2` + `knowledge-comfyui-workflows` + provisioning).
- Subir pod / baixar modelos → `task-launch-runpod-pod` + `knowledge-runpod-provisioning` + `knowledge-runpod-infra`.
- Montar/adaptar workflow → `task-build-workflow` + `knowledge-comfyui-workflows` (+ `knowledge-scail2`).
- Debug de geração → `task-debug-generation` + `knowledge-comfyui-workflows`.
- Criar/empacotar um projeto de workflow → `task-package-workflow-project` (adapta exemplo + gera setup.sh) + a knowledge skill da técnica.
- "Qual GPU / quanto custa" → `knowledge-runpod-infra`.

## Regras
- Se **nenhuma** skill cobre a tarefa, invoque `meta-evolution` para propor uma nova — não improvise
  conhecimento volátil de cabeça.
- Em **ambiguidade** entre skills, prefira a mais específica do domínio (ex.: SCAIL-2 vence ComfyUI genérico).
- Nunca **pule** o passo de evolução ao concluir uma skill de tarefa.
- O router **não** implementa nem guarda conhecimento de domínio — ele só despacha. Conhecimento mora
  nas knowledge skills (por quê: mantém o router estável e barato, e o conhecimento curável em um lugar só).

## Evolução
Se você rotear errado (skill errada, faltante ou descrição ambígua), faça append em `LEARNINGS.md`
desta skill com: a tarefa, a cadeia escolhida e a que seria correta. `meta-consolidation` usa esse
registro para refinar as `description` das skills (gatilho de poda quando o erro de roteamento passa
de ~10–20%).
