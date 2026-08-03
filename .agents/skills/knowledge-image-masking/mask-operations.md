# Operações de Máscara

Converter, crescer, borrar e combinar máscaras depois de obtê-las.

## Conversão
- `MASK to SEGS` / `SEGS to MASK` — converte entre representações.
- `ToBinaryMask` — threshold para máscara binária.
- `ImageColorToMask` — seleciona por cor (sem SAM).
- CLIPSeg (`CLIPSegDetectorProvider`) — por texto sem SAM.
- Depth/luminância → threshold.

## Transformação
- `Dilate Mask` — grow (expande a máscara).
- `Gaussian Blur Mask` — feathering (suaviza bordas).

## Colagem
- `SEGSPaste` — cola SEGS na imagem original.

## Referências
- `docs/image-editing.md` §2
- Aplicar máscara para editar → `knowledge-image-editing`
