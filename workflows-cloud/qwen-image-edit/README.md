# qwen-image-edit — Editar imagem por instrução (Qwen-Image-Edit 2511)

> Edição por instrução com **Qwen-Image-Edit 2511** (20B, Alibaba): troca de objeto/fundo, **texto bilíngue na imagem**, relighting. Alimenta a imagem no Qwen2.5-VL (semântica) e no VAE (aparência). LoRA Lightning p/ 4 passos.

|  |  |
|---|---|
| 🎯 Faz | Edição por instrução: objeto/fundo, texto na imagem, relight |
| 🧠 Técnica | Qwen-Image-Edit 2511 (20B, Alibaba) + LoRA Lightning |
| 🎮 GPU/VRAM | 16–24 GB (fp8/GGUF) |
| 📥 Entrada | 1 imagem (`LoadImage`) + instrução (PT/EN/zh) |
| 📤 Saída | Imagem editada |
| 🧩 Modelos | qwen_image_edit_2511 fp8 + qwen2.5-vl-7b fp8 + qwen_image_vae (setup.sh) |
| 🟡 Status | Rascunho a validar no pod |

> ⚠️ Modelos Qwen mudam de versão rápido — confirme na aba *Files* do HF / deixe o template baixar (Manager → Model Manager).

## Pré-requisitos
- **GPU/VRAM:** 16–24 GB (fp8/GGUF). Pod → `task-launch-runpod-pod`; custo → `knowledge-runpod-infra`.

## Setup (RunPod, root)
```bash
export HF_TOKEN=...
bash setup.sh
```
Instala os nodes (KJNodes, GGUF, rgthree) e baixa o Qwen-Image-Edit 2511 + Qwen2.5-VL + VAE.

## Como usar (:8188)
1. Carregue `qwen-image-edit.json` (Manager → Install Missing se preciso).
2. **Anexe a imagem** no `LoadImage`.
3. Escreva a **instrução** (PT/EN/zh): *"remova a pessoa ao fundo"*, *"troque o texto da placa para 'ABERTO'"*.
4. Rode. (Distilled: ~10 passos, CFG 1.0, euler/res_multistep; LoRA Lightning → 4 passos.)

## Parâmetros
| Parâmetro | Default | Nota |
|---|---|---|
| `steps` | ~10 | 4 com LoRA Lightning |
| `cfg` | 1.0 | Distilled |
| `sampler` / `scheduler` | euler / res_multistep | |

## Validação
Teste uma troca de objeto e uma edição de texto-na-imagem; verifique fidelidade do resto. Erros → `task-debug-generation`.

## Troubleshooting
| Problema | Solução |
|---|---|
| Texto na imagem sai errado | Coloque o texto entre aspas na instrução; aumente `steps` |
| Edição fraca / não aplica | Desative a LoRA Lightning e use ~20 steps, `cfg` 2.5 |
| OOM / CUDA out of memory | Use GGUF; feche outros workflows; reduza resolução |
| Nós vermelhos | Manager → Install Missing Custom Nodes |

## Referências
- **Base do grafo:** `Comfy-Org/workflow_templates/templates/image-qwen_image_edit_2511_lora_inflation.json` (adaptado).
- Conhecimento: `knowledge-image-editing` (§ edição por instrução) · `docs/image-editing.md` §1.5.
