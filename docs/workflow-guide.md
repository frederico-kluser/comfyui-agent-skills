# Guia Completo de Criação de Workflows no ComfyUI (Edição Junho/2026)

## TL;DR
- No ComfyUI, um **workflow é um grafo de nós** (node graph) que você constrói conectando saídas a entradas; ele é salvo em **JSON** em dois formatos distintos — o "workflow" completo (layout visual + lógica) e o "API/prompt" (só a lógica de execução, exportado via "Save (API Format)") — e fica embutido nos metadados das imagens/vídeos gerados, permitindo recarregar tudo arrastando o arquivo de volta ao canvas.
- Para 2026 o frontend foi reescrito (Vue / **Nodes 2.0**), ganhou **Subgraphs** (encapsular partes do workflow como um "super-nó" reutilizável e publicável), **Partial Execution** (rodar só um ramo), Mini Map, nova UI do Manager e **API/Partner Nodes** (chamar modelos pagos de nuvem como Kling, Veo, Seedance dentro do grafo).
- Para vídeo/comerciais (Wan 2.1/2.2 e SCAIL-2), domine o ecossistema do **Kijai ComfyUI-WanVideoWrapper** + **VideoHelperSuite** (VHS) + **Frame Interpolation (RIFE/FILM)**, use **Context Windows** para vídeos longos além do limite de ~81 frames, LoRAs de aceleração (Lightx2v 4 steps) e técnicas de baixa VRAM (block swap, fp8/GGUF, tiled VAE).

## Key Findings

1. **ComfyUI é um ambiente de programação visual procedural**: cada nó é uma operação (carregar modelo, codificar texto, amostrar, decodificar) e os "fios" carregam tipos de dados específicos (MODEL, CLIP, VAE, CONDITIONING, LATENT, IMAGE...). Você só conecta slots do mesmo tipo (mesma cor).
2. **O grafo é um DAG** (grafo acíclico dirigido) executado por dependência, com cache: o ComfyUI só re-executa os nós cujas entradas mudaram, economizando tempo.
3. **Dois JSONs**: o formato de UI (`nodes`, `links`, `groups`, `last_node_id`, `last_link_id`, `version`, formato LiteGraph) e o formato de API (dicionário plano `{ "id": { "class_type", "inputs } }`) usado pelo endpoint `/prompt`.
4. **Custom nodes** expandem tudo; instale-os pelo **ComfyUI-Manager** ("Install Missing Custom Nodes"). Para vídeo, os pacotes-chave são WanVideoWrapper, VideoHelperSuite, KJNodes, rgthree, GGUF, Frame-Interpolation, Impact-Pack e Custom-Scripts.
5. **Organização** é crucial em workflows grandes: Groups, Notes, Reroute, Get/Set (KJNodes/rgthree), bypass/mute, e os novos **Subgraphs**.
6. **Vídeo** tem particularidades fortes: lidar com batches de frames, interpolação, salvar mp4/webm, janelas de contexto, e gestão agressiva de memória.

## Details

### 1. Fundamentos do ComfyUI e a interface de 2026

**O que é.** A documentação oficial define o ComfyUI como "um ambiente para construir e executar workflows de conteúdo generativo", onde "um workflow é definido como uma coleção de objetos de programa chamados *nós* que estão conectados uns aos outros, formando uma rede" — também chamada de *grafo*. É simultaneamente um **node graph**, um **ambiente de programação visual** e um **framework procedural**, comparável ao paradigma de Nuke, Blender, Maya, Unreal e Max. Um workflow pode gerar qualquer mídia: imagem, vídeo, áudio, modelo 3D, modelo de IA, agente, etc.

**Conceitos centrais:**
- **Nodes (nós):** caixas que executam uma função. Têm um título, *inputs* (entradas, à esquerda), *outputs* (saídas, à direita) e *widgets* (campos editáveis: texto, números, dropdowns).
- **Slots e links/edges:** os pontos de conexão são *slots*; os fios entre eles são *links* (ou *edges*). Cada slot tem um **tipo** e uma **cor**; só se conecta entrada e saída do mesmo tipo.
- **Widgets:** valores configuráveis dentro do nó (ex.: `seed`, `steps`, `cfg`). Podem ser convertidos em *input* para receber valor de outro nó.
- **Queue Prompt / execução:** ao clicar em **Run/Queue** (ou `Ctrl+Enter`), o frontend serializa o grafo em JSON e o envia para o backend executar. A execução segue a ordem de dependências.
- **Cache:** o motor só re-executa nós cujas entradas mudaram; nós inalterados reaproveitam a saída em cache.

**A interface reescrita (2026).** A grande virada de 2026 é o **Nodes 2.0**: a documentação oficial explica que o sistema de nós migrou "de renderização Canvas LiteGraph.js para uma arquitetura baseada em Vue", desbloqueando "iteração mais rápida e interações mais ricas" (widgets dinâmicos, nós expansíveis). Está disponível em Desktop, portable e stable; é possível voltar ao renderizador legado pelo menu do logo ComfyUI → toggle "Nodes 2.0". O blog oficial confirma que estão "trabalhando diretamente com autores" de custom nodes (com menção explícita ao autor do rgthree) para garantir migração suave; uma **Linear Mode** está a caminho.

Outras novidades de interface (a partir do release 0.3.51, descrito no blog como "a maior atualização de frontend desde junho"):
- **Subgraphs** em releases estáveis (ver seção 5 e 10), com possibilidade de "desempacotar" (unpack) de volta em nós.
- **Nova UI do Manager** ("Manager Extension" na barra superior).
- **Mini Map** para navegação no canvas e um novo modo de navegação padrão.
- **Tabs com preview** e painel de atalhos.

