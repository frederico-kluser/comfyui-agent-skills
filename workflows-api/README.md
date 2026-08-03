# workflows-api — bundles que rodam por API online (sem GPU)

Três bundles, todos pagos com os **créditos do comfy.org**. **Zero custom node, zero chave de API:**
a autenticação é o **login em `platform.comfy.org`** pela própria interface do ComfyUI.

| Bundle | O que faz | Nó principal |
|---|---|---|
| [`image-edit-nano-banana-2`](image-edit-nano-banana-2/) | 6 edições de foto num arquivo só | `GeminiNanoBanana2` |
| [`image-edit-seedream`](image-edit-seedream/) | As **mesmas** 6 edições, no outro melhor editor | `ByteDanceSeedreamNode` |
| [`video-person-swap-seedance-2`](video-person-swap-seedance-2/) | Me colocar num vídeo no lugar de uma pessoa | `ByteDance2ReferenceNode` |

## Os 6 processos de imagem (iguais nos dois bundles de imagem)
| # | Processo | O que você sobe |
|---|---|---|
| 1 | Trocar a roupa | a foto + a peça |
| 2 | Trocar objetos em cena | a cena + o objeto novo |
| 3 | Trocar a pessoa da foto | a cena + a pessoa nova |
| 4 | **Eu na foto** — com a roupa e a pose **da cena** | a cena + a minha foto |
| 5 | **Eu na foto** — com a **minha** roupa e a **minha** pose | a cena + minha foto de corpo inteiro |
| 6 | Trocar o local (+ match de iluminação) | a foto + o novo local |

Cada bundle é **um arquivo** com os 6 processos como blocos independentes. Só o bloco ativo gasta
crédito; os outros vêm em **bypass** (Ctrl+B liga/desliga pelo nó `Salvar`).

## Por que dois modelos para a mesma coisa
Eles erram de formas diferentes. **Nano Banana 2** raciocina melhor sobre luz, perspectiva e oclusão
(`thinking_level=HIGH`); **Seedream** preserva melhor textura de tecido, estampa e detalhe fino, e sai
maior. Rodar os dois com a mesma entrada custa dois créditos e a diferença costuma ser óbvia.

## Começar
```bash
cd image-edit-nano-banana-2 && bash setup.sh
```
O `setup.sh` **não instala nada**: confere o servidor, verifica no `/object_info` que os nós existem, e
garante que o `.json` aparece no painel *Workflows* (criando o symlink `~/ComfyUI/user/default/workflows/api`
→ este diretório, se ainda não existir).

Depois: abra o workflow no `:8188` e **leia o nó "LEIA PRIMEIRO"** — ele fica no canto superior esquerdo
do grafo e explica os bypasses, a ordem das imagens e o que não apagar do prompt.

## Antes de gastar crédito
1. Esteja **logado** em `platform.comfy.org` (menu de usuário do ComfyUI) e confira o saldo.
2. Rascunhe barato: Nano Banana 2 em `1K`/`MINIMAL`, Seedance em `Seedance 2.0 Fast` `480p` `4s`.
3. Só um bloco ativo por `Run`.

## Convenções destes bundles
- **Prompts em inglês.** Os dois modelos seguem instrução em inglês com bem mais fidelidade. Onde houver
  `<DESCREVA AQUI ...>`, troque pelo seu texto.
- **A cláusula de realismo** no fim de cada prompt (luz, sombra, lente, grão) é o que faz o resultado casar
  com a foto original. Apagou, volta a parecer colagem.
- **A ordem das imagens é o contrato do prompt.** `image0` do `Empilha as imagens` é `Image 1`,
  `image1` é `Image 2`. Inverter inverte o sentido da instrução.
- **Status 🟡** em todos: o grafo foi validado estruturalmente (nós existem no `/object_info` ao vivo,
  assinatura de widgets bate com os templates oficiais), mas **não foi executado** — executar gastaria
  crédito. Valide no primeiro load.

## Ver também
- `.agents/skills/knowledge-comfyui-api-nodes` — as 3 rotas de billing (partner / fal / Replicate),
  catálogo de nós, seed gates, chaves.
- `.agents/skills/task-package-workflow-project` — como um bundle destes é montado.
- `.agents/skills/task-debug-generation` — quando algo falha.
