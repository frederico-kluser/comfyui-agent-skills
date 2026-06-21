# commercial-ondokai — Comercial de ~30s 100% por API (sem GPU pesada)

> Spot de **~30s, 16:9**, produzido inteiramente com **APIs online** dentro do ComfyUI: protagonista
> sintético ancorado em **Nano Banana Pro** (Gemini 3) e cada cena animada com **Veo 3.1** — rodando numa
> máquina de **8 GB de VRAM** que só faz orquestração, upload e download. A geração pesada acontece na nuvem.

|  |  |
|---|---|
| 🎯 Faz | Comercial de ~30s (9 cenas) com protagonista sintético consistente |
| 🧠 Técnica | Âncora de identidade (Nano Banana Pro) → keyframe→vídeo (Veo 3.1) → extensão dirigida → ColorMatch → concat |
| 💳 Custo/billing | **fal credits** (Veo 3.1, Nano Banana Pro, Seedance) + **Comfy login** (nós Kling partner). Sem GPU local pesada |
| 🔌 Provedores/Nós | `NanoBananaPro_fal` · `Veo31_fal` · `SeedanceImageToVideo_fal` / `SeedanceProImageToVideo_fal` · `KlingImage2VideoNode` / `KlingVideoExtendNode` / `KlingCameraControlI2VNode` (partner) |
| 📥 Entrada | 1 frase de identidade do `<<PROTAGONISTA>>` + (opcional) foto-âncora real; prompts por cena |
| 📤 Saída | 9 clipes `.mp4` (h264) → 1 master 16:9 concatenado via `ffmpeg` |
| 🧩 Modelos | Veo 3.1 (vídeo) · Nano Banana Pro / Gemini 3 (imagem) · Kling v2.1 · Seedance (1.5/Pro) |
| 🧱 Requer | `ComfyUI-fal-API` + `FAL_KEY` · login `platform.comfy.org` p/ nós Kling · KJNodes + VideoHelperSuite |
| 🟡 Status | Replicado da máquina local (validar `FAL_KEY`/login no ComfyUI) |

📇 **Card de API (inputs/params por nó):** [`API_REFERENCE_commercial.md`](API_REFERENCE_commercial.md)

> ⚠️ **Por que API e não local?** Os modelos de ponta (Veo 3.1, Nano Banana Pro, Kontext Max) **não cabem
> em 8 GB** em precisão cheia, e a regra do projeto é *"nada de GGUF/quantizado/inferior local"*. A nuvem
> entrega um modelo **melhor e mais rápido**; a 4070 só faz máscara/composição/upload. Ver `knowledge-comfyui-api-nodes`.

## Os 19 arquivos (abra cada um no ComfyUI; o `MarkdownNote` de topo explica o nó)

| Arquivo | Papel | Nó(s) de geração |
|---|---|---|
| `00_LEIA-ME_comece_aqui` | Índice + fluxo + **regra de identidade** + custo | (só nota) |
| `01_GUIA_prompts_e_camera` | **Gramática Veo 3.1** + vocabulário de câmera + negativos + ffmpeg | (só nota) |
| `02_GLOSSARIO_configuracoes` | O que cada campo faz, em PT básico | (só nota) |
| `10_ANCORA_protagonista` | Gera+salva o protagonista uma vez, **trava a identidade** | `NanoBananaPro_fal` |
| `11_cena01_coldopen` … `19_cena09_logo` | As 9 cenas (beats) | `NanoBananaPro_fal` → `Veo31_fal` |
| `20_FERRAMENTA_rascunho_barato` | Testa timing barato antes de gastar Veo | `SeedanceImageToVideo_fal` (480p) |
| `30_MODELO_cena_nova_keyframe_veo` | Molde p/ inventar cena nova (keyframe→Veo) | `NanoBananaPro_fal` + `Veo31_fal` |
| `31_MODELO_cena_camera_kling` | Cena nova com **câmera numérica precisa** | `KlingCameraControlI2VNode` + `KlingCameraControls` |
| `40_ESTENDER_A_veo_handoff` | Estende: último frame → próximo Veo (portável) | 2× `Veo31_fal` + `GetImageRangeFromBatch` |
| `41_ESTENDER_B_kling_nativo` | Estensão nativa encadeada (Kling) | `KlingImage2VideoNode` + 2× `KlingVideoExtendNode` |
| `42_ESTENDER_C_seedance_barato` | Estensão barata p/ rascunho de timing | 2× `SeedanceProImageToVideo_fal` |

**Os 9 beats (roteiro):** 1 tédio do escritório · 2 gaiola da repetição · 3 a faísca *(still)* · 4 o estalo/morph
· 5 herói diante do node-graph · 6 roda sozinho · 7 santuário local-first *(still)* · 8 libertação · 9 logo Ondokai *(still)*.
Tema: uma pessoa libertada por uma ferramenta de automação local-first baseada em nós. (Cenas 3, 7, 9 = imagem parada.)

## Pipeline