**Templates oficiais.** Em `Workflow → Browse Workflow Templates` você acessa o **Workflow Templates** (pacote `comfyui-workflow-templates`), que reúne workflows nativamente suportados (imagem, vídeo, áudio, API) e checa automaticamente se faltam modelos, oferecendo download. Para criar do zero, dê **duplo-clique no canvas** (busca de nós), use o **menu de contexto** (botão direito → Add Node) ou **arraste a partir de um slot** e solte no vazio.

**Navegação e atalhos importantes** (oficiais; no macOS, `Ctrl` ≈ `Cmd`):
- Pan: segurar **Espaço** + mover o cursor (ou arrastar com o botão do meio); zoom com a roda do mouse.
- `Ctrl+Enter`: enfileira o grafo (Queue). `Ctrl+Shift+Enter`: enfileira como prioridade.
- `Ctrl+M`: mute/unmute dos nós selecionados. `Ctrl+B`: bypass.
- `Ctrl+G`: agrupar nós. `Alt+C`: colapsar/expandir.
- `Ctrl+C/Ctrl+V`: copiar/colar (com conexões via `Ctrl+Shift+V`).
- `Delete`/`Backspace`: apagar; `Ctrl+D`: carregar grafo padrão.
- `Ctrl+S`: salvar workflow; `Ctrl+O`: abrir; `Ctrl+Z`/`Ctrl+Y`: desfazer/refazer.
- `Q`: fila; `H`: histórico. Os atalhos são customizáveis em **Settings → Keybinding**.

### 2. Anatomia de um workflow básico (texto→imagem)

O workflow padrão de imagem tem estes nós, conectados em sequência:

1. **Load Checkpoint** — carrega o modelo. Um checkpoint do Stable Diffusion expõe três saídas: **MODEL** (o preditor de ruído / UNet no espaço latente), **CLIP** (codificador de texto) e **VAE** (autoencoder que converte entre pixel e latente).
2. **CLIP Text Encode (Prompt)** — dois nós: um **positivo** (o que você quer) e um **negativo** (o que evitar). Recebem **CLIP** e produzem **CONDITIONING**.
3. **Empty Latent Image** — cria o "canvas" de ruído no espaço latente; aqui você define **largura, altura e batch size** (quantas imagens por execução). Saída: **LATENT**.
4. **KSampler** — o coração da geração. Recebe **MODEL**, **CONDITIONING positivo**, **CONDITIONING negativo** e **LATENT**; executa a desnoising. Parâmetros: `seed`, `control_after_generate`, `steps`, `cfg`, `sampler_name`, `scheduler`, `denoise`. Saída: **LATENT**.
5. **VAE Decode** — recebe o **LATENT** do KSampler e o **VAE**; converte de volta para pixels. Saída: **IMAGE**.
6. **Save Image** / **Preview Image** — salva (em `ComfyUI/output`) ou só pré-visualiza a imagem.

**Fluxo de dados e cores dos slots.** O ComfyUI usa um sistema fortemente tipado. As cores oficiais (tema escuro padrão) dos slots são:

| Tipo | Cor (hex) | Para que serve |
|---|---|---|
| MODEL | `#B39DDB` (lilás) | UNet / preditor de ruído |
| CLIP | `#FFD500` (amarelo) | codificador de texto |
| VAE | `#FF6E6E` (vermelho) | encode/decode pixel↔latente |
| CONDITIONING | `#FFA931` (laranja) | embeddings de prompt |
| LATENT | `#FF9CF9` (rosa) | imagem no espaço latente |
| IMAGE | `#64B5F6` (azul) | tensor de pixels |
| MASK | `#81C784` (verde) | máscara |
| CONTROL_NET | `#6EE7B7` | modelo ControlNet |
| CLIP_VISION | `#A8DADC` | encoder visual |

Diagrama textual do fluxo:

```
[Load Checkpoint] ──MODEL──────────────► [KSampler] ──LATENT──► [VAE Decode] ──IMAGE──► [Save Image]
        │                                   ▲  ▲  ▲                  ▲
        ├──CLIP──► [CLIP Text Encode +] ──CONDITIONING──┘  │  │       │
        ├──CLIP──► [CLIP Text Encode −] ──CONDITIONING─────┘  │       │
        │                                                     │       │
        └──VAE────────────────────────────────────────────────┼───────┘
                          [Empty Latent Image] ──LATENT────────┘
```

**Execução e cache.** O motor monta um DAG a partir das conexões. Para cada nó, a função interna resolve as entradas: se a entrada é um link, busca o valor da saída em cache; se é um valor constante (widget), passa direto. Só re-executa nós com entradas alteradas — por isso mudar só o prompt não re-roda o Load Checkpoint.

### 3. O formato do arquivo de workflow (JSON)

**Dois formatos.** Esta é uma das distinções técnicas mais importantes:

- **Formato "workflow" (UI / LiteGraph):** o formato salvo e carregado na interface. Contém **metadados visuais** — posições (`pos`), tamanhos (`size`), cores, grupos — além da lógica. Estrutura de topo: `last_node_id`, `last_link_id`, `nodes[]`, `links[]`, `groups[]`, `config`, `state`, `version`. Cada nó tem `id`, `type`, `pos`, `size`, `flags`, `order`, `mode`, `inputs[]`, `outputs[]`, `properties`, `widgets_values`. Os links são listados explicitamente; cada input referencia um `link` por id, cada output lista os `links` que dele saem.
- **Formato "API / prompt":** exportado via **"Save (API Format)"** (ou "Export (API)"). É "despojado de metadados de UI e contém apenas as conexões lógicas e valores de widgets necessários para o backend processar o grafo". É um **dicionário plano** onde cada chave é o `id` do nó e o valor tem `class_type` e `inputs`. Conexões entre nós são representadas como `[node_id, output_index]`; valores escalares vão direto.

