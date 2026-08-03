# API Online — Rotas, Billing e Credenciais

O ComfyUI vira um **front-end de orquestração**: o grafo chama um modelo que roda **na nuvem do provedor**, paga-se
**por chamada**.

## As 3 rotas

| Rota | Nós | Cobrança | Credencial |
|---|---|---|---|
| **Partner Nodes** (comfy.org) | `partner/*`: `Kling*`, `FluxVTONode`, `FluxEraseNode`, `GeminiNanoBanana2`, `OpenAIDalle3`, `Ideogram*`, `Recraft*`… | **Comfy credits** (free tier ~400 cr/mês) | **Login** `platform.comfy.org` (sem arquivo). Chave só com `--listen` |
| **fal.ai** (`ComfyUI-fal-API`, gokayfem) | sufixo **`*_fal`** | fal credits | `FAL_KEY` (env ou `custom_nodes/ComfyUI-fal-API/config.ini` `[API]`) |
| **Replicate** (`comfyui-replicate`) | nós Replicate | Replicate | `REPLICATE_API_TOKEN` (+ `import_schemas.py`) |

## Partner vs fal (2026-08-03)
A inferência antiga *"os modelos bons só estão no fal"* **caducou**. O comfy.org hoje serve a
**geração atual**: `GeminiNanoBanana2` (Gemini **3.1** Flash Image), `ByteDanceSeedreamNode` (Seedream **5.0**/4.5),
`ByteDance2ReferenceNode` (**Seedance 2.0**). **Sempre confira o `/object_info` ao vivo** — a lista muda a cada release.

## Chaves e segredos
- ComfyUI cloud → **`~/ComfyUI/secrets.env`** (`chmod 600`, gitignored), carregado pelo `run.sh`. **Nunca `~/.secrets`**.
- `FAL_KEY` (env ou `config.ini`), `REPLICATE_API_TOKEN`.
- Partner = **login**, sem chave (comfy.org **não tem BYOK** no core; workaround `holo-q/comfy-api-liberation`).
- `HF_TOKEN` para baixar os modelos **locais** de apoio (SAM/DINO/ESRGAN).

## Referências
- Decisão API vs GPU → [api-vs-selfhosted](api-vs-selfhosted.md)
- Bundles: `workflows-api/image-edit-nano-banana-2/` · `image-edit-seedream/` · `video-person-swap-seedance-2/`
