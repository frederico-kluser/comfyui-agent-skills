# instruction-edit-kontext — Editar imagem por instrução (Flux Kontext)

Edita uma imagem **descrevendo a mudança em texto, sem máscara** ("troque a jaqueta de couro por jeans
azul"), mantendo a consistência do resto. Usa **Flux.1 Kontext [dev]** (12B).

- **Base do grafo:** `Comfy-Org/workflow_templates/templates/flux_kontext_dev_basic.json` (adaptado).
- **Conhecimento:** `knowledge-image-editing` (§ edição por instrução).

> ⚠️ Rascunho a validar no pod. Confirme os arquivos de modelo na aba *Files* do HF / deixe o template baixar (Manager → Model Manager).

## Pré-requisitos
- GPU/VRAM ~16GB (fp8). RTX 4090/5090. Pod → `task-launch-runpod-pod`; custo → `knowledge-runpod-infra`.

## Setup (RunPod, root)
```bash
export HF_TOKEN=...        # Flux é gated
bash setup.sh
```

## Como usar (:8188)
1. Carregue `instruction-edit-kontext.json` (resolva faltantes: Manager → Install Missing).
2. **Anexe a imagem** no `LoadImage` (a que será editada).
3. Escreva a **instrução** no prompt (direta, em inglês funciona melhor): "Change the leather jacket to a blue denim jacket".
4. `guidance` padrão **2.5** (faixa 0-20). Rode (`Ctrl+Enter`). Edições sucessivas mantêm a composição.
5. Para controle cirúrgico de UMA região, combine com `inpaint-region-cropstitch`.

## Validação
JSON sem nós vermelhos; teste uma troca simples e verifique se o resto da imagem se manteve. Erros → `task-debug-generation`.

## Referências
- `knowledge-image-editing`, `docs/image-editing.md` §1.5.
