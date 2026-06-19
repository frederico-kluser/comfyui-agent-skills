# qwen-image-edit — Editar imagem por instrução (Qwen-Image-Edit 2511)

Edição por instrução com **Qwen-Image-Edit 2511** (20B, Alibaba): troca de objeto/fundo, **texto bilíngue
na imagem**, relighting. Alimenta a imagem no Qwen2.5-VL (semântica) e no VAE (aparência). LoRA Lightning p/ 4 passos.

- **Base do grafo:** `Comfy-Org/workflow_templates/templates/image-qwen_image_edit_2511_lora_inflation.json` (adaptado).
- **Conhecimento:** `knowledge-image-editing` (§ edição por instrução).

> ⚠️ Rascunho a validar no pod. Modelos Qwen mudam de versão rápido — confirme na aba *Files* do HF / deixe o template baixar (Manager → Model Manager).

## Pré-requisitos
- GPU/VRAM 16-24GB (fp8/GGUF). Pod → `task-launch-runpod-pod`; custo → `knowledge-runpod-infra`.

## Setup (RunPod, root)
```bash
export HF_TOKEN=...
bash setup.sh
```

## Como usar (:8188)
1. Carregue `qwen-image-edit.json` (Manager → Install Missing se preciso).
2. **Anexe a imagem** no `LoadImage`.
3. Escreva a **instrução** (PT/EN/zh): "remova a pessoa ao fundo", "troque o texto da placa para 'ABERTO'".
4. Distilled: ~**10 passos**, **CFG 1.0**, euler/res_multistep (LoRA Lightning → 4 passos). Rode.

## Validação
Teste uma troca de objeto e uma edição de texto-na-imagem; verifique fidelidade do resto. Erros → `task-debug-generation`.

## Referências
- `knowledge-image-editing`, `docs/image-editing.md` §1.5.
