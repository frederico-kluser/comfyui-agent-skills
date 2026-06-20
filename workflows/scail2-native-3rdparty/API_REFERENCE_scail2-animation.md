# scail2-animation — API Reference

Workflow de animação SCAIL-2. 63 nós. Modo REPLACE (substitui personagem no vídeo).
Use com `fal-ai/scail-2` no fal.ai (recomendado) ou ComfyUI Cloud API.

## Cards Informativos (apenas nós editáveis)

### 🎯 INPUTS — O que você modifica

| Node | Tipo | Campo | Exemplo | Descrição |
|------|------|-------|---------|-----------|
| **58** | LoadImage | `image` | `"reference_processed_00001_.png"` | Imagem de referência processada (saída do Step 1) |
| **113** | VHS_LoadVideo | `video` | `"carnival-dancing.mp4"` | Vídeo condutor completo. `frame_load_cap=81` |
| **6** | CLIPTextEncode | `text` | `"a person dancing samba..."` | **Prompt positivo** — descreve a cena desejada |
| **7** | CLIPTextEncode | `text` | `"blurry, distorted..."` | **Prompt negativo** — o que evitar |
| **172** | PrimitiveBoolean | `value` | `True` | **Toggle REPLACE** — `True` = substitui personagem |
| **166** | PrimitiveInt | `value` | `81` | **DURAÇÃO** em frames (81 = ~5s a 16fps) |

### ⚙️ PARÂMETROS — Ajuste fino

| Node | Tipo | Campo | Default | Descrição |
|------|------|-------|---------|-----------|
| **3** | KSampler | `seed` | `1234` | Seed de geração |
| **3** | KSampler | `steps` | `6` | Passos do sampler (6–8 recomendado) |
| **3** | KSampler | `cfg` | `1.0` | CFG scale (sempre 1 com LightX2V) |
| **3** | KSampler | `sampler_name` | `euler` | Sampler |
| **3** | KSampler | `scheduler` | `simple` | Scheduler |
| **101** | WanSCAILToVideo | `length` | `81` | Frames do vídeo gerado |
| **101** | WanSCAILToVideo | `width` × `height` | `512 × 896` | Resolução (múltiplos de 32) |
| **101** | WanSCAILToVideo | `pose_strength` | `1.0` | Força do pose driving |
| **48** | ModelSamplingSD3 | `shift` | `5.0` | Shift do scheduler |
| **169** | RIFE VFI | `multiplier` | `2` | Multiplicador de frames (16→32fps) |
| **49** | VHS_VideoCombine | `frame_rate` | `32` | FPS do vídeo final |
| **49** | VHS_VideoCombine | `filename_prefix` | `SCAIL-2` | Nome do arquivo de saída |

### 🔒 FIXOS — Modelos e configuração (não alterar)

| Node | Tipo | Valor |
|------|------|-------|
| **37** | UNETLoader | `wan2.1_14B_SCAIL_2_fp8_scaled.safetensors` |
| **96** | LoraLoaderModelOnly | `Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors` |
| **39** | VAELoader | `wan_2.1_vae.safetensors` |
| **38** | CLIPLoader | `umt5_xxl_fp8_e4m3fn_scaled.safetensors` |
| **57** | CLIPVisionLoader | `clip_vision_h.safetensors` |
| **110** | CheckpointLoaderSimple | `sam3.1_multiplex_fp16.safetensors` |
| **169** | RIFE VFI | `rife49.pth` |

### 📊 ARQUITETURA DO GRAFO

```
┌─ INPUTS ───────────────────────────────────────────────────────┐
│  LoadImage(58) → ref     VHS(113) → video                      │
│  CLIPTextEncode(6) → POS   CLIPTextEncode(7) → NEG            │
│  PrimitiveBoolean(172) → REPLACE   PrimitiveInt(166) → DURAÇÃO │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌─ MODEL LOADING ────────────────────────────────────────────────┐
│  UNETLoader(37) → LoraLoader(96) → ModelSamplingSD3(48) → MODEL│
│  VAELoader(39) → VAE                                          │
│  CLIPLoader(38) → CLIP   CLIPVisionLoader(57) → CLIP_VISION    │
│  CheckpointLoader(110) → SAM3                                  │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌─ SEGMENTATION (SAM3 subgraph) ─────────────────────────────────┐
│  VHS(113) → SAM3_VideoTrack → track_data                       │
│  LoadImage(58) → SAM3_ImageTrack → ref_track_data              │
│  SCAIL2ColoredMask(107) → colored_mask (REPLACE mode)          │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌─ GENERATION ───────────────────────────────────────────────────┐
│  WanSCAILToVideo(101): ref + video + mask + MODEL + VAE + CLIP│
│      → latent                                                  │
│  KSampler(3): latent + POS + NEG + MODEL                       │
│      → latent (denoised)                                       │
│  VAEDecode → frames                                            │
│  RIFE VFI(169): frames ×2 → 32fps                              │
│  VHS_VideoCombine(49) → SCAIL-2_*.mp4                          │
└────────────────────────────────────────────────────────────────┘
```

### 🚀 EXEMPLO DE USO (Python via fal.ai)

```python
import fal_client

# Step 2: SCAIL-2 animation (o Step 1 já produziu reference_processed.png)
result = fal_client.submit(
    "fal-ai/scail-2",
    arguments={
        "image_url": "https://meu-cdn.com/reference_processed.png",
        "video_url": "https://meu-cdn.com/carnival-dancing.mp4",
        "prompt": "a person dancing samba at carnival, colorful costume, festive atmosphere",
        "seed": 42,
        "replacement_mode": True,
        "num_frames": 81,
    }
)
video_url = result.get()["video"]["url"]
print(f"Output: {video_url}")
```

### 📝 NOTAS

- **REPLACE=True** é obrigatório para referência processada (o personagem do vídeo é substituído pela referência)
- **cfg=1** sempre com LightX2V LoRA (a guidance vem da LoRA destilada)
- **euler/simple** é o par recomendado para SCAIL-2
- **shift=5** para SCAIL-2 (diferente do Wan puro que usa shift=1)
- **81 frames** = duração máxima padrão. Para vídeos mais longos, use Context Windows
