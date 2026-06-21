# tryoff-preprocess — API Reference

Workflow de pré-processamento de vestimenta. 14 nós, 3 estágios.
Use com `aodianyun/comfyui-catvton` no Replicate ou ComfyUI Cloud API.

## Cards Informativos (o que editar)

### 🎯 INPUTS — Nós que você modifica

| Node | Tipo | Campo | Exemplo | Descrição |
|------|------|-------|---------|-----------|
| **3** | LoadImage | `image` | `"minha_foto.jpg"` | Foto da pessoa (referência). URL pública ou nome do arquivo no input dir |
| **1** | VHS_LoadVideo | `video` | `"danca.mp4"` | Vídeo condutor. Carregado para referência visual. `frame_load_cap=1` |
| **8** | TryOffRunNode | `prompt` | `"photorealistic human figure..."` | Prompt que guia a geração da roupa standalone |
| **8** | TryOffRunNode | `seed` | `42` | Seed para reprodutibilidade |
| **8** | TryOffRunNode | `num_steps` | `20` | Passos de inferência |
| **8** | TryOffRunNode | `guidance_scale` | `12.0` | Força do prompt |
| **8** | TryOffRunNode | `width` × `height` | `768 × 1024` | Resolução de saída |
| **9** | SaveImage | `filename_prefix` | `"reference_processed_"` | Prefixo do arquivo salvo |

### 🔒 FIXOS — Não alterar (modelos e configuração)

| Node | Tipo | Valor | Por que |
|------|------|-------|---------|
| **4** | SegformerB2ClothesUltra | upper/pants/dress=true | Categorias de roupa a segmentar |
| **5** | TryOffQuantizerNode | `8Bit` | Quantização do modelo |
| **6** | TryOffModelNode | `xiaozaa/cat-tryoff-flux` | Modelo CatVTON |
| **7** | TryOffFluxFillModelNode | `FLUX.1-dev` | Pipeline Flux Fill |
| **11** | MaskGaussianBlur | `radius=3.0` | Feathering da borda da máscara |
| **12** | ImageCompositeMasked | `x=0, y=0, resize=True` | Parâmetros de composição |

### 📊 ESTÁGIOS DO PIPELINE

```
Stage 1 — SEGMENTAÇÃO
  Node 3 (LoadImage) ──IMAGE──→ Node 4 (Segformer) ──MASK──→ Node 11 (Blur)
                                                            ↓
Stage 2 — TRYOFF                                          MASK (borrada)
  Node 3 (LoadImage) ──IMAGE──→ Node 8 (TryOffRunNode) ←── MASK
                                    ↓
  Node 5→6→7 (model chain) ──PIPE──┘
                                    ↓
                          slot 0: garment_image (roupa processada)
                          slot 1: tryoff_image (roupa standalone)

Stage 3 — COMPOSIÇÃO
  Node 3 (LoadImage) ──IMAGE──→ Node 12 (ImageCompositeMasked).destination
  Node 8 slot 0 ──IMAGE───────→ Node 12.source
  Node 11 ──MASK──────────────→ Node 12.mask
                                    ↓
                              Node 9 (SaveImage) → reference_processed_*.png
```

### 🚀 EXEMPLO DE USO (Python)

```python
import json

with open('tryoff-preprocess_api.json') as f:
    wf = json.load(f)

# Editar inputs
wf["3"]["inputs"]["image"] = "https://meu-cdn.com/foto.jpg"
wf["1"]["inputs"]["video"] = "https://meu-cdn.com/danca.mp4"
wf["8"]["inputs"]["prompt"] = "a person wearing carnival costume, detailed fabric..."
wf["8"]["inputs"]["seed"] = 123
wf["8"]["inputs"]["num_steps"] = 20
wf["8"]["inputs"]["guidance_scale"] = 12.0

# Enviar para Replicate
import replicate
output = replicate.run(
    "aodianyun/comfyui-catvton",
    input={"workflow_json": json.dumps(wf)}
)
```
