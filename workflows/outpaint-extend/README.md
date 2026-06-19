# outpaint-extend — Estender a imagem (outpainting com Flux Fill)

Aumenta o enquadramento gerando conteúdo novo nas bordas (outpainting). Usa `Pad Image for Outpainting`
(adiciona borda + máscara) + **Flux.1 Fill [dev]**.

- **Base do grafo:** `Comfy-Org/workflow_templates/templates/flux_fill_outpaint_example.json` (adaptado).
- **Conhecimento:** `knowledge-image-enhance` (§ outpainting), `knowledge-image-editing` (Flux Fill).

> ⚠️ Rascunho a validar no pod. Confirme os modelos na aba *Files* do HF / deixe o template baixar (Manager → Model Manager).

## Pré-requisitos
- GPU/VRAM 16-24GB (Flux Fill fp8/GGUF). Pod → `task-launch-runpod-pod`; custo → `knowledge-runpod-infra`.

## Setup (RunPod, root)
```bash
export HF_TOKEN=...        # Flux é gated
bash setup.sh
```

## Como usar (:8188)
1. Carregue `outpaint-extend.json` (Manager → Install Missing se preciso).
2. **Anexe a imagem** no `LoadImage`.
3. No `Pad Image for Outpainting`, defina quantos px adicionar em cada lado (left/top/right/bottom) e o `feathering`.
4. Prompt do que preencher as bordas (ex.: "extend the beach and sky"). Rode (`Ctrl+Enter`).
5. Para extensões grandes, faça em passos menores e repita; ou use `Extend Image for Outpainting` (CropAndStitch).

## Validação
Verifique continuidade nas bordas (sem emenda/repetição). Erros → `task-debug-generation`.

## Referências
- `knowledge-image-enhance`, `knowledge-image-editing`, `docs/image-editing.md` §4.
