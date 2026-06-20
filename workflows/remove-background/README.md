# remove-background — Remover / trocar o fundo

> Remove o fundo de uma imagem (saída PNG com canal **alpha**) com **ComfyUI-RMBG**. Resultado transparente, pronto para compor sobre outro fundo.

|  |  |
|---|---|
| 🎯 Faz | Remove/troca o fundo → PNG transparente |
| 🧠 Técnica | ComfyUI-RMBG · RMBG-2.0 / BiRefNet / BEN2 / SAM3 (v3.0.0) |
| 🎮 GPU/VRAM | Modesta (RMBG/BiRefNet leves) · SAM3 ~3.4 GB |
| 📥 Entrada | 1 imagem (`LoadImage`) |
| 📤 Saída | Imagem RGBA (fundo transparente) |
| 🧩 Modelos | matting baixam no 1º uso · SAM3 gated (licença HF) |
| 🟢 Status | Pronto — modelos auto-baixam no 1º uso |

> 💡 Para **trocar** o fundo: componha a saída RGBA com `ImageCompositeMasked` ou `scripts/compose.py` do projeto `inpaint-region-cropstitch`.

## Pré-requisitos
- **GPU/VRAM:** modesta serve (RMBG/BiRefNet são leves); **SAM3** é mais pesado (~3.4 GB). Pod → `task-launch-runpod-pod`.
- ComfyUI atual + o custom node `ComfyUI-RMBG` (o `setup.sh` instala).

## Setup (RunPod, root)
```bash
export HF_TOKEN=...        # necessário p/ SAM3 (gated)
bash setup.sh
```
Instala o `ComfyUI-RMBG`. Os modelos de matting baixam no primeiro uso do nó; **SAM3** requer licença aceita no HF.

## Como usar (:8188)
1. Carregue `remove-background.json`.
2. **Anexe a imagem** no `LoadImage`.
3. Escolha o **modelo** no nó RMBG (ver tabela abaixo).
4. Saída: imagem com alpha. Para trocar o fundo, componha com `ImageCompositeMasked` ou `compose.py`.

## Parâmetros — qual modelo usar
| Modelo | Quando usar |
|---|---|
| **BiRefNet / RMBG-2.0** | Uso geral (objetos, produtos, pessoas) |
| **BEN2** | Cabelo e bordas finas |
| **SAM3** | Segmentação **por texto** (escolhe o objeto a manter/remover) |

## Validação
Verifique bordas/cabelo (sem halo). Para recortes difíceis, troque o modelo (BEN2/BiRefNet). Erros → `task-debug-generation`.

## Troubleshooting
| Problema | Solução |
|---|---|
| Halo / borda no cabelo | Troque para **BEN2** ou **BiRefNet**; aumente a resolução de entrada |
| SAM3 não baixa / erro de acesso | Aceite a licença no HF e exporte `HF_TOKEN` |
| Recorte deixa buracos no sujeito | Use um modelo geral (RMBG-2.0/BiRefNet); evite SAM3 em sujeitos complexos |
| Nós vermelhos | Manager → Install Missing Custom Nodes |

## Referências
- **Base do grafo:** `1038lab/ComfyUI-RMBG/example_workflows/Comfyu-rmbg_v2.9.3_node_sample.json` (adaptado).
- Conhecimento: `knowledge-image-enhance` (§ remoção de fundo), `knowledge-image-masking` · `docs/image-editing.md` §2/§4.