Exemplo (formato UI) de um nó KSampler real:
```json
{
  "id": 114,
  "type": "KSampler",
  "pos": [1346, -437],
  "size": {"0": 315, "1": 262},
  "flags": {},
  "order": 13,
  "mode": 0,
  "inputs": [
    {"name": "model", "type": "MODEL", "link": 249},
    {"name": "positive", "type": "CONDITIONING", "link": 250},
    {"name": "negative", "type": "CONDITIONING", "link": 251},
    {"name": "latent_image", "type": "LATENT", "link": 252}
  ],
  "outputs": [
    {"name": "LATENT", "type": "LATENT", "links": [253], "shape": 3, "slot_index": 0}
  ],
  "properties": {"Node name for S&R": "KSampler"},
  "widgets_values": [0, "fixed", 4, 1.4, "lcm", "simple", 1]
}
```
Note como `widgets_values` é uma **lista posicional** (seed, control_after_generate, steps, cfg, sampler_name, scheduler, denoise) — útil ao editar JSON à mão.

O mesmo nó no **formato API** vira algo como:
```json
"3": {
  "class_type": "KSampler",
  "inputs": {
    "seed": 0, "steps": 20, "cfg": 8.0,
    "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0,
    "model": ["4", 0], "positive": ["6", 0],
    "negative": ["7", 0], "latent_image": ["5", 0]
  }
}
```

**Metadados em PNG/vídeo.** "O workflow do ComfyUI é automaticamente salvo nos metadados de qualquer imagem gerada", então **arrastar um PNG gerado de volta ao canvas** (ou usar `Workflows → Open` / `Ctrl+O`) recarrega todo o grafo. O mesmo vale para vídeos: o VHS_VideoCombine tem a opção `save_metadata` que embute uma cópia do workflow no mp4/webm. **Cuidado:** muitas plataformas sociais e compressões **removem os metadados** — para arquivamento confiável, salve também o **JSON** (`Workflows → Export`), que é minúsculo e ideal para versionamento.

**Editar JSON à mão.** É possível, mas frágil. Atenção a vírgulas, à correspondência entre `link` (input) e `links` (output) e aos ids (`last_node_id`/`last_link_id`). Para ferramentas externas, o formato API é o que se modifica programaticamente (trocar prompt, seed, caminho de imagem).

**Relação com a API.** O ComfyUI expõe HTTP + WebSocket na porta 8188 por padrão. Para rodar workflows programaticamente:
1. Ative o **Dev mode** em Settings (aparece o botão "Save (API Format)").
2. Exporte o `workflow_api.json`.
3. Faça `POST /prompt` com `{ "prompt": <workflow_api>, "client_id": <uuid> }`.
4. Acompanhe via WebSocket `/ws?clientId=...` (mensagens `executing`, `progress`, `executed`, `execution_success`/`execution_error`).
5. Recupere resultados via `GET /history/{prompt_id}` e baixe arquivos via `GET /view?filename=...&type=output`.

Endpoints úteis: `/prompt`, `/history/{id}`, `/view`, `/upload/image`, `/queue`, `/interrupt`, `/object_info` (definições de nós). Observação importante: o que a UI chama de "workflow" é submetido no campo `prompt` — **não confunda** com o texto do CLIP. Um custom node de terceiros (SethRobinson/comfyui-workflow-to-api-converter-endpoint) adiciona `/workflow/convert` para converter o JSON completo no formato API server-side, contornando o fato de que o JSON de UI **não roda** direto no `/prompt`.

### 4. Tipos de nós e onde encontrá-los

**Categorias de nós nativos** (acessíveis pelo duplo-clique/busca ou menu de contexto): *loaders* (Load Checkpoint, Load VAE, Load LoRA, UNETLoader, DualCLIPLoader, CLIP Vision), *conditioning* (CLIP Text Encode, ControlNet Apply), *sampling* (KSampler, KSampler Advanced, samplers/guiders/sigmas customizados), *latent* (Empty Latent Image, VAE Encode/Decode, Latent Upscale), *image* (Load Image, Save Image, Upscale, blends), *mask*, e utilidades.

**Como adicionar nós:**
- **Duplo-clique** em área vazia → busca fuzzy.
- **Botão direito** → "Add Node" → navegar por categorias.
- **Arrastar de um slot** e soltar no vazio → lista de nós compatíveis com aquele tipo.

**Custom nodes** são extensões da comunidade. Instale-os via **ComfyUI-Manager** — pré-instalado no Desktop; é "uma extensão para instalar, remover, desabilitar e habilitar custom nodes". Acesse pela barra superior (nova UI) → **Custom Nodes Manager**: busque pelo nome, clique Install, reinicie e atualize o navegador. Há também "Install via Git URL". **Segurança:** a doc oficial alerta para instalar apenas de autores confiáveis, pois plugins maliciosos podem comprometer o sistema. Versões recentes do Manager (V3.38) migraram dados para caminho protegido e adicionaram suporte a `uv`.

**Repositórios populares (especialmente para vídeo/comerciais):**
- **kijai/ComfyUI-WanVideoWrapper** — wrapper para os modelos Wan (2.1/2.2) e derivados como SCAIL-2; o autor o descreve como "perpetuamente em progresso" e seu "sandbox pessoal". Suporta GGUF no próprio model loader e LoRAs de aceleração.
- **Kosinkadink/ComfyUI-VideoHelperSuite (VHS)** — entrada/saída de vídeo: `VHS_LoadVideo`, `VHS_VideoCombine`, `VHS_VideoInfo`, além de dezenas de utilitários de batch (Select/Split/Merge Images/Latents).
- **city96/ComfyUI-GGUF** — suporte a modelos quantizados GGUF (UnetLoaderGGUF, DualCLIPLoaderGGUF). Segundo o repositório/DeepWiki, reduz os requisitos de VRAM "em 2–8× mantendo a qualidade" (*"reducing VRAM requirements by 2-8x while maintaining quality"*), com a ressalva técnica do próprio README de que *"a quantização não era viável para modelos UNET normais (conv2d), [mas] modelos transformer/DiT como o flux parecem menos afetados pela quantização"* — coloque os `.gguf` em `models/unet`.
- **Fannovel16/ComfyUI-Frame-Interpolation** — interpolação de frames (RIFE VFI, FILM VFI, GIMM-VFI), categoria `ComfyUI-Frame-Interpolation/VFI`.
- **kijai/ComfyUI-KJNodes** — utilidades, incluindo nós **Set/Get** (variáveis globais para evitar fios cruzados) e helpers de imagem/máscara.
- **rgthree/rgthree-comfy** — qualidade de vida: Seed, Reroute melhorado, Context/Context Switch, **Fast Muter / Fast Groups Muter**, Any Switch, Power Lora Loader, barra de progresso, Link Fixer.
- **ltdrdata/ComfyUI-Impact-Pack** — detecção/refino (FaceDetailer, detectores, SAM), muito usado para retoque.
- **pythongosssss/ComfyUI-Custom-Scripts** — autocomplete de prompt, sugestões de LoRA, previews e utilidades de UI.

