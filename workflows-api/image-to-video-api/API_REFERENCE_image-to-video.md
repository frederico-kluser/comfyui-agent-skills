# API_REFERENCE — image-to-video-api (cards por nó)

Schemas extraídos do `/object_info` **ao vivo** do ComfyUI. **Padrão A** = saída URL (fal) → `LoadVideoURL →
CreateVideo → SaveVideo` (perde áudio). **Padrão B** = saída VIDEO (partner) → `SaveVideo` direto (áudio ok).

---

## `Veo31_fal` / `Veo31Fast_fal` — Veo 3.1 (fal · padrão A)
- **required**: `prompt` (STRING), `first_frame` (IMAGE)
- **optional**: `last_frame` (IMAGE, morph) · `duration` `[4s,6s,8s]` · `aspect_ratio` `[auto,9:16,16:9,1:1]` ·
  `resolution` `[720p,1080p]` · `generate_audio` (BOOL, default **true**)
- **saída**: `STRING` (url). **Sem seed** → identidade vem do `first_frame`.
- **gotchas**: sem campo negative (negativos em prosa); cold-start de minutos; `Fast` = mais barato/rápido.

## `SeedanceImageToVideo_fal` — Seedance 1.0 (fal · padrão A)
- **required**: `prompt`, `image` (IMAGE), `resolution` `[480p,720p]`, `duration` `[5,10]`, `camera_fixed` (BOOL)
- **optional**: `seed` (INT, default **-1**=aleatório)
- **saída**: `STRING`. Rascunho barato (480p).

## `SeedanceProImageToVideo_fal` — Seedance Pro (fal · padrão A)
- **required**: `prompt`, `image` (IMAGE), `duration` `[2..12]`
- **optional**: `end_image` (IMAGE, **morph**) · `negative_prompt` · `cfg_scale` (0–1, def 0.5) · `variations`
- **saída**: `STRING`. Ligue `image` (início) + `end_image` (fim) para transição.

## `Kling25TurboPro_fal` — Kling 2.5 Turbo Pro (fal · padrão A)
- **required**: `prompt`, `image` (IMAGE), `duration` `[5,10]`
- **optional**: `negative_prompt` (já vem preenchido) · `cfg_scale` · `tail_image` (IMAGE, último frame) · `variations`
- **saída**: `STRING`. Forte em movimento.

## `Kling26Pro_fal` — Kling 2.6 Pro (fal · padrão A)
- **required**: `prompt`, `duration` `[5,10]`
- **optional**: `image` (IMAGE — sem ela vira T2V) · `aspect_ratio` `[16:9,9:16,1:1]` · `negative_prompt` ·
  `cfg_scale` · `generate_audio` (BOOL)
- **saída**: `STRING`. I2V **com áudio**.

## `ByteDanceImageToVideoNode` — Seedance via partner (partner · padrão B)
- **required**: `model` `[seedance-1-5-pro-251215, 1-0-pro, 1-0-lite, 1-0-pro-fast]` · `prompt` · `image` (IMAGE) ·
  `resolution` `[480p,720p,1080p]` · `aspect_ratio` · `duration` (INT 3–12)
- **optional**: `seed` (INT, control_after_generate) · `camera_fixed` · `watermark` · `generate_audio`
  (**só** funciona no `seedance-1-5-pro`)
- **saída**: `VIDEO` (direto no SaveVideo). Login comfy.org.

## `GrokVideoNode` — Grok Imagine (partner · padrão B)
- **required**: `model` `[grok-imagine-video, grok-imagine-video-1.5]` · `prompt` · `resolution` `[480p,720p]` ·
  `aspect_ratio` · `duration` (INT 1–15) · `seed` (INT, só decide re-rodar)
- **optional**: `image` (IMAGE — **obrigatória** no 1.5)
- **saída**: `VIDEO`. Login comfy.org. Resultado não-determinístico (seed não fixa o conteúdo).

---

### Helpers (cadeia do padrão A)
- `LoadImage` (core) → IMAGE. · `LoadVideoURL` (fal-api): `url`→frames IMAGE. ·
  `CreateVideo` (core): `images`+`fps`(+`audio` opcional)→VIDEO. · `SaveVideo` (core): `video`→`.mp4`.
- **Seed gates** (resumo): `Veo*`/`Kling*_fal`/`Kling26` **sem seed** · `Seedance*_fal` `-1` · partner: seed só re-roda.
