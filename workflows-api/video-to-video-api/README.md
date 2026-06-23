# video-to-video-api — transforma 1 vídeo + descrição → vídeo (por API)

> **Card Informativo**

| | |
|---|---|
| 🎯 **Faz** | Pega **o seu vídeo** + um prompt e o **transforma**: re-estiliza, anima personagem ou estende |
| 🧠 **Técnica** | Video-to-Video por **API online** (3 modos: restyle · motion-transfer · extend) |
| 💳 **Custo/billing** | **fal** (`FAL_KEY`) · **partner** (créditos comfy.org) — paga por clipe/segundo |
| 🔌 **Provedores/Nós** | `RunwayAleph2VideoToVideoNode` · `GrokVideoEditNode` · `KlingOmniVideoToVideoEdit_fal` · `Wan2214b_animate_move/replace_character_fal` · `KlingV3ProMotionControl_fal` · `GrokVideoExtendNode` · `KlingVideoExtendNode` · `ViduExtendVideoNode` |
| 📥 **Entrada** | 1 vídeo (`LoadVideo`) + prompt (+ `LoadImage` do personagem nos modos de animação) |
| 📤 **Saída** | `.mp4` em `~/ComfyUI/output/` |
| 🧩 **Modelos** | Runway Aleph · Grok · Kling Omni/V3/Extend · **Wan 2.2 Animate** · Vidu |
| 🧱 **Requer** | ComfyUI atual + `ComfyUI-fal-API`; `FAL_KEY` e/ou login comfy.org |
| 🟡 **Status** | rascunho a validar com geração real (precisa de `FAL_KEY`/login) |

## Status
🟡 **Rascunho** — JSONs validados (parse + nós resolvidos contra o `/object_info` ao vivo + integridade de
links). Falta o **smoke real**. Nos nós de **extend dinâmico** (`30_extend_grok`, `32_extend_vidu`) confira
o dropdown **model** ao abrir (combo dinâmico).

## Pré-requisitos
- ComfyUI rodando (8188). Máquina **8GB basta** — a geração é na nuvem.
- `FAL_KEY` p/ os nós `*_fal`; **login comfy.org** (créditos) p/ os nós partner (Runway/Kling/Grok/Vidu).

## Setup
```bash
FAL_KEY=...  bash setup.sh
```
Instala `ComfyUI-fal-API` (+ Manager + VideoHelperSuite), grava a `FAL_KEY` e baixa os workflows p/
`~/ComfyUI/user/default/workflows/video-to-video-api/`. Reinicie e faça **login** comfy.org.

## Como usar
1. Abra **`00_LEIA-ME_comece_aqui`** e escolha o **modo** (guia detalhado em `01_GUIA_modos_e_entrada`).
2. **`LoadVideo`** → seu vídeo (botão de upload). Nos modos de **animar personagem**, ligue também
   **`LoadImage`** (o sujeito).
3. Ajuste o **prompt** e **Run**.

### Catálogo (por modo)
**🅰️ Restyle / editar** (mantém o movimento, muda o look)
| Arquivo | Nó | Billing | Nota |
|---|---|---|---|
| `10_restyle_runway_aleph` | `RunwayAleph2VideoToVideoNode` | partner | **Melhor** restyle in-context; vídeo 2–30s |
| `11_edit_grok` | `GrokVideoEditNode` | partner | Clipe **≤8.7s / 50MB** |
| `12_edit_kling_omni` | `KlingOmniVideoToVideoEdit_fal` | fal | Editar + inserir **elementos** por referência |

**🅱️ Motion-transfer / animar personagem** (segue um vídeo-guia) — *substituto-API do SCAIL-2*
| Arquivo | Nó | Billing | Nota |
|---|---|---|---|
| `20_animate_wan_move` | `Wan2214b_animate_move_character_fal` | fal | Anima a **imagem** do sujeito p/ seguir o vídeo |
| `21_animate_wan_replace` | `Wan2214b_animate_replace_character_fal` | fal | **Troca** a pessoa do vídeo |
| `22_motion_kling_v3` | `KlingV3ProMotionControl_fal` | fal | Motion-control (image + video) |

**🅲 Estender / continuar**
| Arquivo | Nó | Billing | Nota |
|---|---|---|---|
| `30_extend_grok` | `GrokVideoExtendNode` | partner | Continua **um arquivo** (2–15s) |
| `31_extend_kling` | `KlingVideoExtendNode` | partner | Encadeia por **`video_id`** (gera base + estende) |
| `32_extend_vidu` | `ViduExtendVideoNode` | partner | Continua um arquivo (+ `end_frame` opcional) |

## Os 2 padrões de saída (importa!)
- **Padrão A — nós fal (`*_fal`)**: saída **URL** → `LoadVideoURL → CreateVideo → SaveVideo` (⚠️ perde áudio;
  baixe a URL p/ manter). Aqui: `KlingOmni…`, `Wan2214b_animate_*`, `KlingV3…`.
- **Padrão B — nós partner**: saída **VIDEO** → `SaveVideo` direto (**áudio ok**). Aqui: Runway Aleph, Grok
  edit/extend, Kling extend, Vidu extend.

## Entrada de vídeo & imagem
- O vídeo entra pelo core **`LoadVideo`** (saída **VIDEO**) → input `video` do nó.
- **Exceção:** `KlingVideoExtendNode` **não** aceita arquivo — só **`video_id`** de uma geração Kling; por isso
  `31_extend_kling` gera um base (`KlingImage2VideoNode`) e o estende.
- Nos modos 🅱️, o personagem entra por **`LoadImage`** → input `image`.

## Parâmetros não-óbvios
| Campo | Nota |
|---|---|
| **Wan Animate** `resolution` | `480p`/`580p`/`720p`; `turbo` rápido; defaults bons (`seed` 24, `shift` 8, 20 steps). `input_video_url` = alternativa ao Load Video. |
| **Runway Aleph** `keyframes`/`prompt_images` | imagens-guia (até 5) — use **uma OU outra**, não as duas. |
| **Kling Omni** `keep_audio` / **Kling V3** `keep_original_sound` | mantêm o áudio original. |
| **extend dinâmico** (`model`) | `GrokVideoExtendNode`/`ViduExtendVideoNode` usam combo dinâmico → confira o dropdown ao abrir. |

## Validação
- ✅ parse (`json.tool`) · ✅ nós existem no `/object_info` · ✅ integridade de links.
- ⏳ Smoke real: rode `10_restyle_runway_aleph` (login) ou `20_animate_wan_move` (`FAL_KEY`) e confira o `.mp4`.

## Troubleshooting
- **Nó vermelho**: Manager → *Install Missing Custom Nodes* (`ComfyUI-fal-API`).
- **Nó fal "travado"**: bloqueia sem barra; cold-start ~min em `IN_QUEUE`.
- **Partner pede login/crédito**: Settings > User > Sign In (platform.comfy.org).
- **Grok edit recusa o vídeo**: passou de **8.7s/50MB** — corte antes ou use Runway Aleph.
- **Sem áudio**: nó fal (padrão A) — baixe a URL original.

## Referências
- Cards por nó: [`API_REFERENCE_video-to-video.md`](API_REFERENCE_video-to-video.md)
- Conhecimento dos nós de API: skill `knowledge-comfyui-api-nodes`
- Imagem→vídeo (animar 1 foto): [`../image-to-video-api/`](../image-to-video-api/)
- Equivalente **self-hosted** (SCAIL-2 em GPU): [`../../workflows-cloud/`](../../workflows-cloud/)