```
10_ANCORA  ─NanoBananaPro_fal→ ondokai_anchor.png  ┐ (identidade canônica, salva 1×)
                                                    │ wired no input `images` de cada cena
Para cada beat (11..19):                            ▼
  NanoBananaPro_fal(prompt + <<PROTAGONISTA>> + anchor) → keyframe 4K 16:9
     └─ Veo31_fal(first_frame[, last_frame p/ morph]) → 8s 1080p → LoadVideoURL → CreateVideo(24fps) → SaveVideo
  (cena 14 = morph: 2 keyframes START+END → first_frame + last_frame)
  (cenas 3/7/9 = só keyframe, sem Veo)

Cena longa (>8s) → 40/41/42 (extensão dirigida, ação NOVA por segmento)
Cor entre clipes  → ColorMatch (hm-mkl-hm, 0.4) de CADA clipe contra UM hero frame canônico
Master            → ffmpeg -f concat -r 24 -c:v libx264 -pix_fmt yuv420p ondokai.mp4
```

## Pré-requisitos
- **Sem GPU pesada.** Roda na máquina local (8 GB) ou num pod pequeno só para hospedar o ComfyUI.
- **`FAL_KEY`** (fal.ai) para `*_fal` (Veo 3.1, Nano Banana Pro, Seedance). **Login comfy.org** p/ os nós Kling (partner).
- Nós: `ComfyUI-fal-API` (gokayfem), `ComfyUI-KJNodes`, `ComfyUI-VideoHelperSuite`. Kling = **core/partner** (sem instalar).
- Custo/chaves e a decisão API-vs-self-hosted: **`knowledge-comfyui-api-nodes`**. Procedimento ponta-a-ponta: **`task-create-commercial-api`**.

## Setup
```bash
export FAL_KEY=...            # NUNCA versionar; o setup grava em config.ini (chmod 600) a partir do ambiente
bash setup.sh
```
Instala os 3 custom nodes, configura a `FAL_KEY` no `ComfyUI-fal-API/config.ini` (se `FAL_KEY` estiver no ambiente)
e baixa os 19 `.json` para `ComfyUI/user/default/workflows/`. **Faça login** em `Settings → User → Sign In`
(`platform.comfy.org`) para os nós Kling. Reinicie o ComfyUI.

## Como usar (:8188)
1. **Âncora primeiro** — abra `10_ANCORA_protagonista`, troque a frase `<<PROTAGONISTA — ...>>` pela descrição do
   seu protagonista, rode. Salva `ondokai_anchor.png`. **Essa frase, idêntica, vai em TODOS os prompts.**
2. **Rascunho barato** (opcional) — `20_FERRAMENTA_rascunho_barato` (Seedance 480p) para testar o timing/câmera de um beat antes de gastar Veo.
3. **Cada cena** (`11`..`19`) — confira que o `images` recebe a âncora; escreva o prompt na **gramática Veo 3.1** (abaixo); rode.
4. **Cena nova** — duplique `30_MODELO...veo` (keyframe→Veo) ou `31_MODELO...kling` (câmera numérica).
5. **Cena longa** — use `40/41/42` (ver "Extensão").
6. **Cor** — passe cada clipe por `ColorMatch` (hm-mkl-hm, **0.4**) contra **um** hero frame canônico (não contra o clipe anterior → evita deriva acumulada).
7. **Master** — baixe os `.mp4` e concatene: `ffmpeg -f concat -safe 0 -i lista.txt -r 24 -c:v libx264 -pix_fmt yuv420p ondokai.mp4`.

## Gramática de prompt Veo 3.1 (cinematografia primeiro)
`[plano + movimento de câmera + lente] + [sujeito + figurino] + [ação + física/timing] + [cenário + hora do dia] + [estilo: filme/grade/luz] + [áudio]`
```
[SHOT_TYPE + CAMERA_MOVE + LENS], <<PROTAGONISTA — mesma frase de identidade em TODA cena>>,
<AÇÃO com timing>, in <CENÁRIO + hora do dia + atmosfera>, lit by <ILUMINAÇÃO>.
Style: <película / grão / color grade>.
Audio: dialogue — "<fala exata ou none>"; SFX: <som>; Ambient: <paisagem sonora>.
```
- **Câmera — UM movimento por plano** (dolly in/out, truck L/R, orbit, pedestal, push-in, locked-off, rack focus…). Movimentos conflitantes degradam a saída.
- **Varie a câmera por beat** (cold open = dolly-in 35mm; gaiola = truck lateral anamórfico; estalo = locked-off morph; herói = orbit; etc.).
- **Negativos:** `Veo31_fal` **não tem campo negative** → escreva os negativos em prosa no positivo, OU use um nó com negative (`KlingImage2VideoNode`, `SeedanceProImageToVideo_fal`). Bloco padrão: *no morphing, no warping, distorted hands, extra fingers, flickering textures, face morphing, jitter, camera shake, changing wardrobe color, identity drift*.

