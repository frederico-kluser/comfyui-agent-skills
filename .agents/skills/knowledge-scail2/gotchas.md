# SCAIL-2 — Gotchas

Armadilhas e erros comuns ao rodar SCAIL-2.

## `WEIGHT NOT MERGED warning on patch_embedding`
**Inofensivo.** O ComfyUI monta um patch embedding de 36 canais e concatena os canais de máscara em runtime;
o peso armazenado de 20 canais é esperado. A geração segue normal.

## Nó core ausente
`Create SCAIL-2 Colored Mask` vermelho = ComfyUI não está nightly/master → `git pull` em `$COMFY` + reiniciar.

## Degradação em movimento complexo
Animation Mode pode **colapsar** em Replacement-Mode com inputs difíceis.
A qualidade degrada em movimento complexo.

## Ancoragem em vídeos longos
A ancoragem do frame de referência degrada em vídeos longos.

## Overhead
SCAIL-2 adiciona overhead de SAM 3.1 + CLIP Vision → é um pouco mais lento que Wan 2.1 puro.

## Referências
- `docs/SCAIL-2.md`
- Debug geral → `task-debug-generation`