**Resolver "missing nodes".** Ao carregar um workflow alheio, nós ausentes aparecem em **vermelho**. Abra o ComfyUI-Manager → **"Install Missing Custom Nodes"**: ele detecta e oferece a instalação automática. Reinicie e atualize o navegador; cheque o log do terminal por erros de import (dependências Python faltando exigem `pip install -r requirements.txt` no venv correto). Nó vermelho = custom node faltando; dropdown de modelo vazio = arquivo de modelo ausente, pasta errada ou falta refresh.

### 5. Organização e boas práticas

Workflows de comerciais ficam grandes rápido. Ferramentas para manter legível:

- **Groups (grupos):** caixas coloridas que agrupam nós relacionados (`Ctrl+G`). Dê títulos ("01 - Modelos", "02 - Prompt", "03 - Sampler", "04 - Vídeo"). É possível mutar/bypassar um grupo inteiro (com rgthree, toggles no cabeçalho do grupo).
- **Note nodes:** notas de texto no canvas para documentar parâmetros e instruções.
- **Reroute:** nós de redirecionamento para organizar os "spaghetti"/"noodles" dos fios. Os reroutes do **rgthree** são multidirecionais e melhores que o nativo.
- **Get/Set nodes (KJNodes e rgthree):** atribuem a saída de um nó a uma **variável global** (Set) e a recuperam em outro lugar (Get), eliminando fios longos cruzando a tela. O KJNodes usa Set/Get por nome; clicar com o botão direito oferece "Show/Hide Connections". *Trade-off:* para iniciantes, fios visíveis são mais claros; Get/Set é melhor para workflows densos e reutilizáveis.
- **Bypass vs. Mute:** **Mute** (`Ctrl+M`) "para" o nó e tudo depois dele (o ramo não roda). **Bypass** (`Ctrl+B`) "pula" o nó, deixando os dados passarem sem processamento para os nós seguintes. Use Mute para desligar um ramo inteiro (ex.: upscale caro); Bypass para testar sem uma etapa específica.
- **Primitives:** nós que emitem valores primitivos (INT, FLOAT, STRING, BOOLEAN) e podem alimentar o mesmo valor para vários nós (ex.: uma só `seed` ou `width/height` compartilhada). Converta um widget em input e ligue um Primitive.
- **Cores e nomes:** botão direito → Color para colorir nós/grupos; renomeie nós (título) para refletir função.

**Subgraphs (recurso central de 2026).** O blog oficial os define assim: *"Um subgraph é um workflow ComfyUI padrão com entradas e saídas. Pense neles como super-nós customizados contendo seções inteiras de workflow."* Para criar: selecione nós/grupos/reroutes e "colapse" no toolbox de seleção; tudo é encapsulado num único nó-subgraph. Características: aparecem como um único "super nó"; suportam **aninhamento** (subgraphs dentro de subgraphs) com barra de navegação por níveis; podem ser clonados; e, a partir do **ComfyUI 0.3.63**, **publicados** na biblioteca de nós ("Node Library → Subgraph Blueprints") para reutilização como se fossem nós comuns. Dentro do subgraph, dois nós especiais — **"Inputs"** e **"Outputs"** — gerenciam os slots expostos; conectar um widget ao nó de input expõe aquele controle no nível do subgraph (sem precisar "entrar" nele). Requer frontend ≥ 1.24.3. Substituem os antigos "group nodes" (que serão convertidos automaticamente). *Atenção:* ainda há bugs reportados em 2026 (ex.: previews ao vivo dentro de subgraphs em certos modos, e interação de Power Lora Loader do rgthree dentro de subgraphs colapsados).

**Reprodutibilidade.** Um workflow compartilhado guarda **tipos de nós, conexões e parâmetros — mas NÃO** os arquivos de modelo, custom nodes ou caminhos locais. Para reuso a longo prazo, registre uma "ficha de reprodução": fonte/URL, data, custom nodes requeridos, versão do ComfyUI testada, modelos (checkpoint/LoRA/VAE com hash), e parâmetros-chave (seed, tamanho, sampler, steps, CFG). Nomeie arquivos com data e propósito (ex.: `20260615-comercial-wan22-i2v-v3.json`), não `final-final-2.json`.

### 6. Widgets, parâmetros e controle

- **seed + control_after_generate:** o widget `seed` define o ruído inicial; o `control_after_generate` define o que acontece **após** cada geração: `fixed` (mantém), `increment` (+1), `decrement` (−1) ou `randomize` (aleatório). Para reproduzir um resultado, use `fixed`; para variar em lote, `randomize`.
- **steps:** número de passos de desnoising (mais = potencialmente mais detalhe/tempo).
- **cfg:** quão fortemente o modelo segue o prompt. (Modelos destilados de vídeo como Wan+Lightx2v exigem **cfg = 1**.)
- **sampler_name / scheduler:** algoritmo de amostragem (euler, dpmpp, lcm...) e o cronograma de sigmas (normal, simple, karras...).
- **denoise:** intensidade de desnoising (1.0 para txt2img puro; <1.0 para img2img/refino).
- **Converter widget em input:** botão direito no nó → "Convert widget to input" (no Nodes 2.0, há um painel de parâmetros). Isso permite alimentar o valor a partir de um Primitive ou de nós de lógica/matemática/strings, habilitando automação (ex.: calcular `width` divisível por 32, gerar prompts dinâmicos, compartilhar uma seed entre samplers).

