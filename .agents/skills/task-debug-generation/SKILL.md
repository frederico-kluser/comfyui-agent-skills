---
name: task-debug-generation
description: >-
  Diagnóstico de falhas de geração no ComfyUI: OOM/CUDA out of memory, vídeo preto/cinza, ruído/snow entre runs,
  nós vermelhos (missing), dropdown de modelo vazio, incompatibilidade de tipos e servidor "Reconnecting". Use
  quando algo "deu erro", "não gera", "ficou preto", "estourou a memória", "travou" ou aparece nó vermelho —
  mesmo sem citar a skill. Apoia-se em knowledge-comfyui-workflows.
metadata:
  version: 0.1.0
  type: task
---
# Tarefa — Debugar uma Geração

Roteiro de diagnóstico. Sempre olhe primeiro o **terminal/console** onde o ComfyUI roda — é lá que aparece o
stack trace completo.

## Quando usar
"Deu erro / não gera / ficou preto / OOM / travou / nó vermelho / reconnecting / dropdown vazio".

## Sintoma → causa → correção
- **OOM / "CUDA out of memory"** (mais comum em vídeo): reduza **frames** antes da resolução (720p→480p);
  ative fp8/GGUF; **block swap** (`blocks_to_swap` 20→40); tiled VAE; `--lowvram`/`--novram`; offload do text
  encoder (`t5_cpu`); feche apps que usam GPU. Um job de vídeo por GPU. (Dynamic VRAM é default desde mar/2026.)
- **Vídeo/imagem preto ou cinza**: cfg errado p/ modelo destilado (Wan/Flux/SCAIL-2 usam **cfg≈1**; cfg 7+
  estoura) **ou** VAE incompatível/corrompido (carregue um VAE conhecido). Em Wan, **não** use `--use-sage-attention`
  global (→ preto/ruidoso) — use o node KJNodes `PatchSageAttentionKJ`.
- **Ruído/snow após a 1ª geração boa**: corrupção de VRAM entre runs (Wan 2.2 é o mais afetado) → reinicie o
  ComfyUI ou adicione um nó de limpeza (`easy cleanGpuUsed`) ao fim do workflow.
- **Nós vermelhos (missing)**: Manager → "Install Missing Custom Nodes", reinicie, atualize o navegador. Ainda
  vermelho = dependência Python faltando (veja o terminal; `pip install -r requirements.txt` no venv certo).
  **Exceção**: `Create SCAIL-2 Colored Mask` é **core** → ComfyUI não está nightly (`git pull` em `$COMFY`).
- **Dropdown de modelo vazio**: arquivo na pasta errada ou falta refresh/reiniciar. Confira `models/<subpasta>`.
- **Incompatibilidade de tipos**: link recusado = cor/tipo errado entre slots.
- **Servidor não sobe / "Reconnecting"**: porta 8188 ocupada (outra instância) ou erro de import na
  inicialização — mude a porta ou mate o processo; veja o terminal.
- **CUDA kernel image / Torch errado**: placas novas (RTX 50xx) exigem build do PyTorch com a CUDA certa (12.8).
- **GPU ~0% e geração 10min+**: caiu p/ CPU (VRAM insuficiente) → reduza quantização ou `--lowvram`.

## Ferramentas de debug
Preview Image / preview de vídeo em pontos intermediários; Preview Method = Latent2RGB (ver o KSampler ao vivo);
Preview Any (valores de tensor); Link Fixer (rgthree).

## Referências
- `knowledge-comfyui-workflows` (low-VRAM, cadeia de nós), `knowledge-scail2` (cfg/máscara/nightly),
  `docs/workflow-guide.md` §8, `docs/runpod-guide.md` §9.

## <evolution>
1. Resolveu? Só então persista.
2. Persista: um par sintoma→causa→fix **novo** ou não-óbvio, ou a combinação que destravou. Ignore o já listado.
3. Append em `LEARNINGS.md` (data + fonte). Destile no corpo se recorrente (`version++`). Nova classe de erro → `meta-evolution`.
4. Diff git para revisão.
