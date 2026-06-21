---
name: task-edit-image
description: >-
  Orquestra a edição de uma imagem fim-a-fim: selecionar a região (máscara manual/semântica/automática),
  editar (inpaint por máscara OU instrução textual Kontext/Qwen) e recolar (Inpaint Stitch no grafo ou
  composição Python). Use sempre que o pedido for editar/alterar/retocar uma imagem, trocar ou remover um
  objeto, mudar cor/fundo, ou "edite essa foto" — mesmo sem citar a skill. Decide a técnica e a cadeia de
  knowledge skills; termina com o passo de evolução. Não é para gerar do zero nem para vídeo.
metadata:
  version: 0.1.0
  type: task
---
# Tarefa — Editar uma Imagem (fim-a-fim)

Leva um pedido de edição a um resultado, escolhendo a técnica e orquestrando as knowledge skills. Não
duplica o conhecimento delas — carregue conforme o passo.

## Quando usar
"Edite/altere/retoque a foto", "troque/remova o objeto", "mude a cor/o fundo", "coloque X no lugar de Y".
Selecionar só a máscara → `knowledge-image-masking`; só montar o grafo → `task-build-workflow`.

## Decisão da técnica (escolha a mais direta)
1. **Edição global por instrução, sem máscara** ("deixe noturno", "troque a jaqueta") → **Flux Kontext** ou
   **Qwen-Image-Edit** (`workflows-cloud/instruction-edit-kontext` / `qwen-image-edit`). Mais rápido quando não precisa de precisão.
2. **Edição cirúrgica de uma região** ("troque só este objeto") → **máscara + inpaint + recolar**
   (`workflows-cloud/inpaint-region-cropstitch`). Use quando a precisão importa.
3. **Estender** → `workflows-cloud/outpaint-extend`. **Tirar fundo** → `workflows-cloud/remove-background`.

## Procedimento (caso 2 — região)
1. **Selecione a região** (→ `knowledge-image-masking`): MaskEditor (manual), SAM3/Florence/Grounding DINO (por texto), ou Impact Pack (rostos/mãos).
2. **Edite** (→ `knowledge-image-editing`): `Inpaint Crop` → `InpaintModelConditioning` + KSampler (denoise 0.45-0.7, Flux Fill/SDXL-inpaint) → `Inpaint Stitch`. Bordas → `Gaussian Blur Mask` + `Differential Diffusion`.
3. **Recole** (→ `knowledge-comfyui-api` se fora do ComfyUI): `Inpaint Stitch`/`ImageCompositeMasked` no grafo, ou `compose.py` (alpha blend p/ fidelidade / seamlessClone p/ harmonizar cor-luz) via código.
4. **Valide**: rode em resolução nativa (1024); confira bordas e desvio de cor (Color Match em Flux). Erros → `task-debug-generation`.

## Gotchas
- Modelo de inpaint dedicado + `InpaintModelConditioning` = denoise<1 sem incoerência. Máscara 100% opaca (#FFFFFF) no Crop&Stitch.
- "Dupla cabeça" → `rescale_factor`<1. Área cinza → não use `VAE Encode for Inpainting` com denoise<1.
- Para fidelidade de pixels exata, prefira alpha blend feathered ao seamlessClone.

## <evolution> (ao concluir)
1. A edição ficou boa (sem bordas/desvio, região coerente)? Só então persista.
2. Persista: técnica/modelo que funcionou por tipo de edição, combinação de máscara+denoise, anti-padrão. Ignore o óbvio/volátil.
3. Append em `LEARNINGS.md` (data + fonte). Destile no corpo se recorrente (`version++`). Técnica nova recorrente → `meta-evolution`.
4. Diff git p/ revisão — não faça merge sozinho.