### 7. Workflows de vídeo (Wan 2.1/2.2 e SCAIL-2) — o foco para comerciais

#### Particularidades gerais
Vídeo no ComfyUI = processar **sequências de frames** como batches de IMAGE/LATENT. Em vez de "Empty Latent Image", usam-se nós que definem **largura, altura E número de frames** (length). A saída do sampler é decodificada em uma pilha de frames, que segue para:
- **VHS_LoadVideo** — carrega um vídeo e extrai frames; parâmetros úteis: `force_rate`, `frame_load_cap` (limite de frames), `skip_first_frames`, `select_every_nth`, `custom_width/height`. Ative **VHS Advanced Previews** (engrenagem ao lado do Queue) para preview que reflete `skip_first_frames`/`frame_load_cap` e economiza banda.
- **VHS_VideoCombine** — monta os frames num arquivo. Parâmetros: `frame_rate`, `loop_count`, `filename_prefix`, `format` (`video/mp4`, `video/webm`, `image/gif`), `crf` (qualidade; ~20 ≈ visualmente lossless; menor = melhor/maior arquivo), `pingpong`, `save_metadata` (embute o workflow no vídeo), `pix_fmt`.
- **Frame interpolation (RIFE/FILM/GIMM-VFI):** gera frames intermediários para suavizar/aumentar FPS. Padrão comum: gerar no FPS nativo do modelo e interpolar depois (ex.: RIFE VFI 2×–10×), ajustando o `frame_rate` do VideoCombine para o FPS interpolado.

#### O ecossistema WanVideoWrapper (Kijai) — cadeia de nós
A cadeia típica **texto→vídeo** no wrapper é:

```
WanVideoModelLoader ──model──► WanVideoSampler ──samples──► WanVideoDecode ──► VHS_VideoCombine
LoadWanVideoT5TextEncoder ─► WanVideoTextEncode ──text_embeds──► (Sampler)
WanVideoEmptyEmbeds ──image_embeds──► (Sampler)
WanVideoVAELoader ──vae──► (Decode)
```

Nós principais (nomes de exibição confirmados no código-fonte do repositório Kijai):
- **WanVideo Model Loader (`WanVideoModelLoader`):** carrega o transformer principal (de `models/diffusion_models`), inclusive GGUF; cria o "model patcher". Recebe block-swap, torch-compile e LoRAs.
- **WanVideo VAE Loader (`WanVideoVAELoader`):** carrega o Wan VAE (`models/vae`). Há também **WanVideoTinyVAELoader** para decode rápido.
- **LoadWanVideoT5TextEncoder / LoadWanVideoClipTextEncoder:** carregam o UMT5-XXL (`models/text_encoders`) e o CLIP. Você também pode usar o text encode e o clip vision nativos do ComfyUI com o wrapper.
- **WanVideo TextEncode (`WanVideoTextEncode`):** codifica prompts positivo+negativo. Descrição da fonte: "Codifica prompts de texto em embeddings. Para *prompt travel* rudimentar você pode inserir múltiplos prompts separados por '|', distribuídos igualmente ao longo do vídeo." Existe **WanVideoTextEncodeCached** (carrega e descarrega o T5 completamente, "sem deixar pegada de VRAM ou RAM").
- **WanVideo Empty Embeds (`WanVideoEmptyEmbeds`):** para T2V puro; cria embeds vazios com as dimensões/contagem de frames alvo. A Wiki confirma: "Você pode modificar o tamanho no nó WanVideo Empty Embeds para alterar o tamanho do vídeo."
- **WanVideo ImageToVideo Encode (`WanVideoImageToVideoEncode`):** o nó de I2V; codifica `start_image` (e `end_image` opcional) pela VAE, combinando CLIP-vision embeds. O número de frames tem **default 81** com passo de 4 — coerente com a doc oficial, que diz que o Wan gera "vídeos de até 81 frames (aproximadamente 5 segundos)" a "16 frames por segundo", e o código força `((num_frames-1)//4)*4+1`. Outros parâmetros notáveis: `noise_aug_strength` ("útil em I2V, onde algum ruído adiciona movimento e resultados mais nítidos"), `start_latent_strength`/`end_latent_strength` ("valores menores permitem mais movimento"), `tiled_vae` ("encoding VAE em tiles para reduzir memória").
- **WanVideo Sampler (`WanVideoSampler`):** núcleo da geração. Entradas: `model`, `image_embeds`, `text_embeds`, `shift`, `steps`, `cfg`, `seed`, `scheduler`, `riflex_freq_index`; opcionais incluem `context_options`, `cache_args`/`teacache_args`, `denoise_strength`, `samples` (para v2v). Há variantes **WanVideoSamplerv2** e o par **WanVideoSamplerSettings → WanVideoSamplerFromSettings**.
- **WanVideo Decode (`WanVideoDecode`):** decodifica os latentes em frames para o VideoCombine.

Para **I2V**, troque o `WanVideoEmptyEmbeds` pelo `WanVideoImageToVideoEncode` (alimentado pela VAE + **WanVideoClipVisionEncode** da imagem inicial, usando `clip_vision_h.safetensors`).

