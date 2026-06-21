# workflows-api/ — Bundles que rodam por **API online** (sem GPU pesada)

Projetos de workflow em que **a inferência acontece num provedor hospedado** (Veo, Kling, Nano Banana, Seedance,
Flux Pro…). O ComfyUI local só **orquestra**: monta o grafo, faz upload/download e compõe. Pensado para a máquina
de **8 GB de VRAM** — a regra do projeto é *"nada de GGUF/quantizado/inferior local"*, então a geração pesada vai
para a nuvem (modelo **melhor e mais rápido**), e a GPU local só faz máscara/composição/upscale ESRGAN.

> **`workflows-api/` vs [`workflows-cloud/`](../workflows-cloud/) — o eixo é QUEM roda a inferência:**
> - **`workflows-api/`** → um **provedor hospedado** roda o modelo; você paga **por chamada** (créditos). Sem alugar GPU.
> - **`workflows-cloud/`** → **você** roda o modelo numa **GPU alugada** (RunPod); paga por **segundo de GPU**. (SCAIL-2, Wan, SDXL, Qwen self-hosted.)

## As 3 rotas de nuvem (e onde mora a qualidade)
| Rota | Nós | Cobrança | Credencial |
|---|---|---|---|
| **Partner Nodes** (comfy.org) | `Kling*`, `FluxVTONode`, `GeminiNanoBanana2`, `FluxEraseNode`… (`partner/*`) | **Comfy credits** (free tier ~400 cr/mês) | **Login** em `platform.comfy.org` (sem arquivo de chave) |
| **fal.ai** | sufixo `*_fal` (`Veo31_fal`, `NanoBananaPro_fal`, `Seedance*_fal`, `FluxPro1Fill_fal`…) | **fal credits** | `FAL_KEY` |
| **Replicate** | `comfyui-replicate` | Replicate | `REPLICATE_API_TOKEN` |

> **Princípio:** *"fal vs Comfy não decide qualidade — o MODELO decide."* Os modelos de ponta (Veo 3.1, Nano Banana
> **Pro**/Gemini 3, Flux 1.1 Pro Ultra, Kontext Max) existem em mais de uma hospedeira; muitos nós **partner** expõem
> só versões antigas (`GeminiImageNode` = Gemini 2.5; `VeoVideoGenerationNode` = Veo 2) → a qualidade máxima costuma
> vir do **fal**. Detalhes, catálogo de nós e os **seed gates** (errar TRAVA o nó): **`knowledge-comfyui-api-nodes`**.

## Chaves & segredos (regra do projeto)
- Chaves do ComfyUI cloud → **`~/ComfyUI/secrets.env`** (`chmod 600`, gitignored), carregado pelo `run.sh`. **Nunca** em `~/.secrets` (esse é só dos agentes de código).
- `FAL_KEY` também pode ir em `~/ComfyUI/custom_nodes/ComfyUI-fal-API/config.ini` (`[API]`). Partner = **login**, sem chave.
- Os `setup.sh` deste folder **leem a chave do ambiente** e gravam o `config.ini` — **nunca** embutem segredo no repo.

## Bundles
| Bundle | O que faz | Provedores/Nós | Billing |
|---|---|---|---|
| [`commercial-ondokai/`](commercial-ondokai/) | Comercial de ~30s (9 cenas) com protagonista sintético consistente | Nano Banana Pro + Veo 3.1 + Kling + Seedance | fal + Comfy login |
| [`mask-edit-cloud/`](mask-edit-cloud/) | Edita uma região (máscara) na nuvem **ou** local e recola sem tocar o resto | `FluxPro1Fill_fal` + SAM/GroundingDINO local | fal **ou** local grátis |
| [`outfit-swap-api/`](outfit-swap-api/) | Troca a roupa/look mantendo pose, rosto e fundo | `FluxVTONode` (partner) · `NanoBananaPro_fal` | Comfy credits **ou** fal |

## Como usar
Cada bundle tem `setup.sh` + `README.md` (Card Informativo + pipeline) + `API_REFERENCE_*.md` (inputs/params por nó).
```bash
cd <bundle>/
export FAL_KEY=...        # do seu ~/ComfyUI/secrets.env; nunca commitado
bash setup.sh            # instala os custom nodes, grava o config.ini e baixa os .json
```
Procedimento ponta-a-ponta do comercial: **`task-create-commercial-api`**. Conhecimento dos nós: **`knowledge-comfyui-api-nodes`**.

## Gotchas (resumo — completo em `knowledge-comfyui-api-nodes`)
- Os nós `*_fal` **bloqueiam sem barra de progresso**; cold-start pode ficar minutos em `IN_QUEUE` e ainda completar.
- **Seed gates** divergem por nó: `FluxPro1Fill_fal` → `0` (`-1` trava); `Veo31_fal`/`NanoBananaPro_fal` → **sem seed** (trava por âncora).
- `NanoBananaEdit_fal` = Gemini 2.5 (fraco, "devolve a foto") ≠ `NanoBananaPro_fal` = Gemini 3.
- A cadeia `LoadVideoURL→CreateVideo` extrai **só frames** → perde o áudio nativo do Veo (baixe a URL original).
