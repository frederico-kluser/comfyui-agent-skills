# ComfyUI Commercials — RunPod Ops

Base de conhecimento e workflows para produzir vídeo IA (SCAIL-2, Wan 2.1/2.2, Flux) e
editar imagem (inpaint, Flux Fill/Kontext, Qwen-Image-Edit, SAM/máscara) no ComfyUI — por **APIs online**
(Veo 3.1, Kling, Nano Banana, Seedance; sem GPU) ou **self-hosted no RunPod.io**. Não há código de aplicação:
o valor está nos docs (`docs/`) e nas skills (`.agents/skills/`).

## Roteamento (faça primeiro)
Toda tarefa passa por `.agents/skills/project-router` ANTES de qualquer passo.
Catálogo de skills: `.agents/skills/catalog.md`.

## Comandos / fatos operacionais
- Provisionar pod: `bash .agents/skills/knowledge-runpod-provisioning/scripts/provisioning.sh`
  (ou env `PROVISIONING_SCRIPT=<raw_url>` no template AI-Dock/ComfyUI).
- ComfyUI roda na porta 8188; flag de inferência: `--fast` (GPUs ≥48GB: `--highvram`).
- SCAIL-2 exige ComfyUI nightly/master (o nó `Create SCAIL-2 Colored Mask` é core, não custom).
- Modelos vão em `ComfyUI/models/<subpasta>` no Network Volume (montado em `/workspace`).
- **Por API online** (sem GPU): nós fal (`*_fal`, lê `FAL_KEY`) + partner (login comfy.org). Chaves em `~/ComfyUI/secrets.env` (chmod 600), **nunca** `~/.secrets`. Bundles em `workflows-api/`; conhecimento: `knowledge-comfyui-api-nodes`.
- **Bundles atuais (2026-08-04): 8.** Partner/créditos comfy.org: `image-edit-nano-banana-2` · `image-edit-seedream` (6 edições de foto cada) · `video-person-swap-seedance-2`. **BYOK, zero comfy.org** (traz os próprios nós em `comfy_nodes/`, instalados por symlink pelo `setup.sh`): **`image-edit-pro-byok`** (4 motores de edição em dropdown, `FAL_KEY`) · **`video-seedance25-byok`** (Seedance 2.x + Wan Animate, `FAL_KEY`) · **`video-minimax-h3-byok`** (MiniMax H3 API v2, `MINIMAX_API_KEY`, gera áudio + clona timbre). Também em `FAL_KEY`: `video-person-replace`. Local/CPU: `foto-realismo-celular`.
- **Rosto errado em edição de foto? Cheque nesta ordem, ANTES de trocar de modelo:** (1) resolução da saída — `1K` com pessoa de corpo inteiro dá ~120px de rosto e nenhum modelo segura identidade nisso; (2) passe de degradação (grão/aberração/JPEG) rodando depois — destrói a microtextura de pele; (3) prompt mudando vários eixos de uma vez; (4) referência com rosto pequeno — o rosto deve ocupar **35–60% do quadro** da referência.
- **Todo pipeline de pessoa termina num PASSE FINAL** — é a etapa que mais rende e a mais esquecida. Foto: restauração de rosto (`fal-ai/codeformer`, **`fidelity` 0.7–0.9**; o default `0.5` troca traços). Vídeo: upscale (`fal-ai/seedvr/upscale/video` reconstrói detalhe, melhor em rosto; `fal-ai/topaz/upscale/video` p/ controle fino e fps). **Gere barato e amplie depois**; ordem: gerar → editar plano → upscale → áudio. Ambos consertam **acabamento, não identidade**.
- **Padrão BYOK do repo**: quando não existe nó instalável para o modelo, o bundle **traz o próprio pacote de nós** e o `setup.sh` faz symlink em `custom_nodes/`. Segredo sempre em `~/ComfyUI/secrets.env` (600); os nós leem do ambiente **e** do arquivo. Todo bundle BYOK tem um nó **"Testar Chave"** de custo zero.
- **Um nó custom PODE gastar os créditos do comfy.org** (não precisa ser nó core). Mecanismo, verificado em `execution.py:217`: declare `"hidden": {"auth_token": "AUTH_TOKEN_COMFY_ORG", "comfy_api_key": "API_KEY_COMFY_ORG"}` no `INPUT_TYPES` → o ComfyUI injeta o token da sessão → use `Authorization: Bearer <token>` (ou `X-API-KEY`) contra `https://api.comfy.org` (respeite `--comfy-api-base`). Upload de entrada: `POST /customers/storage` → `{upload_url, download_url}` → `PUT`. É assim que os bundles `image-edit-pro-byok` e `video-seedance25-byok` oferecem o seletor **`rota`** (chave própria × crédito comfy.org).
- ⚠️ **Ao trocar de rota, traduza os rótulos do prompt**: fal usa `@Image1`, partner comfy.org usa `Image 1`, Replicate usa `[Image1]`, MiniMax usa linguagem natural. Sem tradução a referência é ignorada **em silêncio**.
- **Regra de prefixo dos endpoints fal — é POR MODELO, não convenção:** Seedance **2.x não leva** `fal-ai/` (`bytedance/seedance-2.0/reference-to-video`); Seedance v1/v1.5 e Wan Animate **levam** (`fal-ai/wan/v2.2-14b/animate/replace`). Errar dá 404. Confira com `curl -s "https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=<id>"`.
- Antes de afirmar que um nó/modelo existe (ou não), **cheque o `/object_info` ao vivo** (`curl -s :8188/object_info`) — a lista partner muda a cada release.
- Exemplo known-good p/ adaptar um grafo: os **templates oficiais já instalados** em `…/site-packages/comfyui_workflow_templates_*/templates/`.

## Convenções não-óbvias
- SCAIL-2/Wan destilado (LightX2V): `cfg=1`, shift 1, euler/simple, 6–8 steps. `cfg>1` → vídeo borrado.
- Largura/altura divisíveis por 32 no SCAIL-2 (832×480 base 480p). Máx 81 frames por passada.
- Máscara colorida é obrigatória mesmo em Animation Mode single-character.
- Itere em 480p (barato), finalize em 720p. Pare o pod ao terminar (cobrança por segundo).

## Don't touch / segurança
- Nunca commitar nem expor tokens: `HF_TOKEN`, `CIVITAI_TOKEN`, `.env`, chaves de API.
- Nunca colocar tokens em template público do RunPod nem em scripts versionados.
- `docs/` são relatórios de pesquisa (a fonte). Edite conhecimento via skills, não duplique.

## Referências (carregue sob demanda)
- Catálogo de skills: `.agents/skills/catalog.md`
- Skills (fonte única): `.agents/skills/` (symlink: `.claude/skills/`)
- Projetos de workflow: `workflows-api/<projeto>/` (rodam por API, sem GPU) e `workflows-cloud/<projeto>/` (self-hosted em GPU RunPod — **sem bundle versionado hoje**) — json + README + `API_REFERENCE_*.md` + setup.sh; crie via `task-package-workflow-project`.
- Visão geral para humanos: `README.md` (raiz).

## Memória evolutiva
Skills de tarefa rodam o passo `<evolution>` ao concluir e atualizam `LEARNINGS.md`
(revisão humana via git diff). GC periódico: `meta-consolidation`. Conteúdo gerado por
LLM é rascunho até a curadoria humana (ETH Zurich, arXiv:2602.11988).
