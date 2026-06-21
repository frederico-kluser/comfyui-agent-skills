# outpaint-extend — Estender a imagem (outpainting com Flux Fill)

> Aumenta o enquadramento gerando conteúdo novo nas bordas (outpainting). Usa `Pad Image for Outpainting` (adiciona borda + máscara) + **Flux.1 Fill [dev]**.

|  |  |
|---|---|
| 🎯 Faz | Estende o enquadramento gerando conteúdo novo nas bordas |
| 🧠 Técnica | Flux.1 Fill [dev] + `Pad Image for Outpainting` |
| 🎮 GPU/VRAM | 16–24 GB (Flux Fill fp8/GGUF) |
| 📥 Entrada | 1 imagem (`LoadImage`) |
| 📤 Saída | Imagem com enquadramento ampliado |
| 🧩 Modelos | flux1-fill-dev (gated) + clip_l + t5xxl_fp8 + VAE (setup.sh) |
| 🟡 Status | Rascunho a validar no pod |

> ⚠️ Confirme os modelos na aba *Files* do HF / deixe o template baixar (Manager → Model Manager).

## Pré-requisitos
- **GPU/VRAM:** 16–24 GB (Flux Fill fp8/GGUF). Pod → `task-launch-runpod-pod`; custo → `knowledge-runpod-infra`.
- **Flux é gated:** exporte `HF_TOKEN`.

## Setup (RunPod, root)
```bash
export HF_TOKEN=...        # Flux é gated
bash setup.sh
```
Instala os nodes (Inpaint-CropAndStitch, KJNodes, rgthree, GGUF) e baixa o Flux Fill + encoders + VAE.

## Como usar (:8188)
1. Carregue `outpaint-extend.json` (Manager → Install Missing se preciso).
2. **Anexe a imagem** no `LoadImage`.
3. No `Pad Image for Outpainting`, defina quantos px adicionar em cada lado (left/top/right/bottom) e o `feathering`.
4. Prompt do que preencher as bordas (ex.: *"extend the beach and sky"*). Rode (`Ctrl+Enter`).
5. Para extensões grandes, faça em passos menores e repita; ou use `Extend Image for Outpainting` (CropAndStitch).

## Parâmetros
| Parâmetro | Nota |
|---|---|
| `left` / `top` / `right` / `bottom` | px a adicionar por lado (`Pad Image for Outpainting`) |
| `feathering` | Suavização da borda da máscara (transição) |
| `guidance` | ~30 típico para Flux Fill |

## Validação
Verifique continuidade nas bordas (sem emenda/repetição). Erros → `task-debug-generation`.

## Troubleshooting
| Problema | Solução |
|---|---|
| Emenda / repetição na borda | Aumente `feathering`; estenda em passos menores |
| Conteúdo incoerente nas bordas | Descreva no prompt o que preencher |
| Extensão grande falha | Divida em várias passadas; use `Extend Image` (CropAndStitch) |
| Nós vermelhos | Manager → Install Missing Custom Nodes |

## Referências
- **Base do grafo:** `Comfy-Org/workflow_templates/templates/flux_fill_outpaint_example.json` (adaptado).
- Conhecimento: `knowledge-image-enhance` (§ outpainting), `knowledge-image-editing` (Flux Fill) · `docs/image-editing.md` §4.
