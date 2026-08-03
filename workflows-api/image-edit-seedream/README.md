# image-edit-seedream — as mesmas 6 edições, no Seedream 5.0/4.5 (créditos comfy.org)

> Gêmeo do [`../image-edit-nano-banana-2/`](../image-edit-nano-banana-2/): **os mesmos 6 processos**,
> no outro melhor editor disponível por crédito comfy.org. Rode os dois com a mesma entrada e fique
> com o melhor — eles erram de formas diferentes.

|  |  |
|---|---|
| 🎯 Faz | Edita uma foto por instrução + imagem de referência: roupa, objeto, pessoa, cenário, e insere você na cena |
| 🧠 Técnica | Edição multi-referência por **frase única** (até 14 refs no 5.0), saída até 4K, com cláusula de relight no prompt |
| 💳 Custo/billing | **Créditos comfy.org** — 1 chamada por bloco executado. Bloco em bypass = **0 créditos** |
| 🔌 Provedores/Nós | `ByteDanceSeedreamNode` (partner, `partner/image/ByteDance`) · `BatchImagesNode` · `LoadImage` · `SaveImage` — **tudo core, zero custom node** |
| 📥 Entrada | A foto BASE + (quase sempre) uma foto de REFERÊNCIA |
| 📤 Saída | Imagem editada em `output/edit/seedream_<processo>_*` (PNG no 5.0 lite) |
| 🧩 Modelos | Seedream 5.0 lite (`seedream-5-0-260128`) · Seedream 4.5 (`seedream-4-5-251128`) · Seedream 4.0 |
| 🧱 Requer | **Login** em `platform.comfy.org` (sem chave de API). Roda em máquina de 8 GB, sem GPU |
| 🟡 Status | Grafo gerado a partir dos templates oficiais do ComfyUI + `/object_info` ao vivo, e validado estruturalmente. **Ainda não executado** (gastaria crédito) — valide no primeiro load |

📇 **Card de API:** [`API_REFERENCE_image-edit-seedream.md`](API_REFERENCE_image-edit-seedream.md)

## Qual dos dois usar
| Situação | Escolha |
|---|---|
| Colocar você numa cena com luz difícil (contraluz, neon, luz mista) | **Nano Banana 2** (`thinking_level=HIGH` raciocina sobre a luz) |
| Preservar textura de tecido, estampa, logo, detalhe fino de roupa | **Seedream** |
| Precisa de saída grande (3K/4K) direto | **Seedream** (`4096x4096`) ou NB2 em `4K` |
| Cena com muita oclusão (mão na frente do objeto, gente atrás) | **Nano Banana 2** |
| Quer variações rápidas do mesmo enquadramento | **Seedream** (`sequential_image_generation=auto`) |
| Não sei | Rode os dois. É 1 crédito cada e a diferença costuma ser óbvia |

## Pré-requisitos
- ComfyUI atualizado (`ByteDanceSeedreamNode` e `BatchImagesNode` são **core** — não instale nada).
- Estar **logado** em `platform.comfy.org` pela interface do ComfyUI, com créditos.
- Nenhuma GPU necessária.

## Setup
```bash
bash setup.sh
```
Confere que o servidor está no ar, que os 4 nós existem no `/object_info` e que o `.json` está no painel.

## Como usar (:8188)
1. Abra **`image-edit-seedream.json`**. Leia o nó **LEIA PRIMEIRO**.
2. **PROCESSO 1** já vem ativo; os outros 5 em bypass (roxo).
3. Suba `BASE` (= *the first image*) e `REF` (= *the second image*). A ordem no `Empilha as imagens`
   é o que define quem é quem no prompt.
4. **Escolha o `size_preset` com o mesmo formato da sua BASE** — senão ele reenquadra.
5. Edite o prompt (troque os `<DESCREVA AQUI ...>`) e **Run**.
6. Para rodar outro bloco: `Salvar` dele → **Ctrl+B**, e o anterior de volta para bypass.

