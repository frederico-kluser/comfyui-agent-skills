# instruction-edit-kontext — Editar imagem por instrução (Flux Kontext)

> Edita uma imagem **descrevendo a mudança em texto, sem máscara** ("troque a jaqueta de couro por jeans azul"), mantendo a consistência do resto. Usa **Flux.1 Kontext [dev]** (12B).

|  |  |
|---|---|
| 🎯 Faz | Edita a imagem por instrução de texto, sem máscara |
| 🧠 Técnica | Flux.1 Kontext [dev] (12B) |
| 🎮 GPU/VRAM | ~16 GB (fp8) · RTX 4090/5090 |
| 📥 Entrada | 1 imagem (`LoadImage`) + instrução (prompt) |
| 📤 Saída | Imagem editada (composição preservada) |
| 🧩 Modelos | flux1-dev-kontext fp8 + clip_l + t5xxl_fp8 + VAE (setup.sh) |
| 🟡 Status | Rascunho a validar no pod |

> ⚠️ Confirme os arquivos de modelo na aba *Files* do HF / deixe o template baixar (Manager → Model Manager).

## Pré-requisitos
- **GPU/VRAM:** ~16 GB (fp8). RTX 4090/5090. Pod → `task-launch-runpod-pod`; custo → `knowledge-runpod-infra`.
- **Flux é gated:** exporte `HF_TOKEN` (huggingface.co/settings/tokens).

## Setup (RunPod, root)
```bash
export HF_TOKEN=...        # Flux é gated
bash setup.sh
```
Instala os nodes (KJNodes, rgthree, GGUF) e baixa o Kontext fp8 + encoders + VAE; coloca o `.json` em `ComfyUI/user/default/workflows/`.

## Como usar (:8188)
1. Carregue `instruction-edit-kontext.json` (resolva faltantes: Manager → Install Missing).
2. **Anexe a imagem** no `LoadImage` (a que será editada).
3. Escreva a **instrução** no prompt (direta, em inglês funciona melhor): *"Change the leather jacket to a blue denim jacket"*.
4. Rode (`Ctrl+Enter`). Edições sucessivas mantêm a composição.
5. Para controle cirúrgico de **uma** região, combine com `inpaint-region-cropstitch`.

## Parâmetros
| Parâmetro | Default | Faixa | Nota |
|---|---|---|---|
| `guidance` | 2.5 | 0–20 | Força da edição (↑ adere mais à instrução) |
| Modelo | `flux1-dev-kontext_fp8_scaled` | — | Fixo |

## Validação
JSON sem nós vermelhos; teste uma troca simples e verifique se o resto da imagem se manteve. Erros → `task-debug-generation`.

## Troubleshooting
| Problema | Solução |
|---|---|
| A edição ignora a instrução | Seja direto, em inglês; aumente `guidance` (3–4) |
| Altera demais a imagem | Reduza `guidance`; instrução mais específica |
| OOM / CUDA out of memory | Use fp8/GGUF; reduza a resolução; feche outros workflows |
| Nós vermelhos | Manager → Install Missing Custom Nodes |

## Referências
- **Base do grafo:** `Comfy-Org/workflow_templates/templates/flux_kontext_dev_basic.json` (adaptado).
- Conhecimento: `knowledge-image-editing` (§ edição por instrução) · `docs/image-editing.md` §1.5.
