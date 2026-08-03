# API Online — Catálogo de Nós: Imagem, Edição e Upscale

## Gerar/Editar Imagem — 🏆 os 2 melhores por crédito comfy.org

### `GeminiNanoBanana2` (partner, "Nano Banana 2" = Gemini 3.1 Flash Image)
- **Tem seed**, `thinking_level` `MINIMAL|HIGH` (HIGH resolve perspectiva/oclusão/luz).
- `resolution` 1K/2K/4K, `aspect_ratio` `auto` (herda a entrada).
- **Até 14 refs** via `BatchImagesNode`, `system_prompt` editável.
- Saídas: `IMAGE` · `STRING` · `thought_image` (rascunho do raciocínio — bom para depurar).

### `ByteDanceSeedreamNode` (partner, "Seedream 4.5 & 5.0")
- `seedream 5.0 lite`=`seedream-5-0-260128` (**14** refs, saída PNG) · `seedream-4-5-251128` (10 refs) · `seedream-4-0-250828`.
- ⚠️ **piso de pixels na saída: 3.686.400 (≈2560×1440) no 4.5/5.0** (921.600 no 4.0) — preset menor **rejeita antes de cobrar**.
- Teto ~10,4 MP no 5.0, ~16,7 MP no 4.5/4.0.
- `ByteDanceSeedreamNodeV2` tem o **mesmo display name** mas schema V3 → **widgets incompatíveis**; prefira a V1.

### Outros
`NanoBananaPro_fal` (Gemini 3, **sem seed**) · `FluxUltra_fal` · `Ideogram*` · `Recraft*` · `OpenAIDalle3`/`OpenAIGPTImage1`/`OpenAIGPTImageNodeV2`.

## Editar (instrução/inpaint)
- **`FluxProKontext_fal`/`FluxProKontextMulti_fal`** — Kontext Max, face-swap/repose.
- **`FluxPro1Fill_fal`** — inpaint.
- **`FluxEraseNode`** — erase, partner, sem prompt.
- **`FluxVTONode`/`KlingVirtualTryOnNode`** — try-on.
- **`QwenImageEditPlusLoRA_fal`** — 🏆 manter rosto+roupa; guidance 4.0, steps 32; **cold-start ~8 min**.
- ⚠️ `NanoBananaEdit_fal` = Gemini 2.5 = **fraco** ("devolve a foto") → use Kontext Max ou Nano Banana **Pro**.

## Upscale
- **`Upscaler_fal`** (Clarity) — redesenha → `creativity≈0.2` para retrato.
- **`Seedvr_Upscaler_fal`** (SeedVR2) — fidelidade sem perder identidade.
- **`TopazImageEnhance`**.
- Local grátis = `4x-UltraSharp` (ESRGAN).

> **Não existe** node dedicado de face-swap/try-on tipo FASHN/IDM-VTON; `PixverseSwapNode_fal` é **vídeo**. Para swap/repose use **Kontext Max multi** ou **Nano Banana Pro**.

## Referências
- Seed gates → [seed-gates](seed-gates.md)
- Vídeo → [catalog-video](catalog-video.md)
- Música/Áudio → [catalog-music-audio](catalog-music-audio.md)