## Regra de identidade (a mais importante)
O protagonista é **sintético**. Para parecer a MESMA pessoa em todas as cenas: **(a)** a imagem-âncora vai no input
`images` de cada keyframe **e (b)** a frase `<<PROTAGONISTA — ...>>` é **idêntica em todos os prompts**. Troque a frase
**uma vez** e replique-a verbatim. **Nano Banana Pro não tem seed** → a identidade é travada por âncora+frase
(troque para `NanoBanana2_fal`/`GeminiNanoBanana2` se precisar de seed reprodutível). Sempre **nomeie figurino/props**
("gray hoodie, round glasses"). Rostos reais podem ser bloqueados por moderação → use o protagonista sintético.

## Extensão (vídeo > 8 s — ação NOVA por segmento)
| Método | Arquivo | Como | Quando |
|---|---|---|---|
| **A — Veo handoff** | `40_ESTENDER_A_veo_handoff` | `GetImageRangeFromBatch(-1)` pega o último frame → vira `first_frame` do próximo `Veo31_fal` com prompt novo | Portável entre modelos; qualidade Veo |
| **B — Kling nativo** | `41_ESTENDER_B_kling_nativo` | `KlingImage2VideoNode` → `KlingVideoExtendNode` ×N (encadeia `video_id`) | Extensão nativa contínua |
| **C — Seedance barato** | `42_ESTENDER_C_seedance_barato` | `SeedanceProImageToVideo_fal` com `end_image` + handoff de último frame | Rascunho de timing barato |

## Parâmetros (resumo — detalhe nó-a-nó em `API_REFERENCE_commercial.md`)
| Onde | Campo | Valor (comercial) | Nota |
|---|---|---|---|
| `Veo31_fal` | duration / resolution | `8s` / `1080p` | durações 4/6/8s; 720p p/ teste; **24 fps** |
| `Veo31_fal` | generate_audio | `true` nos moldes; `false` nas cenas | ⚠️ a cadeia `LoadVideoURL→CreateVideo` perde o áudio nativo (baixe a URL original p/ manter) |
| `NanoBananaPro_fal` | aspect / resolution | `16:9` / `4K` | sem seed (trava por âncora) |
| `KlingCameraControls` | eixos | só **1 eixo ≠ 0** (ex.: zoom=5) | range −10..+10 |
| `Kling*` / `Seedance*` | cfg_scale | `0.5`–`0.8` | ~0.5 equilibrado |
| `Seedance` (draft) | resolution | `480p` | rascunho barato de timing |

## Custo: itere barato, finalize caro
Rascunho de timing → **Seedance 480p** (`20_FERRAMENTA`). Endpoints **warm** (Nano Banana Pro / Kontext, ~30–60 s) p/
iterar. Final → **Veo 3.1 1080p**. fal cobra por chamada e os nós `*_fal` **bloqueiam sem barra de progresso** (cold-start
pode ficar minutos em `IN_QUEUE` e ainda completar) — ver Troubleshooting.

## Validação
Gere a âncora, depois 1 cena curta, confira a consistência de identidade (rosto/figurino) e a cor entre 2 clipes.
Só então rode as 9 cenas. Erros → `task-debug-generation` + `knowledge-comfyui-api-nodes` (§gotchas).

## Troubleshooting
| Problema | Solução |
|---|---|
| Nó `*_fal` parece travado, sem progresso | Normal: fal **bloqueia sem barra**; cold-start ~minutos em `IN_QUEUE`. Veja `comfyui logs`; cancele só reiniciando o servidor |
| "Failed to upload video" | Causa real (FAL_KEY/arquivo) só aparece no **console do servidor**; confira a `FAL_KEY` |
| Identidade muda entre cenas | Âncora no `images` de TODA cena + frase `<<PROTAGONISTA>>` idêntica + nomeie figurino |
| Nano Banana "devolve a foto sem editar" | Você está num nó **fraco** (`NanoBananaEdit_fal` = Gemini 2.5). Use `NanoBananaPro_fal` (Gemini 3) |
| Vídeo sem áudio | `LoadVideoURL→CreateVideo` extrai só frames; baixe a URL original (STRING) do Veo |
| Cor "deriva" ao longo do comercial | `ColorMatch` contra **um** hero frame canônico, não contra o clipe anterior |
| Rosto real bloqueado | Moderação do Veo; use o protagonista sintético (a âncora) |
| Nós vermelhos | Manager → Install Missing Custom Nodes (fal-API, KJNodes, VHS); Kling exige **login** comfy.org |
| 1:1 sai errado | 1:1 não é saída oficial do Veo → gere 16:9 e recorte no post |

## Referências
- **Conhecimento:** `knowledge-comfyui-api-nodes` (catálogo de nós/provedores, seed gates, chaves) · `knowledge-image-editing`/`knowledge-image-masking` (para `mask-edit-cloud`).
- **Procedimento:** `task-create-commercial-api` (pipeline ponta-a-ponta) · variante self-hosted: `task-create-commercial`.
- **Fontes:** os `MarkdownNote` em `00/01/02` (gramática completa) · doc de pesquisa `config/06-ai-agents/comfyui-cloud-first.md`.
- Custom node fal: [ComfyUI-fal-API](https://github.com/gokayfem/ComfyUI-fal-API).