#### Vídeos longos: Context Windows
Modelos Wan/SCAIL-2 geram nativamente ~81 frames por passada. Para ir além, use o nó **WanVideo Context Options (`WanVideoContextOptions`)**, cuja saída conecta ao input `context_options` do Sampler. Ele divide o vídeo em **janelas de contexto sobrepostas** que são geradas e mescladas, permitindo "gerar vídeos mais longos do que o modelo e as restrições de memória normalmente permitiriam". Parâmetros: `context_schedule` (ex.: `uniform_standard`, `uniform_looped`, `static`), `context_frames` (tamanho da janela, ex.: 81), `context_stride` (ex.: 4), `context_overlap` (frames sobrepostos, ex.: 16), `freenoise` (embaralhar ruído, default True). Internamente, `delta = context_frames - context_overlap` e itera em janelas — o modelo só vê `context_frames` por vez, enquanto o total pode ser arbitrariamente longo. O README do Kijai demonstra: "Teste de janela de contexto: 1025 frames usando janela de 81 frames, com 16 de overlap. Com o modelo 1.3B T2V isso usou menos de 5GB de VRAM e levou 10 minutos numa 5090." *Atenção:* `context_options` é incompatível com o nó MultiTalk I2V (que já faz loop próprio).

Alternativa para SCAIL-2: o custom node **Brobert-in-aus/scail-auto-extend** ("SCAIL Auto Extend Sampler") automatiza chunking, ancoragem (5 primeiros frames presos aos 5 últimos do chunk anterior → 76 frames novos por extensão), color-matching e stitching em uma só fila, evitando o cálculo manual de frames.

#### LoRAs de aceleração e baixa VRAM
- **WanVideo Lora Select (`WanVideoLoraSelect`):** seleciona LoRA de `models/loras` com `strength`, encadeável (alimenta o input `lora` do Model Loader). Variantes: **WanVideoLoraSelectMulti**, **WanVideoSetLoRAs** ("aplica pesos de LoRA diretamente nas camadas lineares sem fazer merge").
- **Lightx2v / step-distill:** LoRAs que permitem **4 passos** sem CFG (cfg=1). Os configs de referência usam `infer_steps: 4` e `enable_cfg: false`; a documentação avisa que "enable_cfg deve ser false (equivalente a sample_guide_scale = 1), caso contrário o vídeo pode ficar completamente borrado". O **Wan 2.2** usa dois modelos (high-noise + low-noise), cada um com seu próprio LoRA 4-step — logo workflows 2.2 costumam ter **dois** Model Loaders + dois LoRA selects. Um padrão comunitário de dois samplers (ex.: 5 passos com CFG alto + 3 passos lightx2v) preserva mais movimento.
- **WanVideo BlockSwap (`WanVideoBlockSwap`):** descarrega blocos do transformer para a CPU, trazendo à GPU só durante o processamento. O parâmetro `blocks_to_swap` tem **default 20, mínimo 0 e máximo 40**; o tooltip do código-fonte é explícito: *"Number of transformer blocks to swap, the 14B model has 40, while the 1.3B model has 30 blocks"* (o modelo 14B tem 40 blocos; o 1.3B tem 30). Também há `offload_img_emb`, `offload_txt_emb` e `use_non_blocking`. Economiza ~10–15GB de VRAM ao custo de ~5–15% de velocidade.
- **WanVideo Torch Compile Settings (`WanVideoTorchCompileSettings`):** configura `torch.compile` (`backend` inductor, `mode`, `fullgraph`); o README adverte que versões recentes dependem menos de torch.compile e que há um pico de VRAM na primeira execução no Windows (limpável apagando o cache do Triton em `C:\Users\<user>\.triton`).
- Outras técnicas: **fp8 scaled** (huggingface.co/Kijai/WanVideo_comfy_fp8_scaled) e **GGUF** (city96) para caber em GPUs menores; **tiled VAE decode**; caches de atenção (TeaCache/MagCache). Garanta dimensões **divisíveis por 32** (ex.: 704×1280), e em SCAIL-2 lembre que ele roda a **16 fps** — gere a 16 e interpole (FILM/RIFE) em vez de subir o `force_rate`.

#### SCAIL-2 especificamente
SCAIL-2 (lançado ~13/jun/2026) é um modelo **baseado em Wan 2.1** especializado em **transferência de movimento** para pessoas/personagens. Diferente do Wan-Animate e do SCAIL-1, ele **não converte a entrada em representação intermediária** (stick figure/OpenPose): passa a imagem de referência e o vídeo-motor quase diretamente ao DiT, preservando profundidade, contato e movimento de múltiplas pessoas. Componentes do workflow oficial (Comfy-Org/SCAIL-2): diffusion model `wan2.1_14B_SCAIL_2_fp8_scaled.safetensors` (versões fp16/mxfp8/GGUF Q2–Q8 também), VAE `wan_2.1_vae.safetensors`, text encoder `umt5_xxl_fp8_e4m3fn_scaled.safetensors`, CLIP Vision `clip_vision_h.safetensors`, máscaras via **SAM 3.1** (`sam3.1_multiplex_fp16.safetensors`) e LoRAs Lightx2v (4-step) + DPO (corrige mãos/rostos). **A máscara é input crítico** mesmo no modo Animação de personagem único (codifica quem é quem por cor). Gera até 81 frames por passada; use Context Windows (Manual) ou o auto-extend para vídeos longos. Carregue o pacote GGUF da city96 se tiver pouca VRAM.

### 8. Depuração e erros comuns

**Como debugar.** Insira **Preview Image** (para imagens) ou previews de vídeo em pontos intermediários para ver a saída de cada etapa. Ative **Preview Method = Latent2RGB** (via Manager/Settings) para ver o KSampler trabalhando ao vivo. O nó **Preview Any** (nativo) exibe valores de tensores para depuração. O **Link Fixer** do rgthree identifica e conserta links quebrados. Sempre olhe o **terminal/console** onde o ComfyUI roda — é lá que aparecem os stack traces completos.

