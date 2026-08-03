# Composição/Replace em Python (Fora do ComfyUI)

Recolar uma região editada na imagem original via código, sem depender do grafo.

## Fórmula universal (alpha matte)
```
saída = original*(1−m) + editada*m
```
Feathering = transição invisível.

## Pillow (paste com máscara)
```python
result.paste(edited, (0,0), mask.filter(ImageFilter.GaussianBlur(10)))
```
Copie a original antes — `paste` é in-place.
Ou `Image.composite(edited, original, mask_blur)`.

## NumPy (alpha blend)
```python
m = mask / 255.0
m = m[..., None]  # broadcast para canais
out = orig * (1 - m) + edited * m
out = out.clip(0, 255)
```

## OpenCV seamlessClone (Poisson)
Casa gradientes, borda invisível. Pode **alterar cor/luz**.
```python
center = (x + w//2, y + h//2)  # centro do boundingRect(mask)
result = cv2.seamlessClone(src, dst, mask, center, cv2.NORMAL_CLONE)
```
- `NORMAL_CLONE` preserva textura; `MIXED_CLONE` para estruturas finas.
- O src deve caber no dst ao redor do center (senão erro -215).
- Guarde `if np.any(mask)` antes.

## Quando usar cada um
| Objetivo | Técnica |
|----------|---------|
| Fidelidade de pixels (cor original) | Alpha blend feathered (Pillow/NumPy) |
| Harmonizar cor/luz com entorno | seamlessClone (OpenCV) |
| Dentro do ComfyUI (sem código) | Inpaint Stitch / ImageCompositeMasked |

## Script pronto
`workflows-cloud/inpaint-region-cropstitch/scripts/compose.py` (alpha-blend e seamlessclone por flag).

## Referências
- `docs/image-editing.md` §3
- API HTTP → [http-api](http-api.md)
