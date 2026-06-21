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
- Projetos de workflow: `workflows-api/<projeto>/` (rodam por API, sem GPU) e `workflows-cloud/<projeto>/` (self-hosted em GPU RunPod) — json + README + setup.sh; crie via `task-package-workflow-project`.
- Visão geral para humanos: `README.md` (raiz).

## Memória evolutiva
Skills de tarefa rodam o passo `<evolution>` ao concluir e atualizam `LEARNINGS.md`
(revisão humana via git diff). GC periódico: `meta-consolidation`. Conteúdo gerado por
LLM é rascunho até a curadoria humana (ETH Zurich, arXiv:2602.11988).
