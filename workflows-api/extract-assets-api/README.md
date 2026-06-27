# extract-assets-api — separar assets de uma UI gerada por IA

> Você manda **uma imagem de interface** (mockup/UI gerado por IA) e, **para cada elemento que você nomear
> em texto**, recebe um **PNG transparente** só daquele elemento. Tudo por API (sem GPU): **Nano Banana Pro**
> (Gemini 3) isola o elemento e **Recraft Remove Background** dá o recorte com alpha.

|  |  |
|---|---|
| 🎯 Faz | Recorta cada elemento de uma UI (botão, logo, avatar, ícone, card) → **PNG transparente** |
| 🧠 Técnica | Nano Banana Pro **isola por texto** → Recraft Remove Background **dá o alpha** (2 estágios) |
| 💳 Custo/billing | **fal credits** (Nano Banana Pro) **+ Comfy credits** (Recraft ~US$0.01/img) |
| 🔌 Provedores/Nós | `NanoBananaPro_fal` (fal) · `RecraftRemoveBackgroundNode` (partner/comfy.org) |
| 📥 Entrada | 1 imagem (a interface) + **N textos** (1 por elemento) |
| 📤 Saída | **N × PNG RGBA** (fundo transparente) |
| 🧩 Modelos | Gemini 3 Pro Image (Nano Banana Pro) · Recraft V3 |
| 🧱 Requer | `ComfyUI-fal-API` + `FAL_KEY` · **login** em platform.comfy.org (Recraft) |
| 🟡 Status | Estrutura validada contra o código-fonte do ComfyUI; **rode 1 elemento p/ confirmar billing/alpha** |

> 💡 **Por que 2 estágios?** O Recraft sozinho tiraria o fundo mas **manteria todos** os elementos da UI. O Nano
> Banana Pro primeiro **isola só o que você nomeou** (sobre fundo branco) e ainda **reconstrói partes ocluídas**;
> o Recraft então transforma o branco em **transparência**. Opção econômica (1 chamada): ver "Parâmetros".

## Os arquivos
| Arquivo | O que é |
|---|---|
| `extract-assets-api.json` | **Workflow visual** (arraste no ComfyUI). 1 `LoadImage` + **5 lanes** (campos de texto). |
| `extract-assets-api.api.json` | Mesmo grafo em **formato API** (1 lane), usado pelo script. |
| `extract_assets.py` | **Driver por terminal** (API HTTP): imagem + lista de elementos → pasta de PNGs (**N ilimitado**). |
| `API_REFERENCE_extract-assets-api.md` | Campos exatos de cada nó. |
| `setup.sh` | Instala `ComfyUI-fal-API`, grava `FAL_KEY`, baixa os arquivos. |

## Pré-requisitos
- **Sem GPU** — tudo roda nos provedores. Máquina de 8GB serve só p/ orquestrar.
- `ComfyUI-fal-API` instalado + `FAL_KEY` (Nano Banana Pro). **Login** em platform.comfy.org (créditos do Recraft).
- `Recraft Remove Background` é nó **CORE** (`comfy_api_nodes`); se não aparecer, **atualize o ComfyUI**.

## Setup
```bash
export FAL_KEY=...        # necessária p/ o Nano Banana Pro (fal)
bash setup.sh            # instala fal-API, grava a chave, baixa workflow + script
# depois: faça login em https://platform.comfy.org  (créditos do Recraft)
```

## Como usar — workflow visual (`:8188`)
1. Carregue `extract-assets-api.json`.
2. **Anexe a interface** no único `LoadImage` (esquerda).
3. Para **cada elemento**: pegue uma lane, **desmute** os 3 nós (selecione → `Ctrl+M`), e no nó **Nano Banana Pro**
   troque `<NOMEIE O ELEMENTO AQUI …>` pelo elemento (ex.: *the user avatar in the top-right*). Ajuste o
   `filename_prefix` do `SaveImage` (ex.: `assets/avatar`).