### Os 6 processos
| # | Processo | BASE | REF | Obs |
|---|---|---|---|---|
| 1 | Trocar a roupa | a pessoa | a peça | REF opcional |
| 2 | Trocar objetos em cena | a cena | o objeto novo | preencha `<DESCREVA AQUI O OBJETO A SUBSTITUIR>` |
| 3 | Trocar a pessoa da foto | a cena | a pessoa nova | REF **obrigatória** |
| 4 | **Eu na foto** — roupa e pose **da cena** | a foto onde quero entrar | a **minha** foto | REF **obrigatória** |
| 5 | **Eu na foto** — **minha** roupa e **minha** pose | a cena de destino | minha foto **de corpo inteiro** | REF **obrigatória** |
| 6 | Trocar o local (+ match de luz) | a foto a manter | o novo local | REF opcional |

## Parâmetros não-óbvios
| Onde | Parâmetro | Nota |
|---|---|---|
| `ByteDanceSeedreamNode` | `model` | `seedream 5.0 lite` (mais novo, **14** referências, saída PNG) · `seedream-4-5-251128` (**10** refs — troque se o 5.0 alucinar detalhe de roupa) · `seedream-4-0-250828` (antigo) |
| | `size_preset` | ⚠️ **Piso de resolução:** no 4.5/5.0 a saída precisa de **≥ 3.686.400 px** (≈ 2560×1440). Preset menor → o nó **rejeita**. No 4.0 o piso é 921.600 px |
| | `width` / `height` | Só valem com `size_preset=Custom`. Teto de pixels: ~10,4 MP no 5.0, ~16,7 MP no 4.5/4.0 |
| | `sequential_image_generation` | `disabled` = 1 imagem. `auto` = o modelo pode gerar uma série (variações, cenas) |
| | `max_images` | Só vale com `auto`. Total (entrada + geradas) ≤ 15. **Cada imagem extra custa uma geração** |
| | `seed` | `randomize`. Gostou? Troque para `fixed` e anote o número |
| | `fail_on_partial` | `true` — aborta se faltar alguma imagem, em vez de devolver resultado parcial silenciosamente |
| `BatchImagesNode` | ordem dos slots | `image0` = *the first image*, `image1` = *the second image*… |

### Estilo de prompt
O Seedream foi treinado para **edição por frase única**. Os prompts deste bundle são uma frase longa
de propósito — evite picotá-los em lista de tópicos, a aderência cai.

A **cláusula de realismo** no fim de cada prompt (luz, sombra, lente, grão) é o que faz o resultado casar
com a foto original. **Não apague.**

## Validação (primeiro load)
1. Nenhum nó vermelho.
2. `Seedream` mostra os widgets nesta ordem: model · prompt · size_preset · width · height ·
   sequential_image_generation · max_images · seed · watermark · fail_on_partial.
3. Os 5 blocos em bypass estão roxos.
4. Teste barato: PROCESSO 1 com `2560x1440 (16:9)` (o menor preset que passa no piso do 4.5/5.0).

## Troubleshooting
| Sintoma | Causa provável | Correção |
|---|---|---|
| Nó vermelho `ByteDanceSeedreamNode` | ComfyUI antigo | Atualize o ComfyUI (o nó é core, `comfy_api_nodes/nodes_bytedance.py`) |
| Erro de resolução / o nó rejeita antes de chamar | `size_preset` abaixo do piso | Use ≥ `2560x1440 (16:9)` no 4.5/5.0 |
| "Insufficient credits" / erro de auth | Não logado ou sem saldo | Login em `platform.comfy.org` pela interface |
| Reenquadrou a foto | `size_preset` com formato diferente da BASE | Escolha o preset do mesmo formato (ou `Custom` com as dimensões da BASE) |
| Ele inventa detalhe na roupa | 5.0 lite alucinando | Troque `model` para `seedream-4-5-251128` |
| Rosto não parece comigo | Foto de REF ruim | Frontal, nítida, luz neutra. Corpo inteiro no processo 5 |
| Veio mais imagem do que pedi (e cobrou) | `sequential_image_generation=auto` | Volte para `disabled` e `max_images=1` |
| Borda de recorte / pele plástica | Cláusula de realismo apagada | Restaure o final do prompt |

Mais casos: `.agents/skills/task-debug-generation`.

## Referências
- Nós de API online: `.agents/skills/knowledge-comfyui-api-nodes`
- Técnica de edição: `.agents/skills/knowledge-image-editing`
- Templates oficiais de origem: `api_bytedance_seedream_5_0_lite_image_edit.json` e
  `template_eric_seedance_5_subject_and_outfit_combine.json` (em `comfyui_workflow_templates_media_image`)
