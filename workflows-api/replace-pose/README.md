# replace-pose — Trocar a POSE de uma pessoa (por foto OU por texto), por API

> Mantém **rosto, roupa e fundo**; muda só a **pose**. Duas formas: por **FOTO de referência** (copia a pose
> de outra foto) ou por **TEXTO** (você descreve a pose). 4 workflows: 2 por referência + 2 por texto, em 2 IAs.

|  |  |
|---|---|
| 🎯 Faz | Recoloca o corpo da pessoa numa nova pose, preservando identidade, roupa e cenário |
| 🧠 Técnica | Repose por edição multi-referência (foto-guia de pose) **ou** por instrução de texto (Nano Banana Pro / Kontext Multi) |
| 💳 Custo/billing | **fal credits** (Nano Banana Pro e Flux Pro Kontext Multi) |
| 🔌 Provedores/Nós | `NanoBananaPro_fal` · `FluxProKontextMulti_fal` (fal) · `ImageResizeKJ` (KJNodes) · `ImageBatch` (core) |
| 📥 Entrada | **Referência:** BASE (a pessoa) + REFERÊNCIA (foto cuja pose copiar). **Texto:** só a BASE + descrição da pose |
| 📤 Saída | A mesma pessoa/cena, na nova pose |
| 🧩 Modelos | Nano Banana Pro / Gemini 3 · Flux 1.1 Pro Kontext Max (multi) |
| 🧱 Requer | `ComfyUI-fal-API` + `FAL_KEY` · `ComfyUI-KJNodes`. Roda em 8GB (sem GPU) |
| 🟡 Status | Gerado a partir dos padrões known-good (replace-object/replace-environment). Validar nós/chave no 1º load |

📇 **Card de API:** [`API_REFERENCE_replace-pose.md`](API_REFERENCE_replace-pose.md)

## Os arquivos
| Arquivo | Modo | Nó-chave | Quando |
|---|---|---|---|
| `00_LEIA-ME_comece_aqui` | — | — | Guia rápido (qual workflow usar) |
| `01_referencia_nanobanana` 🟢 | foto de pose | `NanoBananaPro_fal` | Copiar a pose de uma foto. **Comece aqui** |
| `02_referencia_kontext` 🟢 | foto de pose | `FluxProKontextMulti_fal` | Idem, backend Kontext, `seed=0` |
| `03_texto_nanobanana` 🟢 | descrição | `NanoBananaPro_fal` | Descrever a pose por texto |
| `04_texto_kontext` 🟢 | descrição | `FluxProKontextMulti_fal` | Idem; `image_2` = cópia da BASE (Kontext exige 2 imgs) |

## Como funciona
- **Referência (01/02):** BASE (a pessoa) + REFERÊNCIA (a foto da pose). O prompt manda copiar **só a pose** da 2ª
  imagem, mantendo identidade/rosto/roupa/fundo da 1ª. Nano empilha as 2 imagens (`ImageResizeKJ`×2 → `ImageBatch`);
  Kontext recebe `image_1`/`image_2` direto.
- **Texto (03/04):** só a BASE; você descreve a pose no prompt (troque `<DESCREVA A POSE>`). Nano usa 1 imagem;
  Kontext duplica a BASE em `image_1` **e** `image_2` (o nó exige 2 imagens).

```
Referência:  BASE ─┬─[Resize]─┐                       (Kontext: BASE→image_1, REF→image_2)
                   │          ├─ ImageBatch ─ Nano/Kontext ─ Save
             REF ──┴─[Resize]─┘
Texto:       BASE ─ Nano (1 img) / Kontext (BASE em image_1+image_2) ─ Save   + prompt descreve a pose
```

## Pré-requisitos
- **Sem GPU.** Tudo roda local; a geração vai pra fal. Precisa de **`FAL_KEY`** (Nano Banana e Kontext são fal).

## Setup
```bash
export FAL_KEY=...      # grava em custom_nodes/ComfyUI-fal-API/config.ini (chmod 600)
bash setup.sh
```
Instala `ComfyUI-fal-API` + `ComfyUI-KJNodes` (+ Manager) e baixa os 5 `.json`.

## Como usar (:8188)
1. **Referência:** abra `01_referencia_nanobanana`. No **BASE** suba a foto da pessoa; no **REFERÊNCIA** suba a foto
   com a pose desejada. Run. Saída em `SaveImage`.
2. **Texto:** abra `03_texto_nanobanana`. Suba a foto no **BASE** e troque `<DESCREVA A POSE>` no prompt
   (ex.: *"standing, arms crossed, head turned slightly left"*). Run.
3. Identidade escorregou? Reforce no prompt *"keep the exact same face and clothing"* e suba a resolução no final.

## Parâmetros não-óbvios
| Onde | Parâmetro | Nota |
|---|---|---|
| `FluxProKontextMulti_fal` | `seed=0` + control `fixed` | **`seed>0` TRAVA o nó.** Não use randomize |
| `FluxProKontextMulti_fal` | `max_quality` | `true` melhora a fidelidade (custa mais); default `false` |
| `NanoBananaPro_fal` | `resolution` | `1K`/`2K`/`4K`. Itere em 1K/2K, finalize em 4K |
| `NanoBananaPro_fal` | sem seed | reprodutível por **âncora**: repita prompt+imagens (BASE = 1ª) |
| Prompt | guia de pose | diga *"use the second image ONLY as a pose guide; do not copy its face/clothes/background"* |

## Validação
- Carregue cada `.json`: **0 nós vermelhos** (senão Manager → Install Missing: fal-API, KJNodes).
- `01`/`02` com BASE+REFERÊNCIA → mesma pessoa na pose da referência; rosto/roupa/fundo preservados.
- `03`/`04` só com BASE + texto → pose conforme descrita; identidade preservada.

## Troubleshooting
| Problema | Solução |
|---|---|
| Copiou o rosto/roupa da referência | reforce *"pose guide only; keep identity/clothing of the first image"* |
| Kontext "travado"/`IN_QUEUE` longo | cold-start, completa sozinho; confira `seed=0` e control `fixed` |
| Nano "devolve a foto" | use `NanoBananaPro_fal` (Gemini 3), nunca `NanoBananaEdit_fal` (Gemini 2.5) |
| Anatomia errada (mãos/membros) | reduza a ambição da pose; finalize em 4K; tente a outra IA |
| Nós vermelhos | Manager → Install Missing (fal-API, KJNodes) |

## Referências
- `knowledge-comfyui-api-nodes` (nós fal, seed gates, repose por API), `knowledge-image-editing` (edição por instrução),
  `knowledge-image-enhance` (ControlNet openpose self-hosted, para a variante GPU).
- Trocar **objeto**: `workflows-api/replace-object/` · trocar **fundo**: `workflows-api/replace-environment/` ·
  trocar **roupa**: `workflows-api/outfit-swap-api/`.
- Combinar roupa+fundo+pose: `workflows-api/replace-suite/` (1 por vez) · `workflows-api/replace-pipeline/` (tudo numa run).