4. A **Lane 1** já vem ativa (exemplo); **Lanes 2–5 vêm mutadas** (não gastam crédito até desmutar).
5. `Run`. Cada lane ativa salva 1 PNG transparente em `ComfyUI/output/assets/`.
   > Precisa de **>5** elementos? Duplique uma lane (copiar/colar os 3 nós e religar do `LoadImage`) **ou** use o script.

## Como usar — script (N ilimitado, lote)
```bash
python extract_assets.py interface.png "the blue 'Sign in' button" "the user avatar" "the company logo"
python extract_assets.py interface.png "o card de preço do meio" --out ./assets --resolution 4K
```
- Sobe a imagem **1×**, roda 1 vez por elemento, baixa `./assets/<slug>.png` (nome derivado do texto).
- `--raw-prompt`: usa seu texto como o **prompt inteiro** (sem o template de isolamento), p/ controle fino.
- `--server` (default `127.0.0.1:8188`), `--timeout` (default 600s, p/ cold-start do fal).

## Parâmetros não-óbvios
| Parâmetro | Nota |
|---|---|
| **Nano Banana Pro sem seed** | Não há cache-bust por seed. Prompts diferentes não colidem; p/ refazer o MESMO, mude uma palavra. |
| **Lanes mutadas** | Lanes 2–5 vêm em `mode: muted` → **só paga o que desmutar**. Não deixe lane com placeholder rodando. |
| **`aspect_ratio: auto`** | Mantém a proporção do elemento; evita esticar. |
| **Cold-start fal** | Os nós de API **bloqueiam sem barra**; minutos em `IN_QUEUE` é normal e **conclui**. Não é travamento. |
| **Recraft = RGBA direto** | O slot `IMAGE` do Recraft já tem alpha → vai direto no `SaveImage`. Não use `JoinImageWithAlpha` (inverteria). |
| **Opção 1 chamada (barato)** | Trocar a instrução do Nano p/ *"…on a fully transparent background, PNG with alpha"* e **remover o Recraft**. Mais barato, mas o nó fal pode achatar o alpha p/ RGB → transparência **não garantida**. Por isso o default é 2 estágios. |

## Validação
- **Estrutural:** `python3 -c "import json;json.load(open('extract-assets-api.json'))"` e idem `.api.json`; `bash -n setup.sh`.
- **Funcional (1 elemento):** anexe uma UI, desmute a Lane 1, nomeie um elemento, `Run` → **0 nós vermelhos** e o
  PNG salvo deve ter **canal alpha** (abra num visor com xadrez de transparência). Confirma billing (fal + Comfy) e o alpha.

## Troubleshooting
| Problema | Solução |
|---|---|
| Nó vermelho `NanoBananaPro_fal` | Manager → Install Missing (`ComfyUI-fal-API`); confira `FAL_KEY` no `config.ini`. |
| Nó vermelho `RecraftRemoveBackgroundNode` | É core — **atualize o ComfyUI**; e faça **login** em platform.comfy.org. |
| Saída **sem** transparência (fundo branco) | Confira que o `SaveImage` está ligado no **IMAGE do Recraft** (não no do Nano). |
| Recorte traz vizinhos / falta pedaço | Prompt mais específico ("the SINGLE circular avatar, top-right"); cite cor/posição/forma. |
| Trava em `IN_QUEUE` | Não travou — cold-start do fal leva minutos. `/interrupt` não mata nó fal; só reiniciar o servidor. Itere em endpoints warm. |
| Erro de execução / sem crédito | Veja `comfyui logs`; confirme créditos fal e comfy.org. Mais: `task-debug-generation`. |

## Referências
- Conhecimento: `knowledge-comfyui-api-nodes` (nós hospedados, billing, seed gates) · `knowledge-comfyui-api`
  (API HTTP `/prompt`·`/upload/image`·`/history`·`/view`) · `knowledge-image-enhance` (remoção de fundo) · `knowledge-image-masking`.
- Base conceitual do nó fal: `workflows-api/replace-object/` (mesmo `NanoBananaPro_fal`).
- Schema dos nós conferido no fonte: `comfy_api_nodes/nodes_recraft.py` (`RecraftRemoveBackgroundNode`) e `nodes.py` (`SaveImage`).
