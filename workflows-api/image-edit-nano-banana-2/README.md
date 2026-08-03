# image-edit-nano-banana-2 — 6 edições de foto com Nano Banana 2 (créditos comfy.org)

> **6 arquivos independentes, um por processo**: trocar roupa · trocar objeto em cena · trocar a pessoa ·
> **me colocar na foto com a roupa/pose da cena** · **me colocar na foto com a minha roupa/pose** ·
> trocar o local com match de iluminação. Roda **sem GPU**, pagando com os **créditos do comfy.org**.

|  |  |
|---|---|
| 🎯 Faz | Edita uma foto por instrução + imagem de referência: roupa, objeto, pessoa, cenário, e insere você na cena |
| 🧠 Técnica | Edição multi-referência em contexto (até 14 imagens), com cláusula de relight/compositing no prompt |
| 💳 Custo/billing | **Créditos comfy.org** — 1 chamada por execução |
| 🔌 Provedores/Nós | `GeminiNanoBanana2` (partner, `partner/image/Gemini`) · `BatchImagesNode` · `LoadImage` · `SaveImage` — **tudo core, zero custom node** |
| 📥 Entrada | A foto BASE + (quase sempre) uma foto de REFERÊNCIA |
| 📤 Saída | PNG editado em `output/edit/nb2_<processo>_*.png` |
| 🧩 Modelos | Nano Banana 2 · Gemini 3.1 Flash Image (Google Vertex) |
| 🧱 Requer | **Login** em `platform.comfy.org` (sem chave de API). Roda em máquina de 8 GB, sem GPU |
| 🟡 Status | Grafo gerado a partir dos templates oficiais do ComfyUI + `/object_info` ao vivo, e validado estruturalmente. **Ainda não executado** (gastaria crédito) — valide no primeiro load |

📇 **Card de API:** [`API_REFERENCE_image-edit-nano-banana-2.md`](API_REFERENCE_image-edit-nano-banana-2.md)
🔁 **Irmão:** [`../image-edit-seedream/`](../image-edit-seedream/) — os mesmos 6 processos no Seedream 5.0/4.5. Rode os dois e compare.

## Pré-requisitos
- ComfyUI atualizado (os nós partner `GeminiNanoBanana2`, `BatchImagesNode` são **core** — não instale nada).
- Estar **logado** em `platform.comfy.org` pela própria interface do ComfyUI, com créditos disponíveis.
- Nenhuma GPU necessária: a inferência roda no provedor.

## Setup
```bash
bash setup.sh
```
O script **não instala custom node** (não há nenhum). Ele confere que o servidor está no ar, que os 4 nós
existem no `/object_info` e que os `.json` estão visíveis no painel de workflows.

## Os 6 processos — um arquivo por técnica

Cada processo é um arquivo `.json` independente. Abra o que precisa e rode — sem bypass, sem alternar blocos.

| # | Arquivo | Processo | BASE | REF |
|---|---------|----------|------|-----|
| 1 | `image-edit-nano-banana-2_trocar-roupa.json` | Trocar a roupa | a pessoa | a peça (opcional) |
| 2 | `image-edit-nano-banana-2_trocar-objetos-em-cena.json` | Trocar objetos em cena | a cena | o objeto novo (opcional) |
| 3 | `image-edit-nano-banana-2_trocar-a-pessoa-da-foto.json` | Trocar a pessoa da foto | a cena | a pessoa nova (**obrigatória**) |
| 4 | `image-edit-nano-banana-2_me-colocar-na-foto-roupa-da-cena.json` | **Eu na foto** — roupa e pose **da cena** | a foto onde quero entrar | a **minha** foto (**obrigatória**) |
| 5 | `image-edit-nano-banana-2_me-colocar-na-foto-minha-roupa.json` | **Eu na foto** — **minha** roupa e **minha** pose | a cena de destino | minha foto **de corpo inteiro** (**obrigatória**) |
| 6 | `image-edit-nano-banana-2_trocar-o-local.json` | Trocar o local (+ match de luz) | a foto a manter | o novo local (opcional) |

