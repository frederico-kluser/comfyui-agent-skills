# replace-object — Trocar um OBJETO da foto por outro (que você fornece), por API

> Você dá **2 fotos** — a **BASE** (a cena) e a **REFERÊNCIA** (o objeto novo) — e escreve no **prompt** qual objeto
> da BASE trocar. O resto da cena é preservado. 4 workflows: 2 só por prompt e 2 com **seleção de área opcional**.

|  |  |
|---|---|
| 🎯 Faz | Substitui um objeto da imagem pelo objeto de uma foto de referência, mantendo o resto da cena |
| 🧠 Técnica | Edição multi-referência por prompt (Nano Banana Pro / Kontext Multi) + máscara opcional via `ImageCompositeMasked` |
| 💳 Custo/billing | **fal credits** (Nano Banana Pro e Flux Pro Kontext Multi) |
| 🔌 Provedores/Nós | `NanoBananaPro_fal` · `FluxProKontextMulti_fal` (fal) · `ImageResizeKJ`/`GrowMaskWithBlur` (KJNodes) · `ImageCompositeMasked` (core) |
| 📥 Entrada | BASE (a cena) + REFERÊNCIA (o objeto novo) + prompt nomeando o objeto a trocar; **máscara opcional** (03/04) |
| 📤 Saída | A cena com o objeto substituído |
| 🧩 Modelos | Nano Banana Pro / Gemini 3 · Flux 1.1 Pro Kontext Max (multi) |
| 🧱 Requer | `ComfyUI-fal-API` + `FAL_KEY` · `ComfyUI-KJNodes`. Roda em 8GB (sem GPU) |
| 🟡 Status | Gerado a partir dos padrões known-good (outfit-swap-api + mask-edit-cloud). Validar nós/chave no 1º load |

📇 **Card de API:** [`API_REFERENCE_replace-object.md`](API_REFERENCE_replace-object.md)

## Os arquivos
| Arquivo | Modo | Nó-chave | Quando |
|---|---|---|---|
| `00_LEIA-ME_comece_aqui` | — | — | Guia rápido (qual workflow usar) |
| `01_prompt_nanobanana` 🟢 | só prompt | `NanoBananaPro_fal` | Melhor qualidade/relight. **Comece aqui** |
| `02_prompt_kontext` 🟢 | só prompt | `FluxProKontextMulti_fal` | 2 referências exatas, `seed=0` |
| `03_area_nanobanana` 🟡 | prompt **+ área opcional** | Nano Banana + composite | Limitar a troca a uma região pintada |
| `04_area_kontext` 🟡 | prompt **+ área opcional** | Kontext + composite | Idem, backend Kontext |

## Como funciona (03/04 — a parte não-óbvia)
O grupo **"Seleção de área"** (`Conforma` + `GrowMaskWithBlur` + `ImageCompositeMasked`) vem **DESATIVADO (bypass)
por padrão** → rodar sem fazer nada edita a **imagem inteira**, exatamente igual ao 01/02.
Para limitar a troca a uma região: **selecione os 3 nós do grupo → `Ctrl+B`** (ativa) e pinte a máscara no nó BASE.
O `ImageCompositeMasked` cola a **edição completa** (destination) sobre o **original** (source) usando a máscara
**invertida** → só a área pintada muda; o resto fica **pixel-idêntico**. (Bypass devolve a edição completa.)

```
BASE ─┐                                   (grupo opcional, bypass por padrão)
      ├─Resize─┐                   ┌─Conforma─┐
REF ──┴─Resize─┴─Batch─ Nano/Kontext ─┤          ├─ Composite(inv) ─ Save
BASE.MASK (MaskEditor) ──────── GrowMaskWithBlur ─┘
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
1. Abra `01_prompt_nanobanana`. No **BASE** suba a foto da cena; no **REFERÊNCIA** suba a foto do objeto novo.
2. No prompt, troque `<OBJETO A TROCAR>` pelo objeto da BASE (ex.: *"the old wooden chair"*).
3. Run. Saída em `SaveImage`.
4. Quer limitar a uma região? Use `03`/`04`, ative o grupo de máscara (`Ctrl+B`) e pinte o objeto no BASE
   (botão direito no Load Image → **Open in MaskEditor** → pinte com folga → **Save to node**).

## Parâmetros não-óbvios
| Onde | Parâmetro | Nota |
|---|---|---|
| `FluxProKontextMulti_fal` | `seed=0` + control `fixed` | **`seed>0` TRAVA o nó.** Não use randomize |
| `FluxProKontextMulti_fal` | `max_quality` | `true` melhora a fidelidade (custa mais); default `false` |
| `NanoBananaPro_fal` | `resolution` | `1K`/`2K`/`4K`. Suba p/ `4K` no final (mais caro) |
| `NanoBananaPro_fal` | sem seed | reprodutível por **âncora**: repita prompt+imagens |
| `GrowMaskWithBlur` | `expand` / `blur_radius` | cresce e suaviza a borda da máscara (costura macia) |
| `ImageCompositeMasked` | `resize_source` | `true` casa o tamanho automaticamente |

## Validação
- Carregue cada `.json`: **0 nós vermelhos** (senão Manager → Install Missing).
- `01` com base+referência → objeto trocado, resto preservado.
- `03` **sem** ativar a máscara == resultado do `01` (imagem inteira). Ative + pinte → só a região muda.

## Troubleshooting
| Problema | Solução |
|---|---|
| Kontext "travado"/`IN_QUEUE` longo | é cold-start, completa sozinho; confira `seed=0` e control `fixed` |
| Nano "devolve a foto" | use `NanoBananaPro_fal` (Gemini 3), nunca `NanoBananaEdit_fal` (Gemini 2.5) |
| Mudou o resto da cena | use `03`/`04` com máscara, ou seja específico no prompt (nomeie o objeto, não use "transform") |
| Borda dura na região | aumente `blur_radius`/`expand` no `GrowMaskWithBlur` |
| Nós vermelhos | Manager → Install Missing (fal-API, KJNodes) |

## Referências
- `knowledge-comfyui-api-nodes` (nós fal, seed gates), `knowledge-image-editing` (troca de objeto), `knowledge-image-masking` (MaskEditor).
- Inpaint por **texto** (descrever o objeto sem foto de referência) ou seleção por texto: `workflows-api/mask-edit-cloud/`.
- Variante simétrica de fundo: `workflows-api/replace-environment/`.
