# Relighting — IC-Light

Reiluminar uma imagem: mudar a direção, cor ou intensidade da luz.

## IC-Light
`kijai/ComfyUI-IC-Light` (ou huchenlei native).

### Modos
- **`iclight_sd15_fc`** (foreground/por texto) — descreve a iluminação desejada.
- **`iclight_sd15_fbc`** (por background) — extrai iluminação de uma imagem de fundo.

## Técnica
`IC Light Apply Mask Grey` deixa a área mascarada cinza (neutra para o modelo).
Combine com `ImageCompositeMasked` + IPAdapter para fotografia de produto.

## Referências
- `docs/image-editing.md` §4
- IPAdapter → [controle e estilo](control-style.md)
