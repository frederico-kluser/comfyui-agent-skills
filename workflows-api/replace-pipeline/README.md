# replace-pipeline — Roupa + Fundo + Pose numa ÚNICA run, por API

> Encadeia as 3 edições: **BASE → ROUPA → FUNDO → POSE → Salvar**. Uma execução faz tudo (a saída de cada etapa
> entra na próxima). Em cada etapa você escolhe **TEXTO** (descreve) **ou** **FOTO de referência**. 2 IAs.

|  |  |
|---|---|
| 🎯 Faz | Troca roupa, fundo e pose de uma vez, encadeado, numa única run |
| 🧠 Técnica | Pipeline de 3 edições multi-referência em série; toggle TEXTO/FOTO por etapa |
| 💳 Custo/billing | **fal credits** — **3 chamadas por run** (uma por etapa) |
| 🔌 Provedores/Nós | `NanoBananaPro_fal` · `FluxProKontextMulti_fal` (fal) · `ImageResizeKJ`/`ImageBatch` |
| 📥 Entrada | A BASE (a pessoa/produto) + por etapa: prompt **ou** foto de referência (roupa/fundo/pose) |
| 📤 Saída | A imagem final com as 3 edições aplicadas |
| 🧩 Modelos | Nano Banana Pro / Gemini 3 · Flux 1.1 Pro Kontext Max (multi) |
| 🧱 Requer | `ComfyUI-fal-API` + `FAL_KEY` · `ComfyUI-KJNodes`. Roda em 8GB (sem GPU) |
| 🟡 Status | Gerado a partir dos padrões known-good. Validar nós/chave/toggles no 1º load |

📇 **Card de API:** [`API_REFERENCE_replace-pipeline.md`](API_REFERENCE_replace-pipeline.md)

## Os arquivos
| Arquivo | IA | Quando |
|---|---|---|
| `00_LEIA-ME_comece_aqui` | — | Guia rápido |
| `10_pipeline_nanobanana` 🟢 | Nano Banana Pro | Toggle TEXTO/FOTO por etapa (bypass). **Comece aqui** |
| `11_pipeline_kontext` 🟡 | Flux Pro Kontext Multi | `seed=0`; texto encadeado por `image_2`=duplicata; FOTO = arraste a REF |

## Como funciona
A BASE entra na ETAPA 1 (ROUPA); a saída vira a entrada da ETAPA 2 (FUNDO); a saída desta entra na ETAPA 3 (POSE);
o `Salvar` final tem o resultado das 3.
- **TEXTO ou FOTO por etapa (Nano):** cada etapa tem um grupo **Referência** em **bypass** (= TEXTO: descreva no
  prompt da etapa). Para usar FOTO: selecione os 3 nós do grupo → **Ctrl+B** e suba a foto.
- **Kontext:** `image_2` de cada etapa = duplicata da entrada (= TEXTO). Para FOTO numa etapa, arraste o `IMAGE` do
  nó REF daquela etapa para `image_2`.

```
[BASE] → ETAPA1 ROUPA(texto|foto) → ETAPA2 FUNDO(texto|foto) → ETAPA3 POSE(texto|foto) → [Salvar final]
```

## Setup
```bash
export FAL_KEY=...
bash setup.sh
```
Instala `ComfyUI-fal-API` + `ComfyUI-KJNodes` (+ Manager) e baixa os 3 `.json`.

## Como usar (:8188)
1. Abra `10_pipeline_nanobanana`. Suba a foto na **BASE**.
2. Para cada etapa: **edite o prompt** (troque `<DESCREVA ...>`) **ou** ative a Referência (Ctrl+B) e suba a foto.
3. **Run** → uma execução faz roupa → fundo → pose. Saída final no `Salvar`.

## Parâmetros não-óbvios
| Onde | Parâmetro | Nota |
|---|---|---|
| Grupo Referência (Nano) | bypass (mode 4) | bypass = TEXTO; ativo = usa a FOTO daquela etapa |
| `FluxProKontextMulti_fal` | `seed=0` + `fixed` | **`seed>0` TRAVA** (em **todas** as 3 etapas). `image_2` obrigatória |
| `NanoBananaPro_fal` | `resolution` | suba só na **última** etapa (POSE) pra economizar; itere as anteriores em 1K |
| Custo | 3 chamadas/run | rascunhe barato; mude uma etapa por vez e re-rode quando afinar |

## Validação
- 0 nós vermelhos (Manager → Install Missing: fal-API, KJNodes).
- Run padrão (sem subir referências) = 3 edições por texto encadeadas; a identidade deve persistir até o fim.
- Ativar a Referência de uma etapa e subir a foto → aquela etapa passa a usar a imagem.

## Troubleshooting
| Problema | Solução |
|---|---|
| Identidade derivou ao longo das 3 etapas | reforce "keep the exact same face/identity" em cada prompt; ou rode etapa-a-etapa em `replace-suite` |
| Caro/lento | itere em `replace-suite` (1 etapa por vez) e só monte o pipeline no final; resolução baixa até afinar |
| Kontext travado | `seed=0` + control `fixed` em todas as etapas |
| Quero pular uma etapa | dê bypass no modelo daquela etapa (a imagem passa adiante sem editar) |

## Referências
- `knowledge-comfyui-api-nodes` (nós fal, seed gates, encadeamento). Versão manual/controlada (1 etapa por run):
  `workflows-api/replace-suite/`. Blocos individuais: `replace-object`/`replace-environment`/`replace-pose`/`outfit-swap-api`.
