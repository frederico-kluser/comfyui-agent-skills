# outfit-swap-api — Trocar a roupa/look por API, mantendo pose, rosto e fundo

> Você + uma roupa → troca **só a roupa**, preservando rosto, pose, corpo e fundo. Duas rotas: **try-on dedicado**
> (`FluxVTONode`, partner BFL, 1 peça exata) ou **outfit completo** (`NanoBananaPro_fal`, Gemini 3, relight para casar).

|  |  |
|---|---|
| 🎯 Faz | Troca a roupa/look de uma foto, mantendo pose/rosto/corpo/fundo |
| 🧠 Técnica | Try-on dedicado (Flux VTON, 1 peça) **ou** outfit completo (Nano Banana Pro) |
| 💳 Custo/billing | **Comfy credits** (Flux VTON, partner) **ou** **fal credits** (Nano Banana Pro) |
| 🔌 Provedores/Nós | `FluxVTONode` (partner BFL) · `NanoBananaPro_fal` (fal) |
| 📥 Entrada | Sua foto + 1 peça (VTON) **ou** look completo (Nano Banana) |
| 📤 Saída | Você com a roupa nova |
| 🧩 Modelos | Flux VTON (BFL) · Nano Banana Pro / Gemini 3 |
| 🧱 Requer | Login `platform.comfy.org` (VTON) · `ComfyUI-fal-API` + `FAL_KEY` + `ComfyUI-KJNodes` (Nano Banana) |
| 🟡 Status | Replicado da máquina local (validar nós/chave) |

📇 **Card de API:** [`API_REFERENCE_outfit-swap.md`](API_REFERENCE_outfit-swap.md)

## Os arquivos
| Arquivo | Rota | Nó | Quando |
|---|---|---|---|
| `01_flux_vton` | partner (Comfy credits) | `FluxVTONode` | Vestir **1 peça exata** (a sua roupa real), single-garment |
| `02_nanobanana_outfit` | fal | `NanoBananaPro_fal` | Trocar o **look completo** (você=image_1, look=image_2), com relight |

## Regra de ouro (3 prompts)
Sem pronomes (nomeie *"the person in image 1"*) · **nunca** "transform" · **nomeie a roupa** (*"a red leather jacket"*).
Duas fotos suas ajudam: **corpo inteiro** (carrega a roupa) + **rosto** (trava identidade). Ver `knowledge-image-editing`.

## Pré-requisitos
- **Sem GPU pesada.** `FluxVTONode` = **login** comfy.org (créditos Comfy). `NanoBananaPro_fal` = **`FAL_KEY`**.

## Setup
```bash
export FAL_KEY=...     # só p/ a rota Nano Banana (02); o setup grava em config.ini a partir do ambiente
bash setup.sh
```
Instala `ComfyUI-fal-API` + `ComfyUI-KJNodes` e baixa os 2 `.json`. **Faça login** (`Settings → User → Sign In`) p/ o `FluxVTONode`.

## Como usar (:8188)
1. **1 peça exata** → `01_flux_vton`: foto da pessoa + a peça (garment). Troca só aquela peça.
2. **Look completo** → `02_nanobanana_outfit`: você = `image_1`, o look = `image_2` (empilhados via `ImageResizeKJ`+`ImageBatch`); resolução 1K, `png`.

## Troubleshooting
| Problema | Solução |
|---|---|
| Mudou rosto/pose | Nomeie a roupa, não use "transform"; no Nano Banana ponha **você primeiro** (âncora) |
| `FluxVTONode` vermelho | É **partner** → faça login comfy.org; tem créditos? `Settings → Credits` |
| Nano Banana "devolve a foto" | Use `NanoBananaPro_fal` (Gemini 3), não `NanoBananaEdit_fal` (Gemini 2.5, fraco) |
| Nós vermelhos | Manager → Install Missing (fal-API, KJNodes) |

## Referências
- `knowledge-image-editing` (troca de roupa por instrução/look), `knowledge-comfyui-api-nodes` (FluxVTON partner vs fal).
- Variante self-hosted (try-off/CatVTON em GPU): `workflows-cloud/scail2-native-3rdparty/`.
