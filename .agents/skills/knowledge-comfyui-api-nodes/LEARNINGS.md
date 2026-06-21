# LEARNINGS — knowledge-comfyui-api-nodes

> Memória episódica desta skill. Append-only (data + fonte: usuário > inferência).
> `meta-consolidation` deduplica/promove/poda. Promova ao corpo o que virar padrão estável.

## 2026-06-20 — Gênese: nós de API online (replicado da máquina local)
- **Contexto**: o ComfyUI local (:8188, RTX 4070 8GB) roda a stack inteira por API. Skill destilada da análise do `/object_info` (1775 nós), dos workflows salvos e dos docs `config/06-ai-agents/comfyui-cloud-first.md` + `comfyui-edicao-por-mascara.md`.
- **Aprendizado**: (1) duas famílias coexistem — **partner** nativos (`partner/*`, Comfy credits, login) e **fal** (`*_fal`, `FAL_KEY`). (2) Os modelos bons estão no **fal** (Veo 3.1, Nano Banana Pro/Gemini 3, Flux Ultra/Kontext Max); vários partner são versões antigas (`GeminiImageNode`=Gemini 2.5, `VeoVideoGenerationNode`=Veo 2). (3) **Seed gates** divergem e ERRAR TRAVA: `FluxPro1Fill_fal`=0 (−1 trava), Kontext=0, Ultra/Upscaler=−1, Veo/NanoBananaPro=sem seed. (4) `NanoBananaEdit_fal` (Gemini 2.5) é o fraco ("devolve a foto"); `NanoBananaPro_fal` (Gemini 3) é o bom. (5) Nós fal **bloqueiam sem barra**; cold-start ~min em `IN_QUEUE`. (6) Chaves em `~/ComfyUI/secrets.env`, **nunca** `~/.secrets`.
- **Fonte**: usuário (docs + máquina local) + inferência (análise do `/object_info`).
- **Ação**: corpo da SKILL.md já cobre. Revalidar nomes de nó quando `ComfyUI-fal-API` atualizar (mudam de versão).

_(novas entradas abaixo)_
