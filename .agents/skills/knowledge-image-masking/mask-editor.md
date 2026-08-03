# MaskEditor — Máscara Manual

## Quando usar
Precisa de controle total sobre a região a mascarar, sem depender de detecção automática.

## Como usar
Load Image → clique direito → **"Open in MaskEditor"** → pinte (roda ajusta o pincel) → **"Save to node"**.
Saídas `IMAGE` + `MASK`.

## Dicas
- Pinte um pouco além do objeto (margem para blend).
- Alpha apagado (GIMP/PS) também vira máscara ao carregar.
- Para máscaras complexas, combine com [segmentação por texto](text-segmentation.md) ou [detecção automática](auto-detection.md).

## Referências
- `docs/image-editing.md` §2
- Editar a região depois → `knowledge-image-editing`
