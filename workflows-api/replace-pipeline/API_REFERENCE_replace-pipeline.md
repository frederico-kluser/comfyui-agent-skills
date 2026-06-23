# API Reference — replace-pipeline

3 etapas encadeadas (ROUPA → FUNDO → POSE) numa run. Mesmos nós dos `replace-*`. Detalhe por nó: ver
`replace-pose`/`replace-object`. Aqui ficam as **convenções de encadeamento**.

## Estrutura
- `LoadImage(BASE)` → ETAPA1 (modelo) → ETAPA2 (modelo) → ETAPA3 (modelo) → `SaveImage` final.
- A saída `IMAGE` de cada modelo é a entrada (upstream) do próximo.

## Nano (`NanoBananaPro_fal`) por etapa
- `Resize base` (ativo) normaliza o upstream; grupo **Referência** = `LoadImage(REF)` + `Resize ref` + `ImageBatch` em **mode 4 / bypass**.
- Bypass → `ImageBatch` repassa `image1` (o upstream normalizado) → **TEXTO**. Ativo → batch(upstream, REF) → **FOTO**.
- Sem seed (reprodutível por âncora).

## Kontext (`FluxProKontextMulti_fal`) por etapa
- `image_1` = upstream; `image_2` = upstream (duplicata → **TEXTO**). Para **FOTO**, ligue o `IMAGE` do `LoadImage(REF)` daquela etapa em `image_2`.
- **seed gate:** `seed=0` + `control_after_generate='fixed'` em **todas** as etapas. **`seed>0` TRAVA.**

## Saída de cada modelo
- IMAGE. Encadeada diretamente (Nano: via o `ImageBatch` da próxima etapa; Kontext: direto em `image_1`/`image_2`).

## Custo / billing
- **3 chamadas fal por run.** Itere barato (resolução baixa nas etapas iniciais; só a última em 4K). Para afinar uma
  etapa sem re-pagar as outras, use `replace-suite` (1 chamada por processo).

## Prompts por etapa
- Iguais aos de `replace-suite` (ROUPA/FUNDO/POSE — versões texto e referência). Ver `API_REFERENCE_replace-suite.md`.
