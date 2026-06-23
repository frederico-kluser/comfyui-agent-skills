# replace-environment — Trocar o AMBIENTE/FUNDO (mantendo o sujeito), por API

> Você dá **2 fotos** — a **BASE** (o sujeito) e a **REFERÊNCIA** (o ambiente novo). O sujeito é preservado e
> reiluminado; o fundo vira o novo ambiente. 4 workflows: 2 só por prompt e 2 com **seleção de área opcional**.

|  |  |
|---|---|
| 🎯 Faz | Coloca o sujeito da foto em um novo ambiente (fundo da 2ª imagem), mantendo identidade/pose/roupa |
| 🧠 Técnica | Edição multi-referência por prompt (Nano Banana Pro / Kontext Multi) + máscara opcional via `ImageCompositeMasked` |
| 💳 Custo/billing | **fal credits** (Nano Banana Pro e Flux Pro Kontext Multi) |
| 🔌 Provedores/Nós | `NanoBananaPro_fal` · `FluxProKontextMulti_fal` (fal) · `ImageResizeKJ`/`GrowMaskWithBlur` (KJNodes) · `ImageCompositeMasked` (core) |
| 📥 Entrada | BASE (o sujeito) + REFERÊNCIA (o ambiente novo); **máscara opcional do fundo** (03/04) |
| 📤 Saída | O sujeito no novo ambiente, reiluminado |
| 🧩 Modelos | Nano Banana Pro / Gemini 3 · Flux 1.1 Pro Kontext Max (multi) |
| 🧱 Requer | `ComfyUI-fal-API` + `FAL_KEY` · `ComfyUI-KJNodes`. Roda em 8GB (sem GPU) |
| 🟡 Status | Gerado a partir dos padrões known-good (outfit-swap-api + mask-edit-cloud). Validar nós/chave no 1º load |

📇 **Card de API:** [`API_REFERENCE_replace-environment.md`](API_REFERENCE_replace-environment.md)

## Os arquivos
| Arquivo | Modo | Nó-chave | Quando |
|---|---|---|---|
| `00_LEIA-ME_comece_aqui` | — | — | Guia rápido (qual workflow usar) |
| `01_prompt_nanobanana` 🟢 | só prompt | `NanoBananaPro_fal` | Melhor qualidade/relight. **Comece aqui** |
| `02_prompt_kontext` 🟢 | só prompt | `FluxProKontextMulti_fal` | 2 referências exatas, `seed=0` |
| `03_area_nanobanana` 🟡 | prompt **+ área opcional** | Nano Banana + composite | Travar o sujeito 100% (pintar o fundo) |
| `04_area_kontext` 🟡 | prompt **+ área opcional** | Kontext + composite | Idem, backend Kontext |

## Como funciona (03/04 — a parte não-óbvia)
O grupo **"Seleção de área"** (`Conforma` + `GrowMaskWithBlur` + `ImageCompositeMasked`) vem **DESATIVADO (bypass)
por padrão** → rodar sem fazer nada edita a **imagem inteira**, igual ao 01/02 (o modelo já preserva o sujeito).
Para garantir o sujeito **pixel-idêntico**: **selecione os 3 nós do grupo → `Ctrl+B`** (ativa) e **pinte o FUNDO**
(a área que muda) no nó BASE. O `ImageCompositeMasked` cola a **edição completa** sobre o **original** usando a
máscara **invertida** → só o fundo pintado muda; o sujeito (fora da máscara) fica intacto. (Bypass = edição completa.)

```
BASE ─┐                                   (grupo opcional, bypass por padrão)
      ├─Resize─┐                   ┌─Conforma─┐
REF ──┴─Resize─┴─Batch─ Nano/Kontext ─┤          ├─ Composite(inv) ─ Save
BASE.MASK (pinte o FUNDO) ────── GrowMaskWithBlur ─┘
```

## Pré-requisitos
- **Sem GPU.** Tudo roda local; a geração vai pra fal. Precisa de **`FAL_KEY`**.

## Setup
```bash
export FAL_KEY=...      # grava em custom_nodes/ComfyUI-fal-API/config.ini (chmod 600)
bash setup.sh
```
Instala `ComfyUI-fal-API` + `ComfyUI-KJNodes` (+ Manager) e baixa os 5 `.json`.

## Como usar (:8188)
1. Abra `01_prompt_nanobanana`. No **BASE** suba a foto do sujeito; no **REFERÊNCIA** suba a foto do ambiente novo.
2. O prompt já mantém o sujeito e troca o cenário; ajuste detalhes do ambiente/luz se quiser. Run.
3. Sujeito mudou um pouco? Use `03`/`04`, ative o grupo de máscara (`Ctrl+B`) e **pinte o fundo** no BASE
   (botão direito no Load Image → **Open in MaskEditor** → pinte tudo menos o sujeito → **Save to node**).

## Parâmetros não-óbvios
| Onde | Parâmetro | Nota |
|---|---|---|
| `FluxProKontextMulti_fal` | `seed=0` + control `fixed` | **`seed>0` TRAVA o nó.** Não use randomize |
| `FluxProKontextMulti_fal` | `max_quality` | `true` melhora a fidelidade (custa mais); default `false` |
| `NanoBananaPro_fal` | `resolution` | `1K`/`2K`/`4K`. Suba p/ `4K` no final |
| prompt | relight | descreva a luz do novo cenário (direção/cor) p/ casar o sujeito |
| `GrowMaskWithBlur` | `mask_inverted` | o composite usa a **invertida** (pinte o fundo, não o sujeito) |

## Validação
- Carregue cada `.json`: **0 nós vermelhos**.
- `01` com sujeito+ambiente → sujeito no novo fundo, identidade preservada.
- `03` **sem** máscara == `01`. Ative + pinte o fundo → sujeito fica 100% intacto.

## Troubleshooting
| Problema | Solução |
|---|---|
| Sujeito alterado | use `03`/`04` pintando o fundo; no prompt reforce "keep the subject identical" |
| Iluminação não casa | descreva a luz do ambiente no prompt; Nano Banana relighta melhor |
| Kontext "travado" | cold-start, completa sozinho; confira `seed=0`/control `fixed` |
| Nós vermelhos | Manager → Install Missing (fal-API, KJNodes) |

## Referências
- `knowledge-comfyui-api-nodes` (nós fal, seed gates), `knowledge-image-editing` (troca de fundo), `knowledge-image-masking` (MaskEditor).
- Remover fundo (alpha) em GPU: `workflows-cloud/remove-background/`. Variante de objeto: `workflows-api/replace-object/`.
