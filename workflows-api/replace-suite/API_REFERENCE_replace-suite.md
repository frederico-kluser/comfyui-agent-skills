# API Reference — replace-suite

3 blocos independentes (ROUPA · FUNDO · POSE) num arquivo. Mesmos nós dos bundles `replace-*`/`outfit-swap-api`.
Detalhe de cada nó: ver os cards de `replace-object` / `replace-pose`. Aqui ficam as **convenções do bundle**.

## Estrutura
- Cada bloco: `LoadImage(BASE)` → [grupo **Referência** opcional] → modelo (`NanoBananaPro_fal` ou `FluxProKontextMulti_fal`) → `SaveImage`.
- **Nano:** grupo Referência = `LoadImage(REF)` + `ImageResizeKJ` + `ImageBatch` (em **mode 4 / bypass** por padrão). Bypass → `ImageBatch` repassa a `image1` (a BASE) → **modo TEXTO**. Ativo → batch BASE+REF → **modo FOTO**.
- **Kontext:** `image_1` = BASE, `image_2` = BASE (cópia → **modo TEXTO**). Para **modo FOTO**, ligue o `IMAGE` do `LoadImage(REF)` em `image_2`.

## Liga/desliga de bloco
- O nó **`SaveImage`** é o interruptor: `mode 0` = ativo (executa); `mode 4` = bypass (bloco inteiro não roda).
- Default: **ROUPA `Salvar` ativo**; **FUNDO e POSE `Salvar` em bypass**. Rode 1 por vez (ative só um `Salvar`).

## Seed gate (Kontext)
- `FluxProKontextMulti_fal`: `seed=0` + `control_after_generate='fixed'`. **`seed>0` TRAVA.** `image_1` e `image_2` obrigatórias.

## Nano sem seed
- `NanoBananaPro_fal` não tem seed (reprodutível por âncora: a 1ª imagem do batch = BASE).

## Prompts por etapa (TEXTO padrão; versões de referência p/ colar no modo FOTO)
- **ROUPA — texto:** "*Change ONLY the clothing/outfit to: `<DESCREVA A ROUPA>`. Preserve the exact face, hair, body, pose and background...*"
- **ROUPA — referência:** "*...Change ONLY the clothing to the outfit shown in the SECOND image: replicate its garments, colors, patterns, logos and fabric faithfully...*"
- **FUNDO — texto:** "*Replace ONLY the background/scene behind the subject with: `<DESCREVA O FUNDO>`. Keep the subject's identity, face, pose, body and clothing...*"
- **FUNDO — referência:** "*Place the main subject from the first image into the new environment shown in the second image...*"
- **POSE — texto:** "*Change the body pose to: `<DESCREVA A POSE>`. Keep identity, face, clothing, background...*"
- **POSE — referência:** "*Repose the person from the first image to match the pose of the person in the second image; use it only as a pose guide...*"
