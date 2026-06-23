# image-to-video-api — anima 1 imagem + descrição → vídeo (por API)

> **Card Informativo**

| | |
|---|---|
| 🎯 **Faz** | Pega **uma imagem** + um prompt de movimento e gera um **clipe de vídeo** |
| 🧠 **Técnica** | Image-to-Video por **API online** (modelo roda no provedor; sem GPU local) |
| 💳 **Custo/billing** | **fal** (lê `FAL_KEY`) · **partner** (créditos comfy.org, por login) — paga por clipe |
| 🔌 **Provedores/Nós** | `Veo31_fal` · `Veo31Fast_fal` · `SeedanceImageToVideo_fal` · `SeedanceProImageToVideo_fal` · `Kling25TurboPro_fal` · `Kling26Pro_fal` · `ByteDanceImageToVideoNode` · `GrokVideoNode` |
| 📥 **Entrada** | 1 imagem (`LoadImage`) + prompt de movimento (+ 2ª imagem no morph) |
| 📤 **Saída** | `.mp4` em `~/ComfyUI/output/` |
| 🧩 **Modelos** | Veo 3.1 · Seedance 1.0/1.5/Pro · Kling 2.5/2.6 · Grok Imagine |
| 🧱 **Requer** | ComfyUI atual + nó `ComfyUI-fal-API`; `FAL_KEY` e/ou login comfy.org |
| 🟡 **Status** | rascunho a validar com geração real (precisa de `FAL_KEY`/login) |

## Status
🟡 **Rascunho** — JSONs validados (parse + nós resolvidos contra o `/object_info` ao vivo + integridade de
links). Falta o **smoke real** (gerar 1 clipe), que exige `FAL_KEY` e/ou login comfy.org com créditos.

## Pré-requisitos
- ComfyUI rodando (porta 8188). Máquina **8GB basta** — a geração é na nuvem.
- `FAL_KEY` p/ os nós `*_fal` (de `~/ComfyUI/secrets.env`, chmod 600).
- **Login comfy.org** (créditos) p/ os nós partner (`ByteDance…`, `GrokVideoNode`).

## Setup
```bash
FAL_KEY=...  bash setup.sh
```
Instala `ComfyUI-fal-API` (+ Manager + VideoHelperSuite), grava a `FAL_KEY` (do ambiente) e baixa os
workflows p/ `~/ComfyUI/user/default/workflows/image-to-video-api/`. Reinicie o ComfyUI e faça **login**
em platform.comfy.org para os nós partner.

## Como usar
1. Abra **`00_LEIA-ME_comece_aqui`** e escolha o workflow pelo que precisa (tabela abaixo).
2. **`LoadImage`** → sua imagem (o 1º frame). No morph (`14_*`) ligue também a imagem de FIM.
3. Ajuste o **prompt de movimento** (gramática em `01_GUIA_prompt_e_modelos`).
4. **Run**. O clipe vai para `~/ComfyUI/output/`.

### Catálogo
| Arquivo | Modelo / nó | Billing | Quando usar |
|---|---|---|---|
| `10_veo31_premium` | Veo 3.1 (`Veo31_fal`) | fal | Herói: melhor movimento + **áudio**, 1080p |
| `11_veo31_fast` | Veo 3.1 Fast (`Veo31Fast_fal`) | fal | **Iterar barato** antes do premium |
| `12_seedance_rascunho_480p` | Seedance (`SeedanceImageToVideo_fal`) | fal | Rascunho **bem barato** (480p) |
| `13_seedance15_1080p_audio` | Seedance 1.5 Pro (`ByteDanceImageToVideoNode`) | partner | 1080p **com áudio** |
| `14_seedance_pro_morph` | Seedance Pro (`SeedanceProImageToVideo_fal`) | fal | **Morph** entre 2 imagens |
| `15_kling25_movimento` | Kling 2.5 Turbo (`Kling25TurboPro_fal`) | fal | Ação com **muito movimento** |
| `16_kling26_audio` | Kling 2.6 Pro (`Kling26Pro_fal`) | fal | Animar **com áudio** |
| `18_grok_imagine` | Grok Imagine (`GrokVideoNode`) | partner | Alternativa **barata** |

## Os 2 padrões de saída (importa!)
- **Padrão A — nós fal (`*_fal`)**: saída é uma **URL** → cadeia `LoadVideoURL → CreateVideo → SaveVideo`.
  ⚠️ Essa cadeia pega só os **frames** e **perde o áudio**. Para manter o áudio, **baixe a URL** que o nó
  fal retorna (o texto de saída do nó).
- **Padrão B — nós partner**: saída é **VIDEO** nativo → vai direto no `SaveVideo` (**áudio preservado**).

## Parâmetros não-óbvios
| Campo | Vale | Nota |
|---|---|---|
| **prompt** | direção do MOVIMENTO | `plano+câmera+lente → sujeito → ação → cenário → luz → áudio`. Negativos **em prosa** (Veo/Seedance não têm campo negative). |
| **seed** | — | `Veo*`/`Kling*_fal`/`Kling26` **não têm seed** (identidade vem da imagem). `Seedance…_fal` tem (`-1`=aleatório). Partner: seed só decide **re-rodar**. |
| **resolution/duration** | 480p→1080p · 4–12s | mais alto = mais crédito. Itere barato, finalize alto. |
| **generate_audio** | bool | só Veo 3.1, Kling 2.6 e Seedance 1.5-pro geram áudio. |
| **last_frame / end_image / tail_image** | IMAGEM | opcional — define o último frame (morph/encadeamento). |

## Validação
- ✅ `python -m json.tool` em todos os `.json` (parse).
- ✅ Todos os `class_type` existem no `/object_info` ao vivo.
- ✅ Integridade de links (slots/tipos).
- ⏳ Smoke real: rode `10_veo31_premium` com `FAL_KEY` setada e confira o `.mp4`.

## Troubleshooting
- **Nó vermelho**: Manager → *Install Missing Custom Nodes* (precisa do `ComfyUI-fal-API`).
- **Nó fal "travado" sem barra**: normal — fal **bloqueia** sem progress bar; cold-start ~min em `IN_QUEUE`.
- **Partner pede login/sem crédito**: Settings > User > Sign In (platform.comfy.org).
- **Vídeo sem áudio**: você usou um nó fal (padrão A) — baixe a URL original p/ manter o áudio.

## Referências
- Cards por nó: [`API_REFERENCE_image-to-video.md`](API_REFERENCE_image-to-video.md)
- Conhecimento dos nós de API: skill `knowledge-comfyui-api-nodes`
- Vídeo→vídeo (transformar um vídeo): [`../video-to-video-api/`](../video-to-video-api/)