**Erros frequentes e soluções:**
- **OOM (out of memory) / "CUDA out of memory":** o erro mais comum, sobretudo em vídeo (modelos processam vários frames simultaneamente). Soluções: rodar com `--lowvram` (ou `--novram` em casos extremos), usar modelos **fp8/GGUF**, **block swap**, **tiled VAE**, reduzir resolução/nº de frames, fechar apps que usam GPU (Chrome com aceleração, Discord, OBS). A partir de março/2026, o ComfyUI tem **Dynamic VRAM** ativado por padrão, reduzindo muito os OOMs. Há flags como `--disable-smart-memory` e `--cache-none`.
- **Noise/snow (ruído) após a 1ª geração boa:** corrupção de VRAM entre runs em modelos de vídeo (Wan 2.2 é o mais afetado). Reinicie o ComfyUI ou adicione nós de limpeza de VRAM (ex.: `easy cleanGpuUsed`) ao fim do workflow.
- **Imagem/vídeo preto ou cinza:** VAE incompatível/corrompido, ou CFG errado para o modelo (modelos Flux/Wan destilados usam CFG baixo ~1; um CFG 7+ "estoura" a imagem). Carregue um VAE conhecido via Load VAE.
- **Nós vermelhos (missing nodes):** custom node não instalado → Manager → "Install Missing Custom Nodes". Se instalado mas ainda vermelho, é erro de import (dependência Python) — veja o terminal.
- **Dropdown de modelo vazio:** arquivo no diretório errado, ou falta clicar no refresh / reiniciar. Modelos vão em `ComfyUI/models/<subpasta>` (checkpoints, diffusion_models, vae, loras, text_encoders, clip_vision, unet...).
- **Incompatibilidade de tipos:** você só conecta slots da mesma cor/tipo; um link recusado quase sempre é tipo errado.
- **Servidor não inicia / "Reconnecting…":** porta 8188 ocupada (outra instância), ou erro de import na inicialização. Mude a porta ou mate o processo.
- **CUDA no kernel image / Torch errado:** placas novas (ex.: RTX 50xx) exigem build de PyTorch compatível com a CUDA correta.

### 9. Recursos para aprender e baixar workflows prontos

**Documentação e fontes oficiais (prioritárias):**
- **docs.comfy.org** — documentação oficial (conceitos, interface, tutoriais, changelog, specs do JSON).
- **blog.comfy.org** — anúncios (Subgraphs, Nodes 2.0, API/Partner Nodes).
- **github.com/comfyanonymous/ComfyUI** e **Comfy-Org/ComfyUI** — código e releases.
- **github.com/comfyanonymous/ComfyUI_examples** — exemplos oficiais (imagens com metadados embutidos).
- **Workflow Templates embutidos** (`Workflow → Browse Workflow Templates`) — o melhor ponto de partida, pois checam/baixam modelos.
- **comfy.org/workflows** — galeria de workflows da comunidade.

**Plataformas da comunidade:**
- **CivitAI** (filtro "Workflows") — enorme acervo; muitos workflows Wan 2.2 do Kijai.
- **comfyworkflows.com** — repositório dedicado, pesquisável por categorias/tags.
- **RunComfy** — catálogo curado, com explicações detalhadas (inclui workflows SCAIL-2, Wan 2.2 low VRAM, etc.) e ambiente em nuvem.
- **OpenArt** — *atenção:* a OpenArt anunciou o **encerramento (sunset) dos Workflows em 18 de janeiro de 2026**; exporte dados se ainda os usar.
- **Reddit r/comfyui** e **r/StableDiffusion** — compartilhamentos, suporte e novidades (no r/StableDiffusion dá para filtrar posts com workflow incluído).
- **GitHub dos custom nodes** — muitos têm pasta `example_workflows/` (o WanVideoWrapper, por exemplo).
- **ComfyUI Wiki** (comfyui-wiki.com) — tutoriais detalhados de Wan 2.1/2.2 e mais.

**Como estudar e adaptar workflows alheios:** arraste o JSON/PNG, resolva missing nodes (Manager), mapeie modelos (checkpoint/LoRA/VAE) para os seus arquivos locais, confira a base model dos LoRAs, e trave seed/parâmetros para reproduzir. Verifique sempre **a licença** — muitos embutem LoRAs/custom nodes com licença não-comercial, o que importa para comerciais (a maioria dos modelos Wan é Apache 2.0, com uso comercial permitido).

### 10. Recursos avançados de 2026

