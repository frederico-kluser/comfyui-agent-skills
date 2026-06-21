# inpaint-region-cropstitch — Editar só uma parte da imagem e recolar

> Seleciona uma **região** (máscara), **edita só ela** com inpaint (Flux Fill / SDXL-inpaint) e **recola** na original **sem tocar o resto** — via `Inpaint Crop` + `Inpaint Stitch` (padrão de ouro, 30–100× mais rápido em GPU). Inclui scripts Python para o replace fora do ComfyUI.

|  |  |
|---|---|
| 🎯 Faz | Edita uma região (máscara) e recola sem tocar o resto |
| 🧠 Técnica | Flux Fill / SDXL-inpaint + Inpaint Crop & Stitch (+ scripts Python) |
| 🎮 GPU/VRAM | 16–24 GB (Flux Fill fp8/GGUF) |
| 📥 Entrada | 1 imagem (`LoadImage`) + máscara (MaskEditor / SAM3 / Florence) |
| 📤 Saída | Imagem com a região editada recolada |
| 🧩 Modelos | flux1-fill-dev (gated) + clip_l + t5xxl_fp8 + VAE (setup.sh) |
| 🟡 Status | Rascunho a validar no pod |

> ⚠️ Os nomes/links de modelos (Flux Fill etc.) mudam rápido — confirme na aba *Files* do HF, ou deixe o ComfyUI baixar os faltantes ao abrir o template (Manager → Model Manager).

## Pré-requisitos
- **GPU/VRAM:** 16–24 GB (Flux Fill fp8/GGUF) — RTX 5090/4090. Escolha → `knowledge-runpod-infra`. Pod → `task-launch-runpod-pod`.
- ComfyUI atual + os custom nodes (o `setup.sh` instala).

## Setup (RunPod, root)
```bash
export HF_TOKEN=...        # p/ modelos gated (Flux)
bash setup.sh
```
Instala os nodes (Crop&Stitch, Impact, inpaint-nodes, RMBG/SAM/Florence p/ máscara semântica), baixa os encoders/VAE do Flux + (best-effort) o Flux Fill, e baixa este `.json` p/ `ComfyUI/user/default/workflows/`.

## Como usar (:8188)
1. Carregue `inpaint-region-cropstitch.json`. Resolva modelos faltantes (Manager → "Install Missing").
2. **Anexe a imagem** no `LoadImage`. **Selecione a região**: clique direito → "Open in MaskEditor" (manual), ou troque por SAM3/Florence (máscara por texto: "a camisa") — ver `knowledge-image-masking`.
3. **Prompt** do que vai no lugar (ex.: *"a vintage leather sofa"*). Modelo: Flux Fill (denoise 1.0 com VAE Encode for Inpainting) ou `InpaintModelConditioning` (denoise 0.45–0.7).
4. **Crop&Stitch** (ver Parâmetros). Rode (`Ctrl+Enter`). O Stitch recola sem alterar pixels fora da máscara.

## Parâmetros — Crop & Stitch + inpaint
| Parâmetro | Default / Faixa | Nota |
|---|---|---|
| `blend_pixels` | 16–32 | Feathering da emenda |
| `context_expand` | ↑ se perder contexto | Quanto da volta entra no crop |
| `rescale_factor` | <1 se "dupla cabeça" | Reduz a escala do crop |
| `denoise` | 1.0 (VAE Encode) / 0.45–0.7 (InpaintModelConditioning) | Intensidade da geração |
| máscara | 100% opaca (#FFFFFF), 1024 nativo | Resolução de trabalho |

## Replace via código (fora do ComfyUI) — `scripts/`
```bash
# Recolar uma região editada na original (fidelidade de pixels)
python scripts/compose.py -o original.png -e edited.png -m mask.png --out out.png            # alpha blend feathered
python scripts/compose.py -o original.png -e edited.png -m mask.png --method seamless --clone mixed   # Poisson (harmoniza cor/luz)

# Rodar o workflow inteiro pela API HTTP (precisa do JSON em formato API — "Save (API Format)")
python scripts/run_api.py --workflow wf_api.json --image original.png --image-node 10 \
       --mask mask.png --mask-node 11 --prompt "a vintage leather sofa" --prompt-node 6 --seed 123 --out-dir out/
```
`compose.py`: `alpha` = cor exata (Pillow/NumPy); `seamless` = harmoniza cor/luz (OpenCV). `run_api.py`: upload → /prompt → poll /history → baixa /view. Detalhes → `knowledge-comfyui-api`.

## Validação
JSON sem nós vermelhos (senão Manager → Install Missing). Teste um inpaint simples 1024 e confira bordas/cor (desvio de cor em Flux → nó Color Match). Erros → `task-debug-generation`.

## Troubleshooting
| Problema | Solução |
|---|---|
| "Dupla cabeça" / sujeito duplicado | `rescale_factor` <1; reduza `context_expand` |
| Borda visível na emenda | `blend_pixels` ↑ (24–32); máscara 100% opaca |
| Desvio de cor (Flux) | Adicione um nó Color Match |
| Região fora da máscara mudou | Confirme o `Inpaint Stitch` ligado |
| OOM / cinza | fp8/GGUF; reduza resolução; ver `task-debug-generation` |
| Nós vermelhos | Manager → Install Missing Custom Nodes |

## Referências
- **Base do grafo:** `lquesada/ComfyUI-Inpaint-CropAndStitch/example_workflows/inpaint_flux.json` (adaptado).
- Conhecimento: `knowledge-image-editing` (inpaint), `knowledge-image-masking` (selecionar), `knowledge-comfyui-api` (replace via código) · `docs/image-editing.md` §1/§3.
