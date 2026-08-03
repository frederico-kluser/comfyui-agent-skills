# Schemas V3 — COMFY_DYNAMICCOMBO_V3 / COMFY_AUTOGROW_V3

Nós novos (Seedance 2.0, `BatchImagesNode`, `ByteDanceSeedreamNodeV2`, `OpenAIGPTImageNodeV2`) usam schema V3.

## DYNAMICCOMBO
Os params vivem **dentro** da opção de `model` escolhida.
- `widgets_values[0]` = a **chave** da opção (ex.: `"Seedance 2.0"`).
- O resto segue os params **daquela** opção.
- Trocar de opção troca a lista de widgets.

## AUTOGROW
Slots nomeados **`<grupo>.<prefixo><n>`**:
- `images.image0…` (`BatchImagesNode`, **0-indexado**).
- `model.reference_images.image_1…` (Seedance, **1-indexado**).
- O frontend mantém **um slot livre a mais** (`"shape": 7`).
- Widget convertido em input vira socket com o nome completo (ex.: `model.prompt`) e **assume o slot 0**.

## ⚠️ Ordem dos widgets_values ≠ ordem do /object_info
O frontend insere `control_after_generate` **logo depois do `seed`**.
Reconstruir o nó fora dessa ordem embaralha os widgets **em silêncio**.
**Copie a ordem de um template oficial.**

## Referências
- Templates oficiais → [templates-oficiais](templates-oficiais.md)
- Seedance 2.0 → [seedance-real-human](seedance-real-human.md)
