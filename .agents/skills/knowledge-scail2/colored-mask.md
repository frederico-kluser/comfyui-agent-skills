# SCAIL-2 — Máscara Colorida

Input crítico do SCAIL-2. Obrigatória **mesmo em Animation Mode single-character** — não a remova do workflow.

## Por que é obrigatória
Codifica quem é quem: cada cor mapeia uma região do personagem ao movimento condutor.

## Convenção de cor
- **Preto** = fundo não deve aparecer.
- **Branco** = fundo deve aparecer.
- **Cor** = correspondência entre região do personagem e movimento condutor.

## Geração
Nós SAM 3.1 (`SAM3_VideoTrack`) + `Create SCAIL-2 Colored Mask` (nó **core** do ComfyUI, não custom).

## Replacement Mode
`--replace_flag` + máscara da região a substituir.

## ⚠️ Nó vermelho
`Create SCAIL-2 Colored Mask` ausente = ComfyUI não está nightly/master → `git pull` + reiniciar.

## Referências
- `docs/SCAIL-2.md`
- Grafo nativo → `knowledge-scail2-native`