## Como usar (:8188)
1. Abra o `.json` do processo desejado (painel *Workflows* → `api/`).
2. **Suba as imagens:** `BASE` = a foto que vai ser editada, `REF` = a foto de referência. A ordem importa: `BASE` é **Image 1** no prompt, `REF` é **Image 2**.
3. **Edite o prompt.** Onde houver `<DESCREVA AQUI ...>`, troque pelo seu texto.
4. **Run.** O resultado sai em `output/edit/`.

> **Encadear:** a saída de um processo vira a BASE do próximo. Ex.: rode o 5 (me colocar na cena) e
> depois o 1 (trocar a roupa) usando o resultado como BASE.

## Parâmetros não-óbvios
| Onde | Parâmetro | Nota |
|---|---|---|
| `GeminiNanoBanana2` | `thinking_level` | Vem **`HIGH`**. É o que resolve perspectiva, escala e sombra ao inserir alguém numa cena. `MINIMAL` é mais barato e rápido — só use em edição simples (trocar cor, apagar objeto) |
| | `resolution` | `2K` por padrão. `4K` usa o upscaler nativo do Gemini — deixe para a finalização |
| | `aspect_ratio` | `auto` mantém o formato da BASE. Mudar aqui **reenquadra** |
| | `seed` | `randomize`. Gostou de um resultado? Troque para `fixed` e anote o número — a repetição é *best effort*, não garantida |
| | `system_prompt` | Já vem reescrito para **fotorrealismo/compositing** (preserva poro, textura de tecido, grão). Não apague |
| `BatchImagesNode` | ordem dos slots | `image0` = Image 1, `image1` = Image 2… Inverter troca o sentido do prompt |
| | slots extras | Aceita até **14** imagens: ligue mais `LoadImage` no slot livre e cite `Image 3`, `Image 4`… no prompt |

### A cláusula de realismo
Todo prompt termina com o mesmo parágrafo que manda o modelo casar **direção da luz, temperatura de cor,
contraste, dureza da sombra, sombra de contato, luz rebatida, profundidade de campo, aberração e grão**.
É ele que faz o resultado parecer a mesma foto. **Se apagar, volta a parecer colagem.**

## Validação (o que olhar no primeiro load)
1. Nenhum nó **vermelho** (nó faltando). Se aparecer, o ComfyUI está desatualizado.
2. O nó `Nano Banana 2` mostra os widgets nesta ordem: prompt · model · seed · aspect_ratio · resolution ·
   response_modalities · thinking_level · system_prompt.
3. Faça um teste barato primeiro: `thinking_level=MINIMAL`, `resolution=1K`, no processo 1.

## Troubleshooting
| Sintoma | Causa provável | Correção |
|---|---|---|
| Nó vermelho `GeminiNanoBanana2` | ComfyUI antigo | Atualize o ComfyUI (o nó é core, vem em `comfy_api_nodes`) |
| "Insufficient credits" / erro de auth | Não logado ou sem crédito | Faça login em `platform.comfy.org` pela interface e confira o saldo |
| Ele devolve a foto quase igual | Prompt genérico ou `thinking_level=MINIMAL` | Ponha `HIGH` e seja específico ("replace X with Y", não "melhore") |
| Rosto não parece comigo | Foto de REF ruim | Use foto frontal, nítida, luz neutra, sem óculos escuros. Corpo inteiro no processo 5 |
| Resultado com borda de recorte / pele plástica | A cláusula de realismo foi apagada | Restaure o final do prompt e o `system_prompt` |
| Reenquadrou a imagem | `aspect_ratio` diferente de `auto` | Volte para `auto` |

Mais casos: `.agents/skills/task-debug-generation`.

## Referências
- Conhecimento dos nós de API online: `.agents/skills/knowledge-comfyui-api-nodes`
- Técnica de edição: `.agents/skills/knowledge-image-editing` · realce/relight: `knowledge-image-enhance`
- Template oficial de origem: `comfyui_workflow_templates_media_image/templates/api_google_nano_banana2_image_edit.json`
