# LEARNINGS — task-debug-generation

> Memória episódica desta tarefa. Append-only (data + fonte: usuário > inferência).
> `meta-consolidation` deduplica/promove/poda. Promova um par sintoma→causa→fix ao corpo quando recorrente.
> Revisão humana via git diff.

<!-- Formato:
## AAAA-MM-DD — <sintoma>
- **Contexto**: <modelo, GPU, workflow>
- **Sintoma → causa → fix**: <o que destravou, se não-óbvio>
- **Fonte**: usuário | inferência
- **Ação**: promover ao corpo? / nova classe de erro?
-->

## 2026-07-10 — Clicar num workflow no painel do ComfyUI não abre a tela (fica vazio)
- **Contexto**: bundle `workflows-api/text-to-music-api/` acessado via symlink `~/ComfyUI/user/default/workflows/api → repo/workflows-api`. Usuário: "clico nos itens de música, nenhum abre a tela".
- **Sintoma → causa → fix**: NÃO é o symlink (o `GET /userdata/workflows/<path>` lê o arquivo pelo symlink e devolve **200** — testei; o 404 que eu vi primeiro foi eu esquecer o prefixo `workflows/` no path). A causa real: **a pasta tinha um `.json` que NÃO era workflow** (`presets.json`, um arquivo de config). O painel *Workflows* do ComfyUI lista **todo `.json`** (`listUserDataFullInfo('workflows').filter(f => f.path.endsWith('.json'))`) e, ao clicar, chama `getDataFromJSON` → tenta carregar como grafo → sem `nodes` → **canvas vazio**. Com vários arquivos não-workflow na pasta (script/README/setup), a impressão é "nada funciona". **Fix**: nunca deixe `.json` não-workflow numa pasta exposta ao ComfyUI — config vira **`.mjs`/`.js`** (o frontend só abre `.json`; `.md/.sh/.mjs` são filtrados e não aparecem na sidebar). Validei o workflow real contra o `/object_info` ao vivo (0 problemas) antes de culpar o arquivo.
- **Fonte**: usuário (reportou) + inferência (source maps do `comfyui_frontend_package` + teste `/userdata` + `/object_info`).
- **Ação**: promover — regra reusável p/ `task-package-workflow-project` (bundle-API script-primeiro: só o workflow como `.json`; presets/config em `.mjs`). Classe de erro nova: "workflow não abre / abre vazio" (frontend, não geração).
