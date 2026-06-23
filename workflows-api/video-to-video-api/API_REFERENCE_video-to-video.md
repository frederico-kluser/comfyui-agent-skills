# API_REFERENCE — video-to-video-api (cards por nó)

Schemas do `/object_info` **ao vivo**. **Padrão A** = saída URL (fal) → `LoadVideoURL → CreateVideo →
SaveVideo` (perde áudio). **Padrão B** = saída VIDEO (partner) → `SaveVideo` direto (áudio ok).
Entrada de vídeo = core **`LoadVideo`** (saída VIDEO).

---

## 🅰️ Restyle / editar

### `RunwayAleph2VideoToVideoNode` — Runway Aleph (partner · padrão B)
- **required**: `prompt` (1–1000 chars) · `video` (VIDEO, **2–30s ≤30fps**) · `seed` (control_after_generate) ·
  `public_figure_threshold` `[auto,low]`
- **optional**: `keyframes` (RUNWAY_ALEPH2_KEYFRAME) · `prompt_images` (RUNWAY_ALEPH2_PROMPT_IMAGE) — **uma OU outra**
- **saída**: `VIDEO`. Melhor restyle in-context (luz/estilo/estação, remover/inserir objeto, novos ângulos).

### `GrokVideoEditNode` — Grok edit (partner · padrão B)
- **required**: `model` `[grok-imagine-video]` · `prompt` · `video` (VIDEO, **≤8.7s / 50MB**) · `seed`
- **saída**: `VIDEO`. Para clipes curtos.

### `KlingOmniVideoToVideoEdit_fal` — Kling Omni (fal · padrão A)
- **required**: `prompt` · `video` (VIDEO)
- **optional**: `keep_audio` (BOOL) · `reference_images` (IMAGE) · `element_1..4_frontal_image` +
  `element_1..4_reference_images` (IMAGE) · `variations`
- **saída**: `video_url` (STRING). Edita e pode **inserir elementos** por referência.

## 🅱️ Motion-transfer / animar personagem (substituto-API do SCAIL-2)

### `Wan2214b_animate_move_character_fal` — Wan 2.2 Animate · MOVE (fal · padrão A)
- **required**: `image` (IMAGE — o personagem/sujeito)
- **optional**: `video` (VIDEO — o guia de movimento) **ou** `input_video_url` (STRING) · `turbo` (BOOL) ·
  `resolution` `[480p,580p,720p]` · `seed` (INT, def 24) · `num_inference_steps` (20) · `guidance_scale` (1.0) ·
  `shift` (INT, 8) · `video_quality` `[low,medium,high,maximum]` · `video_write_mode` · safety checkers ·
  `return_frames_zip` · `variations`
- **saída**: `video_url` (STRING) + `frames_zip_url`. Anima a imagem p/ **seguir** o vídeo.

### `Wan2214b_animate_replace_character_fal` — Wan 2.2 Animate · REPLACE (fal · padrão A)
- Mesmos campos do MOVE. **Substitui** o personagem dentro do `video` (mantém movimento/câmera).

### `KlingV3ProMotionControl_fal` — Kling V3 Motion (fal · padrão A)
- **required**: `image` (IMAGE) · `video` (VIDEO) · `character_orientation` `[image,video]`
- **optional**: `prompt` · `keep_original_sound` (BOOL)
- **saída**: `STRING` (url).

## 🅲 Estender / continuar

### `GrokVideoExtendNode` — Grok extend (partner · padrão B)
- **required**: `prompt` · `video` (VIDEO, 2–15s) · `model` (**combo dinâmico**: `grok-imagine-video` →
  `duration` INT 2–10) · `seed`
- **saída**: `VIDEO`. Aceita **arquivo** de vídeo direto.

### `KlingVideoExtendNode` — Kling extend (partner · padrão B)
- **required**: `prompt` · `negative_prompt` · `cfg_scale` (0–1) · `video_id` (STRING, **forceInput** — vem de uma
  geração Kling, ex. `KlingImage2VideoNode.video_id`)
- **saída**: `VIDEO` · `video_id` · `duration`. **Não** aceita arquivo; encadeia por `video_id`; total ≤3min.

### `ViduExtendVideoNode` — Vidu extend (partner · padrão B)
- **required**: `model` (**combo dinâmico**: `viduq2-pro`/`viduq2-turbo` → `duration` 1–7, `resolution`
  `[720p,1080p]`) · `video` (VIDEO) · `prompt` · `seed`
- **optional**: `end_frame` (IMAGE)
- **saída**: `VIDEO`.

---

### Helper de entrada
- `LoadVideo` (core): `file` (upload) → **VIDEO**. Use-o para alimentar o input `video` dos nós acima.
- `KlingImage2VideoNode` (partner): `start_frame`+`prompt`+… → `VIDEO`, **`video_id`**, `duration` (usado em `31_extend_kling`).
