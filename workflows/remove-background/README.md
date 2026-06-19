# remove-background — Remover/trocar o fundo

Remove o fundo de uma imagem (alpha/PNG transparente) com **ComfyUI-RMBG**: RMBG-2.0, INSPYRENET, BEN2,
**BiRefNet** e **SAM3** (v3.0.0). Saída com canal alpha pronta para compor sobre outro fundo.

- **Base do grafo:** `1038lab/ComfyUI-RMBG/example_workflows/Comfyu-rmbg_v2.9.3_node_sample.json` (adaptado).
- **Conhecimento:** `knowledge-image-enhance` (§ remoção de fundo), `knowledge-image-masking`.

> ⚠️ Rascunho a validar no pod. **SAM3** (`sam3.pt`) exige aprovação de licença no Hugging Face. Os modelos do
> RMBG geralmente **baixam sozinhos** no 1º uso do nó.

## Pré-requisitos
- GPU modesta serve (RMBG/BiRefNet são leves); SAM3 é mais pesado (~3.4GB). Pod → `task-launch-runpod-pod`.

## Setup (RunPod, root)
```bash
export HF_TOKEN=...        # necessário p/ SAM3 (gated)
bash setup.sh
```
Instala o ComfyUI-RMBG. Os modelos de matting baixam no primeiro uso; SAM3 requer licença aceita no HF.

## Como usar (:8188)
1. Carregue `remove-background.json`.
2. **Anexe a imagem** no `LoadImage`.
3. Escolha o modelo no nó RMBG: **BiRefNet/RMBG-2.0** (geral), **BEN2** (cabelo/bordas finas), **SAM3** (por texto: segmenta o objeto a manter/remover).
4. Saída: imagem com alpha. Para trocar o fundo, componha com `ImageCompositeMasked` ou `compose.py` (ver `inpaint-region-cropstitch/scripts`).

## Validação
Verifique bordas/cabelo (sem halo). Para recortes difíceis, troque o modelo (BEN2/BiRefNet). Erros → `task-debug-generation`.

## Referências
- `knowledge-image-enhance`, `knowledge-image-masking`, `docs/image-editing.md` §2/§4.
