#!/usr/bin/env python3
"""compose.py — recola uma região editada na imagem original (replace via código).

Dois métodos (ver knowledge-comfyui-api / docs/image-editing.md §3):
  alpha    : alpha blend com máscara borrada (feathering). FIDELIDADE de pixels — cor exata.
  seamless : OpenCV seamlessClone (Poisson). HARMONIZA cor/luz com o entorno (pode alterar a cor).

Fórmula do alpha: out = original*(1-m) + editada*m, com m em [0,1] e bordas borradas.

Uso:
  python compose.py --original orig.png --edited edited.png --mask mask.png --out out.png
  python compose.py -o orig.png -e edited.png -m mask.png --method seamless --clone mixed
Requisitos: pillow, numpy  (opencv-python só para --method seamless).
"""
import argparse, sys


def alpha_blend(original_p, edited_p, mask_p, out_p, feather):
    from PIL import Image, ImageFilter
    import numpy as np
    orig = Image.open(original_p).convert("RGB")
    edited = Image.open(edited_p).convert("RGB").resize(orig.size)
    mask = Image.open(mask_p).convert("L").resize(orig.size)
    if feather > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(radius=feather))
    o = np.asarray(orig, dtype=np.float64)
    e = np.asarray(edited, dtype=np.float64)
    m = (np.asarray(mask, dtype=np.float64) / 255.0)[..., None]  # (H,W,1) broadcast
    out = np.clip(o * (1.0 - m) + e * m, 0, 255).astype("uint8")
    Image.fromarray(out).save(out_p)


def seamless(original_p, edited_p, mask_p, out_p, clone):
    import cv2
    import numpy as np
    src = cv2.imread(edited_p)      # patch editado (BGR)
    dst = cv2.imread(original_p)    # destino (BGR)
    if src is None or dst is None:
        sys.exit("erro: não consegui ler --edited/--original")
    src = cv2.resize(src, (dst.shape[1], dst.shape[0]))
    mask = cv2.imread(mask_p, cv2.IMREAD_GRAYSCALE)
    mask = cv2.resize(mask, (dst.shape[1], dst.shape[0]))
    _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    if not np.any(mask):
        sys.exit("erro: máscara vazia")
    x, y, w, h = cv2.boundingRect(mask)
    center = (x + w // 2, y + h // 2)              # (x,y), não (linha,coluna)
    flag = cv2.MIXED_CLONE if clone == "mixed" else cv2.NORMAL_CLONE
    cv2.imwrite(out_p, cv2.seamlessClone(src, dst, mask, center, flag))


def main():
    ap = argparse.ArgumentParser(description="Recola uma região editada na original.")
    ap.add_argument("-o", "--original", required=True)
    ap.add_argument("-e", "--edited", required=True)
    ap.add_argument("-m", "--mask", required=True, help="L: 255=usa editada, 0=mantém original")
    ap.add_argument("--out", default="result.png")
    ap.add_argument("--method", choices=["alpha", "seamless"], default="alpha")
    ap.add_argument("--feather", type=float, default=10.0, help="raio do blur da máscara (alpha)")
    ap.add_argument("--clone", choices=["normal", "mixed"], default="normal", help="seamlessClone mode")
    a = ap.parse_args()
    if a.method == "alpha":
        alpha_blend(a.original, a.edited, a.mask, a.out, a.feather)
    else:
        seamless(a.original, a.edited, a.mask, a.out, a.clone)
    print(f"OK -> {a.out}  ({a.method})")


if __name__ == "__main__":
    main()