- **Subgraphs + publicação:** encapsular e publicar módulos reutilizáveis (ver seção 5). A partir do 0.3.63, "Subgraph Blueprints" na biblioteca de nós; edição de widgets do subgraph por um painel de parâmetros sem entrar nele.
- **Partial Execution:** o blog oficial explica: *"Quer testar apenas um ramo... Quando você clica em qualquer nó de saída no fim de um ramo e o ícone verde de play no selection-toolbox fica ativo, clique nele para rodar só aquele ramo!"* Ideal para iterar numa etapa sem rodar o workflow inteiro. O changelog confirma "suporte de backend para execução parcial de workflows, permitindo processamento eficiente de workflows multi-estágio".
- **Sistema de nós V3 / Nodes 2.0:** o **V3 schema** (`comfy_api`) é a nova API declarativa para custom nodes (classes IO, `define_schema`), com API pública versionada, isolamento de dependências e recursos como *price badges*, inputs dinâmicos e MultiType. O ComfyUI migrou várias categorias nativas para V3. Para autores: pinar `comfy_api>=0.0.3,<0.1.0`, versionar IDs de nó. Nodes 2.0 é a camada de **renderização** (Vue) sobre isso.
- **API / Partner Nodes (modelos pagos de nuvem):** nós nativos que chamam modelos proprietários via API — Kling, Google Veo, OpenAI/GPT-Image, RunwayML, Pika, Luma, Seedance, Nano Banana, Flux Pro, etc. Funcionam como clientes de API (autenticação, upload, polling). Cobrados em **créditos**: a página oficial de preços confirma *"All prices are in credits (211 credits = 1 USD)"* — por exemplo, um `sora-2` 1280×720 de 8 segundos custa ~168,8 créditos (≈ US$0,10 × 8 × 211). Pagamento direto ao Comfy Org, "mesmo preço da API original". Vantagens: misturar modelos de nuvem com pré/pós-processamento local; uma só conta de créditos; acesso a modelos de ponta sem hardware caro. São **opcionais** — o ComfyUI continua gratuito e open-source. Acesse via `Workflow → Browse Templates → Image API / Video API` ou pela categoria API Node na biblioteca.
- **Comfy Cloud:** versão hospedada oficial. Segundo o blog Comfy, as GPUs são "aproximadamente duas vezes mais rápidas que A100s" e têm "96GB de VRAM e 180GB de RAM" (RTX 6000 Pro Blackwell), com "todos os modelos do Comfy Cloud liberados para uso comercial". A API é compatível com a local (`/api/prompt`), há execução paralela de jobs, e um **tier grátis** anunciado oficialmente dá "400 créditos todo mês, completamente grátis" (basta logar com Google); cada workflow pode rodar até 60 minutos no tier grátis, com um job ativo por vez (30 min nos planos Standard e Creator).
- **Outras novidades do motor (changelog 2026):** execução paralela de nós (especialmente para chamadas de API), `--feature-flag` registry, OpenAPI para cloud, otimizações de memória para câmera WAN, melhorias de interpolação (RIFE/FILM), suporte a HunyuanVideo 1.5, e novos nós de áudio/3D.

## Recommendations

**Estágio 1 — Fundamentos (se ainda não fez):** Atualize o ComfyUI para a última versão estável e teste o **Nodes 2.0**. Recrie do zero o template txt→imagem para internalizar o fluxo MODEL/CLIP/VAE/CONDITIONING/LATENT/IMAGE. Memorize `Ctrl+Enter`, `Ctrl+B`, `Ctrl+M`, `Ctrl+G`. *Benchmark para avançar:* conseguir construir e depurar o grafo básico sem consultar.

**Estágio 2 — Higiene de workflow:** Instale **rgthree-comfy** e **KJNodes**; adote **Groups**, **Reroute/Get-Set** e **Fast Groups Muter**. Comece a encapsular blocos repetidos em **Subgraphs** e publique os que reutiliza (ex.: "carregador de modelos Wan", "saída de vídeo"). *Benchmark:* um workflow de comercial com >40 nós que outra pessoa consiga ler.

**Estágio 3 — Pipeline de vídeo para comerciais:** Padronize sobre **WanVideoWrapper + VHS + Frame-Interpolation**. Crie um workflow-mestre com grupos: (1) Loaders (com LoRA Lightx2v + block swap), (2) Prompt/Conditioning, (3) Sampler com **Context Options** para clipes longos, (4) Decode, (5) **RIFE/FILM** para suavizar, (6) **VHS_VideoCombine** em mp4 (crf ~20, `save_metadata` on). Use **Partial Execution** para iterar só no ramo do sampler. *Thresholds:* se bater OOM, ative block swap (suba `blocks_to_swap` de 20 em diante, até o máximo de 40 no 14B) → fp8 → GGUF → reduza frames/resolução (mantendo múltiplos de 32). Se o movimento ficar "duro", baixe `start_latent_strength` ou suba `noise_aug_strength`; se borrar com Lightx2v, confirme **cfg=1**.

**Estágio 4 — Versionamento e escala:** Salve **sempre** o JSON (não confie só nos metadados do mp4) com nomenclatura datada e uma ficha de reprodução (modelos + hashes + custom nodes + versão). Para entregar em volume, exporte em **"Save (API Format)"** e automatize via `/prompt` + WebSocket, ou use **Comfy Cloud**/Partner Nodes quando precisar de modelos de nuvem (Kling/Veo/Seedance) — verificando licença comercial e custo em créditos por geração.

**Quando reavaliar:** Se um custom node central (ex.: WanVideoWrapper, que é "perpetuamente WIP") quebrar após update, fixe a versão anterior via Manager e teste em cópia antes de migrar workflows de produção. Reavalie o pipeline a cada release maior de modelo (a cadência Wan/SCAIL é rápida).

## Caveats

- **Ritmo de mudança:** o frontend e os custom nodes mudam muito rápido em 2026. Nomes de nós, defaults e até a UI (Nodes 2.0 vs. legado) podem divergir do que você vê; o **código-fonte no GitHub** é a fonte autoritativa, e mirrors auto-gerados (comfyai.run, instasd) às vezes ficam defasados.
- **WanVideoWrapper é "sandbox" do autor:** o próprio Kijai descreve o pacote como perpetuamente em progresso e propenso a problemas; nem todo modelo novo é portado para o ComfyUI nativo.
- **Bugs conhecidos de Subgraphs (2026):** previews ao vivo dentro de subgraphs e certas interações (Power Lora Loader do rgthree) ainda apresentavam falhas reportadas; teste antes de depender deles em produção.
- **Metadados são frágeis:** redes sociais e compressão removem o workflow embutido em PNG/mp4 — sempre arquive o JSON.
- **Números de fornecedores:** os ganhos "20–24× mais rápido" e o regime de 4 passos do Lightx2v vêm dos cards/docs do próprio fornecedor (lightx2v), não de benchmarks independentes.
- **Licenças:** workflows e modelos da comunidade podem ter cláusulas não-comerciais; para comerciais, valide cada componente (modelos Wan 2.2 são Apache 2.0 / uso comercial permitido, mas LoRAs/custom nodes variam).
- **OpenArt Workflows encerra em 18/jan/2026** — não dependa dele como repositório de longo prazo.
- **API nodes custam dinheiro real** e podem ter versões de modelo mais antigas e menos controle que as plataformas nativas dos fornecedores.