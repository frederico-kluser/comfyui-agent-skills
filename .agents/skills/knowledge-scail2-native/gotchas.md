# SCAIL-2 Nativo — Gotchas e Por Que Importa

## `replacement_mode` é UM booleano
Percorre `SCAIL2ColoredMask` **e** `WanSCAILToVideo` — alterne os dois juntos.
Este workflow usa um Primitive único ligado nos dois.

## Máscara por texto, não pintada
Gerada por **texto** (SAM3), não pintada: troque o prompt do subgraph
("human" → "the man on the left", "dog"...) para mudar o alvo.
Encontra/rastreia todas as instâncias do conceito.

## 16 fps, não force_rate
SCAIL-2 roda a **16 fps** (`force_rate 16`) → interpole com RIFE ×2 para 32.
Não suba o force_rate.

## Nós core ausentes
`SCAIL2ColoredMask`/`WanSCAILToVideo` vermelhos = ComfyUI não está nightly.

## Comparação nativo vs wrapper
- **Nativo** (`workflows-cloud/scail2-native-3rdparty/`): toggle replacement_mode explícito, máscara SAM3 por texto integrada — mais direto para "trocar pessoa".
- **Wrapper Kijai** (`workflows-cloud/person-swap-scail2`): pose-control, cadeia WanVideoWrapper.

## Referências
- `workflows-cloud/scail2-native-3rdparty/`
- Modelo/VRAM → `knowledge-scail2`
- Máscara por texto → `knowledge-image-masking`
