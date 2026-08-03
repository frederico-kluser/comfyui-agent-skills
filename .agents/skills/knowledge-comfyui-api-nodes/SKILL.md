---
name: knowledge-comfyui-api-nodes
description: >-
  Conhecimento dos nós de API ONLINE do ComfyUI (modelo roda num provedor hospedado, paga por chamada): nós
  nativos partner (comfy.org credits) vs fal (`*_fal`) vs Replicate; catálogo de provedores/modelos (Veo 3.1,
  Nano Banana Pro, Kling, Seedance, Flux Pro/Kontext/Fill, Sora, Luma, Ideogram, Recraft, ElevenLabs) com os
  nomes de nó EXATOS; os seed gates que TRAVAM o nó; billing, chaves (secrets.env/FAL_KEY/login) e a decisão
  API-vs-self-hosted (regra dos 8GB). Use ao montar/rodar qualquer workflow que chame um modelo hospedado,
  escolher provedor, estimar créditos ou debugar um nó fal "travado" — mesmo sem citar a skill. NÃO cobre a API
  HTTP do próprio ComfyUI (ver knowledge-comfyui-api) nem GPU self-hosted/RunPod (ver knowledge-runpod-infra).
metadata:
  version: 0.3.0
  type: knowledge
---
# ComfyUI — Nós de API Online (geração hospedada)

O ComfyUI vira um **front-end de orquestração**: o grafo chama um modelo que roda **na nuvem do provedor**, paga-se
**por chamada**. Numa máquina de 8 GB isso é o caminho principal — a regra é *"nada de GGUF/quantizado/inferior
local"*: os modelos de ponta não cabem em 8 GB em precisão cheia, e a nuvem entrega um modelo **melhor e mais
rápido**. A GPU local só faz **máscara (SAM/GroundingDINO), composição (`ImageCompositeMasked`) e upscale ESRGAN**.

## Quando usar
"Rodar/montar workflow por API", "Veo/Kling/Nano Banana/Seedance/Flux Pro", "qual provedor", "quanto custa em
créditos", "nó `*_fal` travou", "fal vs Comfy", configurar `FAL_KEY`/login. Para a **API HTTP do próprio ComfyUI**
(`/prompt`, automação por código) → `knowledge-comfyui-api`. Para **alugar GPU** e rodar o modelo você mesmo → `knowledge-runpod-infra`.

## Técnicas (um arquivo por técnica)

| Técnica | Arquivo | O que cobre |
|---------|---------|-------------|
| Rotas e billing | [routes-billing.md](routes-billing.md) | Partner vs fal vs Replicate, credenciais, secrets.env |
| API vs self-hosted | [api-vs-selfhosted.md](api-vs-selfhosted.md) | Quando usar API vs alugar GPU (regra dos 8GB) |
| Seed gates | [seed-gates.md](seed-gates.md) | Tabela de seeds que travam cada nó |
| Catálogo: Vídeo | [catalog-video.md](catalog-video.md) | I2V/T2V, V2V (restyle/motion-transfer/extend), padrões de saída |
| Catálogo: Imagem/Edição | [catalog-image-edit.md](catalog-image-edit.md) | Nano Banana 2, Seedream, Kontext, Fill, Erase, Upscale |
| Catálogo: Música/Áudio | [catalog-music-audio.md](catalog-music-audio.md) | Sonilo, ACE-Step, ElevenLabs, licenciamento, formato loop |
| Seedance 2.0 humano real | [seedance-real-human.md](seedance-real-human.md) | Asset verification, group_id, rótulos posicionais |
| Schemas V3 | [schemas-v3.md](schemas-v3.md) | DYNAMICCOMBO, AUTOGROW, ordem widgets_values |
| Templates oficiais | [templates-oficiais.md](templates-oficiais.md) | Onde achar exemplos known-good, grep por NodeType |
| Fal gotchas | [fal-gotchas.md](fal-gotchas.md) | Bloqueio, cold-start, padrões de saída, stub trap |

## Referências
- Bundles que aplicam isto (todos **partner / créditos comfy.org**, zero custom node): `workflows-api/image-edit-nano-banana-2/` · `workflows-api/image-edit-seedream/` (6 edições de foto cada) · `workflows-api/video-person-swap-seedance-2/` (troca de pessoa em vídeo + fluxo de asset de humano real).
- Bundles fal antigos foram **removidos em 2026-08-03**; recuperáveis no git (commit `e1dd237` e anterior).
- Procedimento do comercial: `task-create-commercial-api`. Editar imagem: `task-edit-image` + `knowledge-image-editing`/`knowledge-image-masking`.
- API HTTP do ComfyUI (automação): `knowledge-comfyui-api`. GPU/custo self-hosted: `knowledge-runpod-infra`.
- Fonte de pesquisa: `config/06-ai-agents/comfyui-cloud-first.md` (+ `comfyui-edicao-por-mascara.md`).

## Evolução
Append em `LEARNINGS.md` ao descobrir: um novo nó/endpoint, um seed gate, um modelo que substituiu outro (versão), um
cold-start medido, ou um gotcha de billing. Atribua a fonte (usuário > inferência). Diff git p/ revisão humana.
