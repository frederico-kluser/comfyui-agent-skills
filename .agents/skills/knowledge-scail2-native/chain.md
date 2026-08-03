# SCAIL-2 Nativo — A Cadeia (3 Grupos)

O caminho **nativo** (nós core do ComfyUI), distinto do wrapper kijai. `SCAIL2ColoredMask` e `WanSCAILToVideo` são **core** → exigem ComfyUI **nightly**.

## Grafo completo
```
UNETLoader(wan2.1_14B_SCAIL_2_fp8) → LoraLoaderModelOnly(lightx2v rank64, str 1) → ModelSamplingSD3(shift 5) → KSampler
CLIPLoader(umt5_xxl, type "wan") → CLIPTextEncode +/− ─┐
VAELoader(wan_2.1_vae) ─────────────────────────────── │
CLIPVisionLoader(clip_vision_h) → CLIPVisionEncode(ref) │
VHS_LoadVideo(force_rate 16, cap 81) → (driving frames) │
LoadImage(ref) ─────────────────────────────────────── │
SAM3 subgraph → SCAIL2ColoredMask → (2 máscaras) ─────→ WanSCAILToVideo → (positive/negative/latent) → KSampler
                                                          → VAEDecode → RIFE VFI(×2) → VHS_VideoCombine
```

## Os 3 grupos
1. **MODELS** — UNETLoader, CLIPLoader, VAELoader, CLIPVisionLoader, LoraLoaderModelOnly, ModelSamplingSD3
2. **INPUTS** — LoadImage (ref), VHS_LoadVideo (driving), CLIPTextEncode (±), SAM3 subgraph, SCAIL2ColoredMask
3. **SAMPLER+OUTPUT** — WanSCAILToVideo, KSampler, VAEDecode, RIFE VFI, VHS_VideoCombine

## Controles (Primitives nomeados)
- `DURAÇÃO (FRAMES)` = 81
- `REPLACE` (BOOLEAN) → liga em `replacement_mode`. **False = Animation, True = Replacement.**

## Referências
- `workflows-cloud/scail2-native-3rdparty/` (workflow analisado + README)
- Nós detalhados → [key-nodes](key-nodes.md)
