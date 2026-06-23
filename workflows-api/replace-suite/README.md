# replace-suite — Roupa + Fundo + Pose num arquivo só (rode UM por vez), por API

> Junta os 3 "replace" (**roupa**, **fundo**, **pose**) num único workflow, como **blocos independentes**.
> Você roda **um processo por vez** e encadeia manualmente (a saída de um vira a BASE do próximo). Em cada etapa
> você escolhe **TEXTO** (descreve) **ou** **FOTO de referência**. 2 IAs (Nano Banana Pro · Kontext Multi).

|  |  |
|---|---|
| 🎯 Faz | Troca roupa, fundo e pose — um processo por execução, no mesmo arquivo, com saída encadeada à mão |
| 🧠 Técnica | 3 blocos independentes de edição multi-referência; toggle TEXTO/FOTO por etapa (grupo em bypass) |
| 💳 Custo/billing | **fal credits** — 1 chamada por processo rodado |
| 🔌 Provedores/Nós | `NanoBananaPro_fal` · `FluxProKontextMulti_fal` (fal) · `ImageResizeKJ`/`ImageBatch` |
| 📥 Entrada | A foto (BASE) do bloco que for rodar; opcionalmente uma FOTO de referência (roupa/fundo/pose) |
| 📤 Saída | A foto editada do processo rodado (use-a como BASE do próximo) |
| 🧩 Modelos | Nano Banana Pro / Gemini 3 · Flux 1.1 Pro Kontext Max (multi) |
| 🧱 Requer | `ComfyUI-fal-API` + `FAL_KEY` · `ComfyUI-KJNodes`. Roda em 8GB (sem GPU) |
| 🟡 Status | Gerado a partir dos padrões known-good. Validar nós/chave/toggles no 1º load |

📇 **Card de API:** [`API_REFERENCE_replace-suite.md`](API_REFERENCE_replace-suite.md)

## Os arquivos
| Arquivo | IA | Quando |
|---|---|---|
| `00_LEIA-ME_comece_aqui` | — | Guia rápido |
| `10_modular_nanobanana` 🟢 | Nano Banana Pro | Melhor qualidade/relight. Toggle TEXTO/FOTO limpo (bypass). **Comece aqui** |
| `11_modular_kontext` 🟡 | Flux Pro Kontext Multi | `seed=0`; `image_2` = cópia da entrada (texto) ou arraste a REF (foto) |

## Como funciona (a parte não-óbvia)
São **3 blocos** empilhados (PROCESSO 1: ROUPA · 2: FUNDO · 3: POSE), cada um com **BASE** e **Salvar** próprios.
- **Ligar/desligar um bloco = o nó `Salvar`.** O PROCESSO 1 (ROUPA) vem **ATIVO**; FUNDO e POSE vêm em **bypass**.
  Para rodar outro: selecione o `Salvar` do bloco → **Ctrl+B** (ativa) e deixe os outros `Salvar` em bypass.
  (Bypassar o `Salvar` faz o bloco inteiro não executar — zero chamadas fal extras.)
- **TEXTO ou FOTO, por etapa (Nano):** o grupo **Referência** de cada bloco vem em **bypass** (= TEXTO: descreva no
  prompt). Para usar uma FOTO: selecione os 3 nós do grupo → **Ctrl+B** e suba a foto.
- **Kontext:** `image_2` vem ligada à BASE (= TEXTO). Para usar FOTO, arraste o `IMAGE` do nó REF para `image_2`.

```
PROCESSO 1 ROUPA  [BASE]→(Ref roupa: bypass=texto)→ Nano/Kontext → [Salvar ROUPA]   ← ATIVO
PROCESSO 2 FUNDO  [BASE]→(Ref fundo: bypass=texto)→ Nano/Kontext → [Salvar FUNDO]    ← bypass
PROCESSO 3 POSE   [BASE]→(Ref pose:  bypass=texto)→ Nano/Kontext → [Salvar POSE]     ← bypass
```

## Setup
```bash
export FAL_KEY=...
bash setup.sh
```
Instala `ComfyUI-fal-API` + `ComfyUI-KJNodes` (+ Manager) e baixa os 3 `.json`.

## Como usar (:8188) — encadeando os 3
1. Abra `10_modular_nanobanana`. Deixe ATIVO só **PROCESSO 1 (ROUPA)**. Suba a foto na BASE ROUPA, edite o prompt
   (ou ative a Referência + suba a peça). **Run** → salva a foto com a roupa nova.
2. Pegue essa saída e suba-a na **BASE FUNDO**. Ative o `Salvar FUNDO`, bypass o `Salvar ROUPA`. Edite/ative ref. **Run**.
3. Repita para **POSE** (BASE = saída do fundo). Resultado final = roupa + fundo + pose.

> Quer tudo numa run só, automático? Use **`workflows-api/replace-pipeline/`**.

## Parâmetros não-óbvios
| Onde | Parâmetro | Nota |
|---|---|---|
| Bloco | `Salvar` em bypass (mode 4) | bloco não executa; ative só o que vai rodar |
| Grupo Referência (Nano) | bypass (mode 4) | bypass = TEXTO; ativo = usa a FOTO |
| `FluxProKontextMulti_fal` | `seed=0` + `fixed` | **`seed>0` TRAVA**. `image_2` é obrigatória (cópia da BASE no texto) |
| `NanoBananaPro_fal` | `resolution` | itere em 1K/2K, finalize em 4K |
| Prompt por etapa | `<DESCREVA ...>` | troque o placeholder no modo TEXTO; no modo FOTO, cole o prompt de referência do card |

## Validação
- 0 nós vermelhos (Manager → Install Missing: fal-API, KJNodes).
- Só o PROCESSO 1 ativo por padrão → uma run = 1 chamada fal (roupa).
- Ativar PROCESSO 2 e bypassar o 1 → roda só o fundo. Etc.

## Troubleshooting
| Problema | Solução |
|---|---|
| Rodou 3 chamadas de uma vez | deixe ATIVO só 1 `Salvar`; os outros em bypass |
| Etapa ignorou a foto de referência | ative o grupo Referência (Ctrl+B); no Kontext, ligue a REF em `image_2` |
| Identidade mudou entre etapas | reforce "keep the exact same face/identity"; use a saída anterior como BASE |
| Kontext travado | `seed=0` + control `fixed` |

## Referências
- `knowledge-comfyui-api-nodes` (nós fal, seed gates, bypass de grupo). Blocos individuais: `replace-object`,
  `replace-environment`, `replace-pose`, `outfit-swap-api`.
- Versão automática (tudo numa run): `workflows-api/replace-pipeline/`.
