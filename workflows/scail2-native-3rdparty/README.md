# scail2-native-3rdparty — SCAIL-2 nativo (workflow de TERCEIROS)

> **Autoria de terceiros (comunidade).** O `scail2-native-3rdparty.json` foi **fornecido pelo usuário** e está
> **preservado sem edição** (grafo original intacto, incluindo a `MarkdownNote` com os links de modelo). Aqui
> apenas o renomeamos, colocamos numa pasta e o documentamos. Crédito a quem o montou.

Troca/anima uma pessoa num vídeo usando o **caminho NATIVO do SCAIL-2** (nós core do ComfyUI), com **máscara
gerada por TEXTO** (SAM3) e **toggle Animation↔Replacement**. Conhecimento destilado em `knowledge-scail2-native`.

> ⚠️ Exige ComfyUI **nightly/master** — `SCAIL2ColoredMask` e `WanSCAILToVideo` são **core** (vermelhos = não-nightly).

## O que ele faz (todas as técnicas)
Grafo em 3 grupos — **00 MODELS · 01 INPUTS · 02 SAMPLER+OUTPUT** — 63 nós, organizado com Set/Get (KJNodes).

1. **Vídeo-condutor**: `VHS_LoadVideo` com `force_rate 16` (SCAIL-2 roda a 16 fps) e `frame_load_cap 81` (máx por passada).
2. **Foto de referência**: `LoadImage` → `CLIPVisionEncode` (`clip_vision_h`) = identidade.
3. **Máscara por texto (SAM3)**: o subgraph **SAM3** roda `SAM3_VideoTrack` ×2 com prompts `CLIPTextEncode` (aqui **"human"**) — rastreia o conceito no **vídeo** e na **foto**, gerando `SAM3_TRACK_DATA`. Troque o texto para mudar o alvo ("the man on the left", "dog"...).
4. **Máscara colorida**: `SCAIL2ColoredMask` recebe os dois track_data + `replacement_mode` → produz `pose_video_mask` e `reference_image_mask`.
5. **Resolução**: `ResizeImageMaskNode` (`scale total pixels 0.5` → meia-res do pose/mask; `scale to multiple 32` → dims **÷32**).
6. **Modelo**: `UNETLoader`(SCAIL-2 fp8) → `LoraLoaderModelOnly`(lightx2v rank64, força 1) → `ModelSamplingSD3`(**shift 5**).
7. **Texto**: `CLIPLoader`(umt5, tipo "wan") → `CLIPTextEncode` **positivo/negativo** (vazios — preencha).
8. **Condicionamento SCAIL**: `WanSCAILToVideo` junta tudo — `pose_video(+mask)`, `reference_image(+mask)`, `clip_vision_output`, `width/height/length` (512×896×81 = 9:16 vertical), `replacement_mode` → `positive/negative/latent`.
9. **Sampler**: `KSampler` — `6 steps`, `cfg 1`, `euler`, `simple`, `denoise 1` (config canônica destilada).
10. **Saída**: `VAEDecode`(`wan_2.1_vae`) → `RIFE VFI`(`rife49`, ×2 → **32 fps**) → `VHS_VideoCombine` (h264-mp4, crf 19, save_metadata).
11. **Controles**: Primitives nomeados `DURAÇÃO (FRAMES)`=81 e **`REPLACE`** (False=Animation, True=Replacement) — o booleano alimenta SCAIL2ColoredMask **e** WanSCAILToVideo.

**Por que vale o aprendizado:** é o jeito **nativo** (alternativa mais direta ao wrapper kijai do `person-swap-scail2`),
com o **toggle replacement_mode explícito** e **masking por texto** integrado. Ver `knowledge-scail2-native`.

## Modelos (da nota embutida no workflow)
| Arquivo | Pasta |
|---|---|
| `wan2.1_14B_SCAIL_2_fp8_scaled.safetensors` (Comfy-Org/SCAIL-2) | `diffusion_models/` |
| `Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors` (lightx2v) | `loras/` |
| `umt5_xxl_fp8_e4m3fn_scaled.safetensors` (Comfy-Org/Wan_2.1_repackaged) | `text_encoders/` |
| `wan_2.1_vae.safetensors` | `vae/` |
| `clip_vision_h.safetensors` | `clip_vision/` |
| `sam3.1_multiplex_fp16.safetensors` (Comfy-Org/sam3.1) | `checkpoints/` |
| `rife49.pth` (vem com o Frame-Interpolation) | — |

## Setup (RunPod, root)
```bash
export HF_TOKEN=...
bash setup.sh
```
Garante nightly, instala os custom nodes (SAM3, VHS, Frame-Interpolation, KJNodes), baixa os modelos e o `.json`.

## Como usar (:8188)
1. Carregue `scail2-native-3rdparty.json` (Manager → Install Missing se houver vermelho não-core; core vermelho → `git pull` no ComfyUI).
2. **INPUTS**: suba o vídeo no `VHS_LoadVideo` e a foto no `LoadImage`. Ajuste o **prompt do SAM3** (o conceito a segmentar).
3. Escreva os prompts **positivo/negativo** (descreva o vídeo gerado — SCAIL-2 gosta de prompt longo).
4. Toggle **REPLACE** (True = trocar a pessoa preservando a cena). Ajuste **DURAÇÃO** (≤81).
5. Rode. Saída em 32 fps (RIFE ×2).

## Validação
Sem vermelhos; teste 480p curto; confira a máscara (PreviewImage) e a troca. Erros → `task-debug-generation`.

## Referências
- `knowledge-scail2-native` (grafo nativo), `knowledge-scail2` (modelo/params), `knowledge-image-masking` (SAM3), `docs/SCAIL-2.md`.
